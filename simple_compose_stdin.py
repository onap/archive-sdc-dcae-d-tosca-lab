#Author: Shu Shi
#emaiL: shushi@research.att.com

import sys, json, base64, logging

from toscalib.tosca_workbook import ToscaWorkBook
    
input_data = sys.stdin.readline()  
try:
    in_data = json.loads(input_data)
except ValueError as e:
    logging.error( 'error, cannot load input json data: ' + str(input_data))

workbook = ToscaWorkBook()
workbook._import_dir('./data/shared_model/')

#if in_data.has_key('models'):
if 'models' in in_data:
    in_model = in_data['models']
    if type(in_model) != list:
        logging.warning( 'models in the input should be a list type')
    for model_entry in in_model:
        for key in ['schema', 'template', 'translate']:
#            if model_entry.has_key(key):
            if key in model_entry:
                workbook._import_yml_str(base64.b64decode(model_entry[key]))

#if in_data.has_key('template'):
if 'template' in in_data:
    in_temp = in_data['template']
    workbook._translate_template_yaml_str(base64.b64decode(in_temp))
    workbook._add_shared_node([{'dcae.capabilities.cdapHost':'cdap_host'}, {'dcae.capabilities.dockerHost': 'docker_host'}, {'dcae.capabilities.composition.host': 'composition_virtual'}])
                
ret = workbook._export_yaml_web('cloudify,main')
print(ret)
