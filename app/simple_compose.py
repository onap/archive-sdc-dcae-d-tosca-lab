#Author: Shu Shi
#emaiL: shushi@research.att.com

from toscalib.tosca_workbook import ToscaWorkBook
    
workbook = ToscaWorkBook()

workbook._import_dir('./data/tosca_model/')
workbook._import_dir('./data/shared_model/')

workbook._use('foi', 'NO_PREFIX')
workbook._assign('policy_0', 'policy_id', 'something_filled_by_CLAMP')

workbook._export_yaml('test_template.yaml', 'noexpand,main,rawfunc')

workbook._add_shared_node([{'dcae.capabilities.dockerHost': 'docker_host'}, {'dcae.capabilities.composition.host': 'composition_virtual'}])
 
workbook._load_translation_db('./data/tosca_model/')
workbook._load_translation_db('./data/shared_model/')

workbook._export_yaml('./data/blueprint/foi.yaml', 'cloudify,main')
#workbook._export_yaml('test_template2.yaml', 'noexpand,main,rawfunc')


