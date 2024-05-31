import configparser
import argparse
from pathlib import Path
import os
from lib import pre_collinearity, collinearity, dotplot, prepare_ks, ks, blockinfo, ks_peaks, peaksfit, ksfigure, \
     classification_gene, orthogroup3, number_gn_visualization


base_dir = Path(__file__).resolve().parent


def run_pre_coll():
    global base_dir
    config_par = configparser.ConfigParser()
    config_par.read(os.path.join(base_dir, "config_file/pre_collinearity.conf"))
    config_soft = configparser.ConfigParser()
    config_soft.read(os.path.join(base_dir, 'config_file/software_path.ini'))
    pre_collinearity.Prepare(config_par, config_soft).run_all_process()


def run_coll():
    global base_dir
    config_par = configparser.ConfigParser()
    config_par.read(os.path.join(base_dir, 'config_file/collinearity.conf'))
    config_soft = configparser.ConfigParser()
    config_soft.read(os.path.join(base_dir, 'config_file/software_path.ini'))
    collinearity.Collinearity(config_par, config_soft).run()


def run_dotplot():
    global base_dir
    config_par = configparser.ConfigParser()
    config_par.read(os.path.join(base_dir, 'config_file/dotplot.conf'))
    dotplot.Dotplot(config_par).run()


def run_prepare_ks():
    global base_dir
    config_par = configparser.ConfigParser()
    config_par.read(os.path.join(base_dir, 'config_file/ks.conf'))
    config_soft = configparser.ConfigParser()
    config_soft.read(os.path.join(base_dir, 'config_file/software_path.ini'))
    prepare_ks.Prepare(config_par, config_soft).run()


def run_ks():
    global base_dir
    config_par = configparser.ConfigParser()
    config_par.read(os.path.join(base_dir, 'config_file/ks.conf'))
    config_soft = configparser.ConfigParser()
    config_soft.read(os.path.join(base_dir, 'config_file/software_path.ini'))
    ks.Ks(config_par, config_soft).sub_run()


def run_block_info():
    global base_dir
    config_par = configparser.ConfigParser()
    config_par.read(os.path.join(base_dir, 'config_file/block_info.conf'))
    blockinfo.BlockInfo(config_par).run()


def run_ks_pdf():
    global base_dir
    config_par = configparser.ConfigParser()
    config_par.read(os.path.join(base_dir, 'config_file/ks_peaks.conf'))
    ks_peaks.KsPeaks(config_par).run()


def run_pdf_fit():
    global base_dir
    config_par = configparser.ConfigParser()
    config_par.read(os.path.join(base_dir, 'config_file/peaks_fit.conf'))
    peaksfit.PeaksFit(config_par).run()


def run_ks_figure():
    global base_dir
    config_par = configparser.ConfigParser()
    config_par.read(os.path.join(base_dir, 'config_file/ks_figure.conf'))
    ksfigure.KsFigure(config_par).run()


# def run_pre_classification():
#     config_par = configparser.ConfigParser()
#     config_par.read('./config_file/classification.conf')
#     pre_classification.PreClassification(config_par).run()


# def run_classification():
#     config_par = configparser.ConfigParser()
#     config_par.read('./config_file/classification.conf')
#     classification.Classification(config_par).run()


def run_class_gene():
    global base_dir
    config_par = configparser.ConfigParser()
    config_par.read(os.path.join(base_dir, 'config_file/classification_gene.conf'))
    if int(config_par["classification"]["type"]) == 1:
        classification_gene.ClassGeneUnique(config_par).run()
    else:
        classification_gene.ClassGene(config_par).run()


# def run_group():
#     global base_dir
#     config_par = configparser.ConfigParser()
#     config_par.read(os.path.join(base_dir, 'config_file/orthogroup.conf'))
#     orthogroup.Group(config_par).run()


# def run_group2():
#     global base_dir
#     config_par = configparser.ConfigParser()
#     config_par.read(os.path.join(base_dir, 'config_file/orthogroup2.conf'))
#     orthogroup2.Group(config_par).run()


def run_group3():
    global base_dir
    config_par = configparser.ConfigParser()
    config_par.read(os.path.join(base_dir, 'config_file/orthogroup3.conf'))
    orthogroup3.Group(config_par).run()


