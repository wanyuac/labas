#!/usr/bin/env python3

"""
This is the master script of software rasti. It implements three sub-commands 'detect', 'call_alleles', and 'aln2mut'.
Dependencies: BLAST+, Python 3, BioPython, pandas, cd-hit

Copyright (C) 2023-2024 Yu Wan <wanyuac@gmail.com>
Licensed under the GNU General Public Licence version 3 (GPLv3) <https://www.gnu.org/licenses/>.
Creation: 18 Dec 2023; the latest update: 16 Apr 2024.
"""

from argparse import ArgumentParser
from utility.detect import detect
from utility.call_alleles import call_alleles
from utility.aln2mut import aln2mut

def parse_arguments():
    parser = ArgumentParser(description = "Targeted gene detection for assemblies")
    subparsers = parser.add_subparsers(title = "Sub-commands of rasti", dest = "subcommand")

    # Sub-command 'detect'
    detect_parser = subparsers.add_parser(name = 'detect', help = "Detect target nucleotide sequences in genome/metagenome assemblies")
    detect_parser.add_argument('--queries', '-q', dest = 'queries', type = str, required = True, help = "Mandatory input: a multi-FASTA file of query DNA sequences. For coding sequences, add CDS to the beginning of sequence annotations \
                               and separated from other annotations with a \'|\' character in this FASTA file. For example, \'>seq CDS|other annotations\'")
    detect_parser.add_argument('--assemblies', '-a', nargs = '+', dest = "assemblies", type = str, required = True, help = "Mandatory input: FASTA files of genome/metagenome assemblies against which queries will be searched")
    detect_parser.add_argument('--assembly_suffix', '-s', dest = 'assembly_suffix', type = str, required = False, default = 'fna', help = "Filename extension (fasta/fna/fa, etc) to be removed from assembly filenames in order to get a sample name (default: fna)")
    detect_parser.add_argument('--outdir', '-o', dest = 'outdir', type = str, required = False, default = 'output', help = "Output directory (default: output)")
    detect_parser.add_argument('--min_identity', '-mi', dest = 'min_identity', type = float, default= 90.0, required = False, help = "Minimum percent nucleotide identity for BLAST to identify a match (default: 90.0; range: 70-100)")
    detect_parser.add_argument('--min_qcov', '-mq', dest = 'min_qcov', type = float, default = 90.0, required = False, help = "Minimum percent query coverage for BLAST to identify a match (default: 90.0; range: 0-100)")
    detect_parser.add_argument('--max_evalue', '-me', dest = 'max_evalue', type = str, default = '1e-5', required = False, help = "Maximum E-value for BLAST to identify a match (default: 1e-5)")
    detect_parser.add_argument('--max_match_num', '-mh', dest = 'max_match_num', type = int, default = 5, required = False, help = "Maximum number of matches reported by BLAST for each query sequence (default: 5; Range: 1-500)")
    detect_parser.add_argument('--pause', '-p', dest = 'pause', type = float, default = 0.2, required = False, help = "Number of seconds to hold between consecutive BLAST searches (default: 0.2; range: 0-60)")
    detect_parser.add_argument('--reload', '-r', dest = 'reload', action = 'store_true', help = "Flag this option to enable importing existing BLAST outputs without reruning the BLAST search (Option --pause is disabled in this case)")
    detect_parser.add_argument('--cd_hit_est', '-c', dest = 'cd_hit_est', type = str, default = 'cd-hit-est', required = False, help = "Full path of program cd-hit-est (default: cd-hit-est)")
    detect_parser.add_argument('--threads', '-t', dest = "threads", type = str, default = '1', required = False, help = "Number of threads (default: 1)")

    # Sub-command 'call_alleles'
    caller_parser = subparsers.add_parser(name = 'call_alleles', help = "Call alleles from results of \'rasti detect\', namely, BLAST search and sequence clustering")
    caller_parser.add_argument('--compiled_hit_table', '-t', dest = 'compiled_hit_table', type = str, required = True, help = "Input: compiled hits in the outputs of sub-command 'detect'")
    caller_parser.add_argument('--sample_list', '-s', dest = 'sample_list', type = str, required = True, help = "Input: a test file listing names of sample. It can be \'sample_list.txt\' in the output directory of \'rasti detect\'.")
    caller_parser.add_argument('--queries', '-q', dest = 'queries', type = str, required = True, help = "Mandatory input: a multi-FASTA file of query DNA sequences used for the \'detect\' method")
    caller_parser.add_argument('--representatives_dir', '-r', dest = 'representatives_dir', type = str, required = True,\
                               help = "Input: directory of input FASTA files of representatives allele sequences (*_representatives.fna).")
    caller_parser.add_argument('--outdir', '-o', dest = 'outdir', type = str, required = False, default = 'output/5_alleles', help = "Output directory (default: output/5_alleles)")

    # Sub-command 'aln2mut'
    aln2mut_parser = subparsers.add_parser(name = 'aln2mut', help = "Identify mutations from a FASTA-format sequence alignment")
    aln2mut_parser.add_argument('--input', '-i', dest = 'input', type = str, required = True, help = "Input alignment in the FASTA format")
    aln2mut_parser.add_argument('--outdir', '-o', dest = 'outdir', type = str, required = False, default = '.', help = "Output directory (default: current working directory)")
    aln2mut_parser.add_argument('--output_prefix', '-p', dest = 'output_prefix', type = str, required = False, default = 'mutations', help = "Prefix for output files (default: mutations)")
    aln2mut_parser.add_argument('--ref_name', '-r', dest = 'ref_name', type = str, required = True, help = "Name of the reference sequence in the alignment")
    aln2mut_parser.add_argument('--list', '-l', dest = 'list', action = 'store_true', help = "Create a list of alterations in a conventional format (e.g., W25N)")
    aln2mut_parser.add_argument('--var', '-v', dest = 'var', action = 'store_true', help = "Create a FASTA-format alignment file of variable sites only")

    return parser.parse_args()


def main():
    args = parse_arguments()
    if args.subcommand == 'detect':
        detect(query = args.queries, assemblies = args.assemblies, assembly_suffix = args.assembly_suffix, outdir = args.outdir, \
               min_identity = args.min_identity, min_qcov = args.min_qcov, max_evalue = args.max_evalue, max_match_num = args.max_match_num, \
               pause = args.pause, job_reload = args.reload, cd_hit_est_path = args.cd_hit_est, threads = args.threads)
    elif args.subcommand == 'call_alleles':
        call_alleles(hit_table = args.compiled_hit_table, sample_list = args.sample_list, queries_fasta = args.queries,\
                     representatives_dir = args.representatives_dir, outdir = args.outdir)
    elif args.subcommand == 'aln2mut':
        aln2mut(aln_file = args.input, outdir = args.outdir, output_prefix = args.output_prefix, ref_name = args.ref_name, vcf_to_list = args.list, var_aln = args.var)


if __name__ == '__main__':
    main()
