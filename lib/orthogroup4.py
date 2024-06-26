import pandas as pd
import os


class Group:
    def __init__(self, config_par):
        self.query_blast = config_par['group']['query_blast']
        self.ref_blast = config_par['group']['ref_blast']
        self.query_ref_collinearity = config_par['group']['query_ref_collinearity']
        self.output = config_par['group']['output']
        self.use_blast = config_par['group']['use_blast_pair']
        if self.use_blast in {"0", "FALSE", "False", "false"}:
            self.query_pair_file_dir = config_par['group']['query_pair_file_dir']
            self.query_pair_file_prefix = config_par['group']['query_pair_file_prefix']
            self.ref_pair_file_dir = config_par['group']['ref_pair_file_dir']
            self.ref_pair_file_prefix = config_par['group']['ref_pair_file_prefix']

    @staticmethod
    def split_conf(conf):
        new_conf = []
        split_lt = conf.split(",")
        for ele in split_lt:
            if len(ele) == 0:
                continue
            new_conf.append(ele.strip())
        return new_conf

    # get query_ref pair as element in a list and a dict query_tab_ref : bitscore
    @staticmethod
    def read_blast_get_bs(blast):
        blt_idt_lt = {}
        mapping_list = []
        with open(blast) as blt:
            for line in blt:
                rd_lt = line.split('\t')
                if rd_lt[0] == rd_lt[1]:
                    continue
                if rd_lt[0] + '\t' + rd_lt[1] not in blt_idt_lt:
                    blt_idt_lt[rd_lt[0] + '\t' + rd_lt[1]] = float(rd_lt[11])
                if [rd_lt[0], rd_lt[1]] not in mapping_list and [rd_lt[1],  rd_lt[0]] not in mapping_list:
                    mapping_list.append([rd_lt[0], rd_lt[1]])
        return blt_idt_lt, mapping_list

    @staticmethod
    def read_pair_get_map(pair_file):
        mapping_list = []
        for file in pair_file:
            with open(file) as f:
                _ = next(f)
                for line in f:
                    lt = line.split()
                    mapping_list.append([lt[0], lt[2]])
        return mapping_list

    def get_ref_list(self, collinearity):
        query_ref_collinearity_list = self.split_conf(collinearity)
        ref_list = []
        for col in query_ref_collinearity_list:
            df_col = pd.read_csv(col, sep='\t', comment="#", index_col=None, header=0)
            df_column = df_col['refGene'].tolist()
            ref_list.extend(df_column)
        return ref_list

    @staticmethod
    def align_collinearity(collinearity):
        df_col = pd.read_csv(collinearity, sep='\t', comment="#", index_col=None, header=0)
        df = df_col.iloc[:, [0, 5]]
        query_list = []
        # query is maize , ref is sorghum dict query:ref
        query_ref = df.set_index('queryGene')['refGene'].to_dict()
        # key is ref, value is list
        ref_query_dict = {}
        for query in query_ref:
            assert query not in query_list
            query_list.append(query)
            if query_ref[query] not in ref_query_dict:
                ref_query_dict[query_ref[query]] = [query]
            else:
                ref_query_dict[query_ref[query]].append(query)
        return ref_query_dict, query_ref, query_list

    @staticmethod
    def query_group(mapping_list, ref_query_dict, query_ref, blt_lt, query_list):
        pre_df = []
        for query_lt in ref_query_dict.values():
            for query in query_lt:
                for pr in mapping_list:
                    if query in pr and pr[1-pr.index(query)] not in query_list:
                        pre_df.append([query_ref[query], query, pr[1-pr.index(query)]])
        df = pd.DataFrame(pre_df)
        # print(df)
        # df = df.drop_duplicates()
        df[0] = df[0].astype('str')
        df[1] = df[1].astype('str')
        df[2] = df[2].astype('str')
        duplicated_df = df[df.duplicated(subset=df.columns[2], keep=False)].copy()
        duplicated_df.sort_values(by=df.columns[2], inplace=True)
        duplicated_df.reset_index(drop=True, inplace=True)
        dupl_list = []
        for key, group in duplicated_df.groupby(by=df.columns[2]):
            score = []
            sub_group_list = []
            for sub_key, sub_group in group.groupby(by=df.columns[0]):
                # sub_key is oryza gene
                sub_group_list.append(sub_group)
            if len(sub_group_list) == 1:
                continue
            # to compute repeat gene bitscore

            else:
                for grp in sub_group_list:
                    grp = grp.iloc[:, [1, 2]]
                    to_bs_lt = grp.values.tolist()
                    grp_score_lt = []
                    for lt in to_bs_lt:
                        if lt[0] + '\t' + lt[1] in blt_lt and lt[1] + '\t' + lt[0] in blt_lt:
                            pr_bs = (blt_lt[lt[0] + '\t' + lt[1]] + blt_lt[lt[1] + '\t' + lt[0]]) / 2
                        elif lt[0] + '\t' + lt[1] in blt_lt:
                            pr_bs = blt_lt[lt[0] + '\t' + lt[1]]
                        else:
                            pr_bs = blt_lt[lt[1] + '\t' + lt[0]]
                        grp_score_lt.append(pr_bs)
                    average = sum(grp_score_lt) / len(grp_score_lt)
                    i = 1
                    while i <= len(grp_score_lt):
                        score.append(average)
                        i += 1
            group["score"] = score
            group.sort_values(by=group.columns[3], ascending=False)
            ft_lt = group.iloc[0, 0:3].tolist()
            dupl_list.append(ft_lt)
        df.drop_duplicates(subset=df.columns[2], keep=False, inplace=True)
        dup_df = pd.DataFrame(dupl_list)
        df = pd.concat([df, dup_df])
        for row in df.itertuples(index=False, name=None):
            ref_query_dict[row[0]].append(row[2])
        # group number determine and mazie gene has been phased
        return ref_query_dict

    @staticmethod
    def ref_group(ref_list, ref_mapping_list, ref_blt_lt, ref_query_dict):
        pre_ref_df = []
        for ref in ref_list:
            for pr in ref_mapping_list:
                if ref in pr and pr[1 - pr.index(ref)] not in ref_list:
                    pre_ref_df.append([ref, pr[1 - pr.index(ref)]])
        ref_df = pd.DataFrame(pre_ref_df)
        ref_df[0] = ref_df[0].astype('str')
        ref_df[1] = ref_df[1].astype('str')

        duplicated_df = ref_df[ref_df.duplicated(subset=ref_df.columns[1], keep=False)].copy()
        duplicated_df.sort_values(by=ref_df.columns[1], inplace=True)
        duplicated_df.reset_index(drop=True, inplace=True)
        dupl_list = []
        for key, group in duplicated_df.groupby(by=ref_df.columns[1]):
            score = []
            to_bs_lt = group.values.tolist()
            for lt in to_bs_lt:
                if lt[0] + '\t' + lt[1] in ref_blt_lt and lt[1] + '\t' + lt[0] in ref_blt_lt:
                    pr_bs = (ref_blt_lt[lt[0] + '\t' + lt[1]] + ref_blt_lt[lt[1] + '\t' + lt[0]]) / 2
                elif lt[0] + '\t' + lt[1] in ref_blt_lt:
                    pr_bs = ref_blt_lt[lt[0] + '\t' + lt[1]]
                else:
                    pr_bs = ref_blt_lt[lt[1] + '\t' + lt[0]]
                score.append(pr_bs)
            group["score"] = score
            group.sort_values(by=group.columns[2], ascending=False)
            ft_lt = group.iloc[0, 0:2].tolist()
            dupl_list.append(ft_lt)
        ref_df.drop_duplicates(subset=ref_df.columns[1], keep=False, inplace=True)
        ref_dup_df = pd.DataFrame(dupl_list)
        ref_df = pd.concat([ref_df, ref_dup_df])
        for row in ref_df.itertuples(index=False, name=None):
            ref_query_dict[row[0]].append(row[1])
        return ref_query_dict

    @staticmethod
    def write_out(output, ref_query_dict):
        output = open(output, "w")
        idx = 0
        for ref in ref_query_dict:
            group_number = str(idx).zfill(7)
            merged_str = "\t".join(ref_query_dict[ref])
            output.write("OG" + group_number + "\t" + merged_str + "\t" + str(ref) + "\n")
            idx += 1
        output.close()

    def run(self):
        if self.use_blast in {"1", "TRUE", "True", "true"}:
            query_blast_list = self.split_conf(self.query_blast)
            query_ref_collinearity_list = self.split_conf(self.query_ref_collinearity)
            output_ref_query_dict = {}
            ref_list = self.get_ref_list(self.query_ref_collinearity)
            ref_blt_lt, ref_mapping_list = self.read_blast_get_bs(self.ref_blast)
            for i in range(len(query_blast_list)):
                blt_lt, mapping_list = self.read_blast_get_bs(query_blast_list[i])
                ref_query_dict, query_ref, query_list = self.align_collinearity(query_ref_collinearity_list[i])
                ref_query_dict = self.query_group(mapping_list, ref_query_dict, query_ref, blt_lt, query_list)
                for key, value in ref_query_dict.items():
                    if key in output_ref_query_dict:
                        output_ref_query_dict[key].extend(value)
                    else:
                        output_ref_query_dict[key] = value.copy()
            ref_query_dict = self.ref_group(ref_list, ref_mapping_list, ref_blt_lt, output_ref_query_dict)
            self.write_out(self.output, ref_query_dict)

        if self.use_blast in {"0", "FALSE", "False", "false"}:
            # maize sorghum
            query_pair_file_prefix_list = self.split_conf(self.query_pair_file_prefix)
            query_blast_list = self.split_conf(self.query_blast)
            query_ref_collinearity_list = self.split_conf(self.query_ref_collinearity)

            ref_list = self.get_ref_list(self.query_ref_collinearity)
            output_ref_query_dict = {}
            ref_pair_file_path = []
            suffix = [".wgd.pairs", ".tandem.pairs", ".proximal.pairs", ".transposed.pairs", ".dispersed.pairs"]
            for suf in suffix:
                ref_pair_file_path.append(os.path.join(self.ref_pair_file_dir, self.ref_pair_file_prefix + suf))
            for i in range(len(query_pair_file_prefix_list)):
                query_pair_file_path = []
                for suf in suffix:
                    query_pair_file_path.append(os.path.join(self.query_pair_file_dir, query_pair_file_prefix_list[i] + suf))

                blt_lt, _ = self.read_blast_get_bs(query_blast_list[i])
                mapping_list = self.read_pair_get_map(query_pair_file_path)

                ref_query_dict, query_ref, query_list = self.align_collinearity(query_ref_collinearity_list[i])
                ref_query_dict = self.query_group(mapping_list, ref_query_dict, query_ref, blt_lt, query_list)
                for key, value in ref_query_dict.items():
                    if key in output_ref_query_dict:
                        output_ref_query_dict[key].extend(value)
                    else:
                        output_ref_query_dict[key] = value.copy()
            ref_blt_lt, _ = self.read_blast_get_bs(self.ref_blast)
            ref_mapping_list = self.read_pair_get_map(ref_pair_file_path)
            ref_query_dict = self.ref_group(ref_list, ref_mapping_list, ref_blt_lt, output_ref_query_dict)
            self.write_out(self.output, ref_query_dict)