def run_clv():
    global base_dir
    config_par = configparser.ConfigParser()
    config_par.read(os.path.join(base_dir, 'config_file/class_gene_number_visualization.conf'))
    number_gn_visualization.ClsVis(config_par).run()
# def run_class_gene_2():
#     config_par = configparser.ConfigParser()
#     config_par.read('./config_file/classification_gene_2.conf')
#     if int(config_par["classification"]["type"]) == 1:
#         classification_gene_2.ClassGeneUnique(config_par).run()
#     else:
#         classification_gene_2.ClassGene(config_par).run()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='collinearity gene analysis', prog="quotaAnchor")
    parser.add_argument('-v', '--version', action='version', version='%(prog)s 0.0.1_053024_beta')
    subparsers1 = parser.add_subparsers(title='gene collinearity analysis', dest='analysis')

    # get the longest protein and AnchorWave pro input file
    parser_sub1 = subparsers1.add_parser('pre_col', help='get longest protein and AnchorWave pro(collinearity) input file')
    parser_sub1.set_defaults(func=run_pre_coll)
    # produce collinearity file
    parser_sub1 = subparsers1.add_parser('col', help='get gene collinearity file by AnchorWave pro command')
    parser_sub1.set_defaults(func=run_coll)
    # collinearity dotplot or blast dotplot
    parser_sub1 = subparsers1.add_parser('dotplot', help='collinearity dotplot or blast dotplot')
    parser_sub1.set_defaults(func=run_dotplot)
    # prepare data for synonymous mutation and non-synonymous mutation(longest cds)
    parser_sub1 = subparsers1.add_parser('pre_ks', help='get longest cds')
    parser_sub1.set_defaults(func=run_prepare_ks)
    # synonymous mutation and non-synonymous mutation
    parser_sub1 = subparsers1.add_parser('ks', help='get ks and ka information')
    parser_sub1.set_defaults(func=run_ks)
    # summary block information
    parser_sub1 = subparsers1.add_parser('block_info', help='summary block information')
    parser_sub1.set_defaults(func=run_block_info)
    # ks probability density function curve
    parser_sub1 = subparsers1.add_parser('kp', help='ks(total, average, median) probability density function curve')
    parser_sub1.set_defaults(func=run_ks_pdf)
    # ks probability density function curve fitting
    parser_sub1 = subparsers1.add_parser('pf', help='ks probability density function curve fitting')
    parser_sub1.set_defaults(func=run_pdf_fit)
    # ks probability density function curve fitting
    parser_sub1 = subparsers1.add_parser('kf', help='ks distribution figure')
    parser_sub1.set_defaults(func=run_ks_figure)
    # #
    # parser_sub1 = subparsers1.add_parser('get_chr_info', help='assumed ancestor file')
    # parser_sub1.set_defaults(func=run_pre_classification)
    # # get ancestor chr 1 chr_total_gene_number class
    # parser_sub1 = subparsers1.add_parser('class', help='relative classification')
    # parser_sub1.set_defaults(func=run_classification)
    # class gene
    parser_sub1 = subparsers1.add_parser('class_gene', help='class gene as tandem, proximal, transposed, wgd/segmental, dispersed, singletons')
    parser_sub1.set_defaults(func=run_class_gene)
    # parser_sub1 = subparsers1.add_parser('group', help='orthogroup based collinearity')
    # parser_sub1.set_defaults(func=run_group)
    # parser_sub1 = subparsers1.add_parser('group2', help='orthogroup based collinearity')
    # parser_sub1.set_defaults(func=run_group2)
    parser_sub1 = subparsers1.add_parser('group3', help='orthogroup based collinearity')
    parser_sub1.set_defaults(func=run_group3)
    parser_sub1 = subparsers1.add_parser('clv', help='class gene number visualization')
    parser_sub1.set_defaults(func=run_clv)
#    parser_sub1 = subparsers1.add_parser('class_gene_2', help='class gene as tandem, proximal, transposed, wgd/segmental, dispersed, singletons')
#    parser_sub1.set_defaults(func=run_class_gene_2)

    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func()
    else:
        parser.print_help()
