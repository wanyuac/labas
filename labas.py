#!/usr/bin/env python

"""
MegaBLAST-based search of query sequences against genome assemblies.

Dependencies: BLAST+, BioPython, Python 3

Example command: python labas.py --queries query/query_genes.fna --genomes *.fna

Note: this script cannot grep FASTA files for --genomes on Windows OS. Please use Windows's Linux subsystem to run this script.

Copyright (C) 2023 Yu Wan <wanyuac@126.com>
Licensed under the GNU General Public Licence version 3 (GPLv3) <https://www.gnu.org/licenses/>.
Creation: 14 Jan 2023; the latest update: 15 Jan 2023.
"""

import os
import sys
from argparse import ArgumentParser
from lib.BLAST import BLAST
from lib.utilities import check_dir, check_file, check_assemblies, check_values

def parse_arguments():
    parser = ArgumentParser(description = "Targeted gene detection for assemblies")
    parser.add_argument('--queries', '-q', dest = 'queries', type = str, required = True, help = "(Mandatory) a multi-Fasta file of query DNA sequences")
    parser.add_argument('--genomes', '-g', nargs = '+', dest = "genomes", type = str, required = True, help = "(Mandatory) Fasta files of genome assemblies against which queries will be searched")
    parser.add_argument('--assembly_suffix', '-s', dest = 'assembly_suffix', type = str, required = False, default = 'fna', help = "Filename extension (fasta/fna/fa, etc) to be removed from assembly filenames in order to get a sample name (Default: fna)")
    parser.add_argument('--outdir', '-o', dest = 'outdir', type =str, required = False, default = 'results', help = "Output directory (Default: results)")
    parser.add_argument('--output_prefix', '-p', dest = 'output_prefix', type = str, required = False, default = 'BLAST', help = "Output prefix for the table of results (Default: labas)")
    parser.add_argument('--min_identity', '-mi', dest = 'min_identity', type = float, default= 80.0, required = False, help = "Minimum percent nucleotide identity for BLAST to identify a match (Default: 80.0; range: 70-100)")
    parser.add_argument('--min_qcov', '-mq', dest = 'min_qcov', type = float, default = 80.0, required = False, help = "Minimum percent query coverage for BLAST to identify a match (Default: 80.0; range: 0-100)")
    parser.add_argument('--max_evalue', '-me', dest = 'max_evalue', type = str, default = '1e-5', required = False, help = "Maximum E-value for BLAST to identify a match (Default: 1e-5)")
    parser.add_argument('--max_match_num', '-mh', dest = 'max_match_num', type = int, default = 5, required = False, help = "Maximum number of matches reported by BLAST for each query sequence (Default: 5; Range: 1-500)")
    return parser.parse_args()


def main ():
    args = parse_arguments()

    # Environmental settings and sanity check
    out_dirs = {'root' : args.outdir, 'blast' : os.path.join(args.outdir, '1_blast'), 'parsed' : os.path.join(args.outdir, '2_parsed')}
    for d in out_dirs.values():
        check_dir(d)
    if check_file(f = args.queries, message = True):
        blast = BLAST(query_fasta = args.queries, min_identity = check_values(v = args.min_identity, v_min = 70.0, v_max = 100.0, v_reset = 80.0, n = 'min_identity'),\
                      min_qcov = check_values(v = args.min_qcov, v_min = 0, v_max = 100.0, v_reset = 80.0, n = 'min_qcov'), max_evalue = args.max_evalue,\
                      max_hits = check_values(v = args.max_match_num, v_min = 1, v_max = 200, v_reset = 5, n = 'max_match_num'))
        blast.check_executives()
    else:
        sys.exit(1)
    genomes = check_assemblies(fs = args.genomes, suf = '.' + args.assembly_suffix)  # Return: {genome name : Path of the assembly's FASTA file}
    n = len(genomes)
    if n > 0:
        print(f"Number of genomes: {n}", file = sys.stdout)
    else:
        print("Error: none of input genomes exists.", file = sys.stderr)
        sys.exit(1)

    # Iteratively run megaBLAST through genomes
    blast_out_dir = out_dirs['blast']
    for g, fasta in genomes.items():
        blast.search(subject_name = g, subject_fasta = fasta, outdir = blast_out_dir)
    return


if __name__ == '__main__':
    main()
