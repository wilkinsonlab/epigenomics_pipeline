#!/usr/bin/env python
from bioblend import galaxy
import re
import sys

## get port
port = sys.argv[1]

gi = galaxy.GalaxyInstance(url='http://localhost:' + port, key='admin')

# create histories for the analyses
print("creating histories")
hist_1 = gi.histories.create_history(name =' ChIP-Seq 1')
hist_2 = gi.histories.create_history(name = 'ChIP-Seq 2')
hist_3 = gi.histories.create_history(name = 'RNA-Seq')

# get workflows
print("finding workflows")
wf11 = gi.workflows.get_workflows(name='ChIP-Seq analysis from fastq 1')[0]
wf12 = gi.workflows.get_workflows(name='ChIP-Seq analysis from fastq 2')[0]
wf2 = gi.workflows.get_workflows(name='RNA-Seq analysis from fastq')[0]

# create library and upload files
print("uploading files to galaxy")
my_lib = gi.libraries.create_library('test_lib', description='Test data', synopsis=None)

## chipseq
chip_path = "./test_data/chipseq_reads/"
chip_files = ["chip1_1-r1.fq.gz", "chip1_1-r2.fq.gz", 
    "chip1_2-r1.fq.gz", "chip1_2-r2.fq.gz", "chip2_1-r1.fq.gz", 
    "chip2_1-r2.fq.gz", "chip2_2-r1.fq.gz", "chip2_2-r2.fq.gz", 
    "input1_1-r1.fq.gz","input1_1-r2.fq.gz", "input1_2-r1.fq.gz", 
    "input1_2-r2.fq.gz", "input2_1-r1.fq.gz", "input2_1-r2.fq.gz", 
    "input2_2-r1.fq.gz", "input2_2-r2.fq.gz"]

lib_chip = {}
for f in chip_files:
    lib_chip.update({f: gi.libraries.upload_file_from_local_path(my_lib['id'], chip_path + f, folder_id=None, file_type='fastqsanger.gz', dbkey='test_genome')})

fl1 = gi.libraries.upload_file_from_local_path(my_lib['id'], chip_path + "chiplist1", folder_id=None, file_type='txt', dbkey='test_genome')
fl2 = gi.libraries.upload_file_from_local_path(my_lib['id'], chip_path + "chiplist2", folder_id=None, file_type='txt', dbkey='test_genome')

## rnaseq
rna_path = "./test_data/rnaseq_reads/"
rna_files = ["rna1_1-r1.fq.gz", "rna1_2-r1.fq.gz", "rna1_3-r1.fq.gz", 
    "rna2_1-r1.fq.gz", "rna2_2-r1.fq.gz", "rna2_3-r1.fq.gz"]

lib_rna = {}
for f in rna_files:
    lib_rna.update({f: gi.libraries.upload_file_from_local_path(my_lib['id'], rna_path + f, folder_id=None, file_type='fastqsanger.gz', dbkey='test_genome')})

fl3 = gi.libraries.upload_file_from_local_path(my_lib['id'], rna_path + "rnalist", folder_id=None, file_type='txt', dbkey='test_genome')

## genome resources
gff_path = "./test_data/genome/"
lib_gff = gi.libraries.upload_file_from_local_path(my_lib['id'], gff_path + "genes.gff", folder_id=None, file_type='gff3', dbkey='test_genome')


# create collections
fwd_chip1 = [x for x in chip_files if re.search("1_.?-r1", x)]
f_list1 = [{'id': lib_chip[f][0]['id'], 'name': f.split("-")[0], 'src': 'ldda'} for f in fwd_chip1]
f_coll_desc1 = {'collection_type': 'list',
 'element_identifiers': f_list1,
 'name': 'forward'}
col_11 = gi.histories.create_dataset_collection(hist_1['id'], f_coll_desc1)

rev_chip1 = [x for x in chip_files if re.search("1_.?-r2", x)]
r_list1 = [{'id': lib_chip[f][0]['id'], 'name': f.split("-")[0], 'src': 'ldda'} for f in rev_chip1]
r_coll_desc1 = {'collection_type': 'list',
 'element_identifiers': r_list1,
 'name': 'reverse'}
col_12 = gi.histories.create_dataset_collection(hist_1['id'], r_coll_desc1)

fwd_chip2 = [x for x in chip_files if re.search("2_.?-r1", x)]
f_list2 = [{'id': lib_chip[f][0]['id'], 'name': f.split("-")[0], 'src': 'ldda'} for f in fwd_chip2]
f_coll_desc2 = {'collection_type': 'list',
 'element_identifiers': f_list2,
 'name': 'forward'}
col_21 = gi.histories.create_dataset_collection(hist_2['id'], f_coll_desc2)

rev_chip2 = [x for x in chip_files if re.search("2_.?-r2", x)]
r_list2 = [{'id': lib_chip[f][0]['id'], 'name': f.split("-")[0], 'src': 'ldda'} for f in rev_chip2]
r_coll_desc2 = {'collection_type': 'list',
 'element_identifiers': r_list2,
 'name': 'reverse'}
col_22 = gi.histories.create_dataset_collection(hist_2['id'], r_coll_desc2)

f_list = [{'id': lib_rna[f][0]['id'], 'name': f.split("-")[0], 'src': 'ldda'} for f in rna_files]
f_coll_desc = {'collection_type': 'list',
 'element_identifiers': f_list,
 'name': 'forward'}
col_3 = gi.histories.create_dataset_collection(hist_3['id'], f_coll_desc)


# run workflows
print("running test analysis")
wf_input1 = {'0': {'id': col_11['id'], 'src': 'hdca'}, '1': {'id': col_12['id'], 'src': 'hdca'}, 
    '2': {'id': fl1[0]['id'], 'src': 'ld'}}
wf_input2 = {'0': {'id': col_21['id'], 'src': 'hdca'}, '1': {'id': col_22['id'], 'src': 'hdca'}, 
    '2': {'id': fl2[0]['id'], 'src': 'ld'}}
wf_input3 = {'0': {'id': col_3['id'], 'src': 'hdca'}, '1': {'id': lib_gff[0]['id'], 'src': 'ld'}, 
    '2': {'id': fl3[0]['id'], 'src': 'ld'}}

wf_run1 = gi.workflows.invoke_workflow(wf11['id'], inputs = wf_input1, history_id = hist_1['id'], import_inputs_to_history = True)
wf_run2 = gi.workflows.invoke_workflow(wf12['id'], inputs = wf_input2, history_id = hist_2['id'], import_inputs_to_history = True)
wf_run3 = gi.workflows.invoke_workflow(wf2['id'], inputs = wf_input3, history_id = hist_3['id'], import_inputs_to_history = True)
