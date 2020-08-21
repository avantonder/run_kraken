#!/usr/bin/env python

import os, argparse, sys, subprocess

#Script and database locations

KRAKEN_DIR = "/software/pathogen/etc/kraken/1.1.1/wrappers/kraken"
KRAKEN_REPORT_DIR = "/software/pathogen/etc/kraken/1.1.1/wrappers/kraken-report"
KRAKEN_DATABASE = "/lustre/scratch118/infgen/team81/avt/M_bovis/kraken/minikraken_20171019_8GB"
BRACKEN_DIR = "~avt/Software/Bracken/src/est_abundance.py"
BRACKEN_DATABASE = "/lustre/scratch118/infgen/team81/avt/NTM/minikraken_8GB_100mers_distrib.txt"
JOB_ARRAY = "~jh22/scripts/run_array"
RUN_KRAKEN_BIN_DIR = "~avt/Scripts/run_kraken/bin/"

#Parse command line options

def parse_args(args):

	global _parser

	_parser = argparse.ArgumentParser(description = 'run_kraken.py: a tool for running kraken and bracken on a user-defined list of fastq files')
	_parser.add_argument('--fastq_ids', '-f', help='A file containing fastq IDs e.g. 12345_1.fastq.gz [REQUIRED]')
	_parser.add_argument('--threshold', '-c', help='Minimum percentage of reads assigned to a species to be reported (default = 5) [OPTIONAL]')
	_parser.add_argument('--output_prefix', '-o', help='Prefix to append to output files (default = Bracken) [OPTIONAL]')

	opts = _parser.parse_args(args)

	return opts

#Write list of commands to file for job array script

def joblist_writer(filename, command_list):

	with open(filename, 'w') as file_handler:
		file_handler.write("\n".join(str(i) for i in command_list))

#Main script

def main(opts):

	if not opts.output_prefix:
		out_name = 'Bracken'
	else:
		out_name = str(opts.output_prefix)

	if not opts.threshold:
		min_threshold = 5
	else:
		min_threshold = opts.threshold

	fastq_files = open(opts.fastq_ids).readlines()
	fastq_names = [i.split('\n')[0] for i in fastq_files]
	id_list = [i.split('_1.')[0] for i in fastq_files]
	classified_list = [i + '_classified.fastq' for i in id_list]
	unclassified_list = [i + '_unclassified.fastq' for i in id_list]
	kraken_out_list = [i + '_kraken.out' for i in id_list]
	kraken_report_list = [i + '_kraken.report' for i in id_list]
	bracken_report_list = [i + '_output_species_abundance.txt' for i in id_list]

	os.makedirs('kraken_results')

	kraken_bsub_CMD = '-q normal -M8000 -R "select[mem>8000] rusage[mem=8000]" -n8 -R "span[hosts=1]" -o o.%J -e e.%J -J '
	kraken_job_name = '"krakenArray[1-' + str(len(id_list)) + ']%50" '
	
	kraken_array_CMD = []

	for a, b, c, d in zip(classified_list, unclassified_list, kraken_out_list, fastq_names):
		kraken_array_CMD.append(KRAKEN_DIR + ' --threads 8 --fastq-input --gzip-compressed --classified-out kraken_results/' + a + ' --unclassified-out kraken_results/' + b + ' --output kraken_results/' + c + ' -db ' + KRAKEN_DATABASE + ' ' + d)

	joblist_writer('joblist.txt', kraken_array_CMD)

	kraken_submission = 'bsub ' + kraken_bsub_CMD + kraken_job_name + JOB_ARRAY + ' joblist.txt'

	subprocess.call(kraken_submission, shell = True)

	kraken_array_report_CMD = []

	for a, b in zip(kraken_out_list, kraken_report_list):
		kraken_array_report_CMD.append(KRAKEN_REPORT_DIR + ' --db ' + KRAKEN_DATABASE + ' kraken_results/' + a + ' > kraken_results/' + b)

	joblist_writer('joblist2.txt', kraken_array_report_CMD)

	kraken_report_bsub_CMD = '-q normal -M1000 -R "select[mem>1000] rusage[mem=1000]" -o o.%J -e e.%J -w "done(krakenArray[*])" -J '
	kraken_job_name_2 = '"krakenArray2[1-' + str(len(id_list)) + ']%50" '

	kraken_report_submission = 'bsub ' + kraken_report_bsub_CMD + kraken_job_name_2 + JOB_ARRAY + ' joblist2.txt'

	subprocess.call(kraken_report_submission, shell = True)

	bracken_bsub_CMD = '-q normal -M8000 -R "select[mem>8000] rusage[mem=8000]" -o o.%J -e e.%J -w "done(krakenArray2[*])" -J '
	bracken_job_name = '"brackenArray[1-' + str(len(id_list)) + ']%50" '

	bracken_array_CMD = []

	for a, b in zip(kraken_report_list, bracken_report_list):
		bracken_array_CMD.append('python ' + BRACKEN_DIR + ' -i kraken_results/' + a + ' -k ' + BRACKEN_DATABASE + ' -l S -t 10 -o kraken_results/' + b)

	joblist_writer('joblist3.txt', bracken_array_CMD)

	bracken_submission = 'bsub ' + bracken_bsub_CMD + bracken_job_name + JOB_ARRAY + ' joblist3.txt'

	subprocess.call(bracken_submission, shell = True)

	kraken_output_bsub_CMD = '-q normal -M1000 -R "select[mem>1000] rusage[mem=1000]" -o o.%J -e e.%J -w "ended(brackenArray*)" -J krakenOutput '

	kraken_output_CMD = 'python ' + RUN_KRAKEN_BIN_DIR + 'kraken_parser.py' + ' -o ' + out_name + ' -c ' + str(min_threshold)

	kraken_parser_CMD = 'bsub ' + kraken_output_bsub_CMD + kraken_output_CMD

	subprocess.call(kraken_parser_CMD, shell = True)

if __name__ == "__main__":
  opts= parse_args(sys.argv[1:])
  main(opts)
