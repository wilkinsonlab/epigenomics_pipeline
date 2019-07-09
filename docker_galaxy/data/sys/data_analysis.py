#!/usr/bin/env python
from bioblend import galaxy
import re
import sys

## get port
port = sys.argv[1]

gi = galaxy.GalaxyInstance(url='http://localhost:' + port, key='admin')

# create histories for the analyses
print("creating histories")
hist_1 = gi.histories.create_history(name =' ChIP-Seq leaf')
hist_2 = gi.histories.create_history(name = 'ChIP-Seq infl')
hist_3 = gi.histories.create_history(name = 'RNA-Seq all')

# prepare workflows
print("preparing workflows")
wf1 = gi.workflows.get_workflows(name='Brapa ChIP-Seq analysis')[0]
wf2 = gi.workflows.get_workflows(name='Brapa RNA-Seq analysis')[0]

ew11 = gi.workflows.export_workflow_dict(wf1['id'])
ew12 = gi.workflows.export_workflow_dict(wf1['id'])
ew2 = gi.workflows.export_workflow_dict(wf2['id'])

ew11['name'] = u'Brapa ChIP-Seq leaf'
ew12['name'] = u'Brapa ChIP-Seq infl'
ew2['name'] = u'Brapa RNA-Seq all'

## modify export folder for chipseq
for i in range(1,len(ew11['steps'])):
    try:
        if re.search("export",ew11['steps'][str(i)]['tool_id']):
            ew11['steps'][str(i)]['tool_state'] = re.sub("res/","res/chipseq1",ew11['steps'][str(i)]['tool_state'])
            ew12['steps'][str(i)]['tool_state'] = re.sub("res/","res/chipseq2",ew12['steps'][str(i)]['tool_state'])
    except:
            continue
## modify export folder for rnaseq
for i in range(1,len(ew2['steps'])):
    try:
            if re.search("export",ew2['steps'][str(i)]['tool_id']):
                    ew2['steps'][str(i)]['tool_state'] = re.sub("-res","-res/rnaseq",ew2['steps'][str(i)]['tool_state'])
    except:
            continue

## import modified workflows
print("uploading workflows")
iw11 = gi.workflows.import_workflow_dict(ew11)
iw12 = gi.workflows.import_workflow_dict(ew12)
iw2 = gi.workflows.import_workflow_dict(ew2)

# create library to upload files
print("uploading files to galaxy")
file_path = "/data/files/"
my_lib = gi.libraries.create_library('Brapa_lib', description='B. rapa data', synopsis=None)
lib_sra1 = gi.libraries.upload_file_from_local_path(my_lib['id'], file_path + "SRA01", folder_id=None, file_type='txt', dbkey='Brapa_chiifu_v3.0')
lib_sra2 = gi.libraries.upload_file_from_local_path(my_lib['id'], file_path + "SRA02", folder_id=None, file_type='txt', dbkey='Brapa_chiifu_v3.0')
lib_sra3 = gi.libraries.upload_file_from_local_path(my_lib['id'], file_path + "SRA03", folder_id=None, file_type='txt', dbkey='Brapa_chiifu_v3.0')
lib_gff = gi.libraries.upload_file_from_local_path(my_lib['id'], file_path + "Brapa_3.0_myUTR.gff", folder_id=None, file_type='gff3', dbkey='Brapa_chiifu_v3.0')

# transfer files from library to histories
dat1 = gi.histories.upload_dataset_from_library(hist_1['id'], lib_sra1[0]['id'])
dat2 = gi.histories.upload_dataset_from_library(hist_2['id'], lib_sra2[0]['id'])
dat3 = gi.histories.upload_dataset_from_library(hist_3['id'], lib_sra3[0]['id'])
dat4 = gi.histories.upload_dataset_from_library(hist_3['id'], lib_gff[0]['id'])

# run with data from library
print("run analysis")
wf_input1 = {'0': {'id': lib_sra1[0]['id'], 'src': 'ld'}}
wf_input2 = {'0': {'id': lib_sra2[0]['id'], 'src': 'ld'}}
wf_input3 = {'0': {'id': lib_sra3[0]['id'], 'src': 'ld'}, '1': {'id': lib_gff[0]['id'], 'src': 'ld'}}

wf_run1 = gi.workflows.invoke_workflow(iw11['id'], inputs = wf_input1, history_id = hist_1['id'], import_inputs_to_history = True)
wf_run2 = gi.workflows.invoke_workflow(iw12['id'], inputs = wf_input2, history_id = hist_2['id'], import_inputs_to_history = True)
wf_run3 = gi.workflows.invoke_workflow(iw2['id'], inputs = wf_input3, history_id = hist_3['id'], import_inputs_to_history = True)
