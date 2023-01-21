#!/usr/bin/env python

"""
This module defines class Hits.

Dependencies: Python 3

Copyright (C) 2023 Yu Wan <wanyuac@126.com>
Licensed under the GNU General Public Licence version 3 (GPLv3) <https://www.gnu.org/licenses/>.
Creation: 15 Jan 2023; the latest update: 21 Jan 2023.
"""

import os
import sys
from lib.Hit import Hit, HIT_ATTRS

class Hit_tables:
    """ Manage raw BLAST outputs """
    def __init__(self):
        self.__hit_tables = dict()  # A dictionary {genome : table} of raw BLAST outputs
        return
    
    @property
    def table_num(self):  # Number of hit tables
        return len(self.__hit_tables)

    @property
    def sample_names(self):
        return list(self.__hit_tables.keys())

    def add_table(self, sample, hit_table):  # Parameter hit_table is a list of rows in BLAST's raw tabulated output.
        if hit_table != None:  # Each element of the dictionary __hit_tables stores information of rows in the raw output TSV file when the output is not empty. Otherwise, the table is None.
            ht = dict()  # A temporary hit table (dictionary)
            hits_num = dict()
            for line in hit_table:
                h = Hit(sample = sample, hit_line = line, append_sample_name = True)
                q = h.query
                if q in ht.keys():  # More than one hit of the current query sequence is found by BLAST in the current sample (hit table)
                    n = hits_num[q]
                    if n == 1:  # There is only a single hit in list ht[h.query].
                        h_prev = ht[q][0]
                        h_prev.set_hitid(':'.join([h_prev.hit, '1']))  # For example, 'gene1@sample1:1'
                        ht[q] = [h_prev]
                    n += 1
                    h.set_hitid(':'.join([h.hit, str(n)]))  # For example, 'gene1@sample1:2' for the second hit of gene 1 in sample 1
                    ht[q].append(h)
                    hits_num[q] = n
                else:
                    ht[q] = [h]
                    hits_num[q] = 1
            self.__hit_tables[sample] = ht  # Variable self.__hit_tables[sample_name] is a nested dictionary.
        else:  # No hit is generated at all from the current sample
            self.__hit_tables[sample] = None  # A record is created even if the sample does not have any hits, so we won't lose any samples in downstream analysis.
        return

    def write_hit_sequences(self, query, outdir):
        with open(os.path.join(outdir, '.'.join([query, 'fna'])), 'w') as fasta:  # Override any previous output
            for s, t in self.__hit_tables.items():  # Iterate through hit tables by sample names
                if t != None:
                    if query in t.keys():
                        for h in t[query]:  # Iterate through the list of hits
                            h.write_seq(fasta)
                    else:
                        print(f"Warning (write_hit_sequences): query sequence {query} was not found in sample {s}.", file = sys.stderr)
                else:
                    print(f"Warning (write_hit_sequences): no query sequence was found in sample {s}.", file = sys.stderr)
        return
    
    def compile_tables(self, outdir):
        output_tsv = open(os.path.join(outdir, 'compiled_hits.tsv'), 'w')
        print('\t'.join(['sample', 'hit', 'qseqid', 'sseqid'] + HIT_ATTRS), file = output_tsv)  # Print the header line
        for s, t in self.__hit_tables.items():  # Iterate through hit tables by sample names
            if t != None:
                for hits in t.values():
                    for h in hits:
                        print('\t'.join([s, h.hit] + h.attr_values), file = output_tsv)
            else:
                print(f"Warning (compile_tables): no query sequence was found in sample {s}.", file = sys.stderr)
        output_tsv.close()
        return
