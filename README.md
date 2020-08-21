# run_kraken

Script for running kraken and bracken on on a user-defined list of fastq files to produce a csv file of reads mapped to species. Designed to run on the Sanger farm.

# usage: 

run_kraken_farm5.py [-h] [--fastq_ids FASTQ_IDS] [--threshold THRESHOLD][--output_prefix OUTPUT_PREFIX]

run_kraken.py: a tool for running kraken and bracken 

optional arguments:

-h, --help            show this help message and exit

--fastq_ids FASTQ_IDS, -f FASTQ_IDS A file containing fastq IDs e.g. 12345_1.fastq.gz [REQUIRED]

--threshold THRESHOLD, -c THRESHOLD Minimum percentage of reads assigned to a species to be reported (default = 5) [OPTIONAL]

--output_prefix OUTPUT_PREFIX, -o OUTPUT_PREFIX Prefix to append to output files (default = Bracken)  [OPTIONAL]
