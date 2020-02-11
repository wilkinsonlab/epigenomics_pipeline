#!/usr/bin/env python
from bioblend import galaxy
import re
import sys

## get port
port = sys.argv[1]

gi = galaxy.GalaxyInstance(url='http://localhost:' + port, key='admin')

# get workflows
print("finding workflows")
wf11 = gi.workflows.get_workflows(name='Brapa ChIP-Seq analysis leaf')[0]
wf12 = gi.workflows.get_workflows(name='Brapa ChIP-Seq analysis infl')[0]
wf2 = gi.workflows.get_workflows(name='Brapa RNA-Seq analysis')[0]

# create library to upload files
print("uploading files to galaxy")
my_lib = gi.libraries.create_library('Brapa_lib', description='B. rapa data', synopsis=None)
lib_sra1 = gi.libraries.upload_file_from_local_path(my_lib['id'], "./files/SRA01", 
    folder_id=None, file_type='txt', dbkey='Brapa_chiifu_v3.0')
lib_sra2 = gi.libraries.upload_file_from_local_path(my_lib['id'], "./files/SRA02", 
    folder_id=None, file_type='txt', dbkey='Brapa_chiifu_v3.0')
lib_sra3 = gi.libraries.upload_file_from_local_path(my_lib['id'], "./files/SRA03", 
    folder_id=None, file_type='txt', dbkey='Brapa_chiifu_v3.0')
lib_list1 = gi.libraries.upload_file_from_local_path(my_lib['id'], "./files/chiplist1", 
    folder_id=None, file_type='txt', dbkey='Brapa_chiifu_v3.0')
lib_list2 = gi.libraries.upload_file_from_local_path(my_lib['id'], "./files/chiplist2", 
    folder_id=None, file_type='txt', dbkey='Brapa_chiifu_v3.0')
lib_list3 = gi.libraries.upload_file_from_local_path(my_lib['id'], "./files/rnalist", 
    folder_id=None, file_type='txt', dbkey='Brapa_chiifu_v3.0')
lib_gff = gi.libraries.upload_file_from_local_path(my_lib['id'], "./files/Brapa_3.0_myUTR.gff", 
    folder_id=None, file_type='gff3', dbkey='Brapa_chiifu_v3.0')

# prepare inputs
wf_input1 = {'0': {'id': lib_sra1[0]['id'], 'src': 'ld'}, 
             '1': {'id': lib_list1[0]['id'], 'src': 'ld'}}
wf_input2 = {'0': {'id': lib_sra2[0]['id'], 'src': 'ld'}, 
             '1': {'id': lib_list2[0]['id'], 'src': 'ld'}}
wf_input3 = {'0': {'id': lib_sra3[0]['id'], 'src': 'ld'}, 
             '1': {'id': lib_gff[0]['id'], 'src': 'ld'}, 
             '2': {'id': lib_list3[0]['id'], 'src': 'ld'}}

# create histories for the analyses
print("creating histories")
hist_1 = gi.histories.create_history(name =' ChIP-Seq leaf')
hist_2 = gi.histories.create_history(name = 'ChIP-Seq infl')
hist_3 = gi.histories.create_history(name = 'RNA-Seq')

# run with data from library
print("run analysis")
wf_run1 = gi.workflows.invoke_workflow(wf11['id'], inputs = wf_input1, 
    history_id = hist_1['id'], import_inputs_to_history = True)
wf_run2 = gi.workflows.invoke_workflow(wf12['id'], inputs = wf_input2, 
    history_id = hist_2['id'], import_inputs_to_history = True)
wf_run3 = gi.workflows.invoke_workflow(wf2['id'], inputs = wf_input3,  
    history_id = hist_3['id'], import_inputs_to_history = True)
