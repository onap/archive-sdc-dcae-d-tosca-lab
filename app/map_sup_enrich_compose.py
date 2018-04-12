#Author: Shu Shi
#emaiL: shushi@research.att.com

from toscalib.tosca_workbook import ToscaWorkBook
from toscalib.tosca_builder import ToscaBuilder

import getopt, sys, json, logging

def usage():
    print('OPTIONS:')
    print('\t-h|--help: print this help message')
    print('\t-i|--input: The home folder where all spec files are')
    print('\t-o|--output: the output file name')
    print('\t-v|--value: the json value file')

    
def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hi:o:v:", ["help", "input=", "output=", "value="])
    except getopt.GetoptError as err:
        # print help information and exit:
        logging.error( str(err)) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)

    spec_prefix = None
    output_file = None
    value_file = None
    
    for o, a in opts:
        if  o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-i", "--input"):
            spec_prefix = a
        elif o in ("-o", "--output"):
            output_file = a
        elif o in ("-v", "--value"):
            value_file = a
        else:
            logging.error( 'Unrecognized option: ' + o)
            usage()
            sys.exit(2)
            
    if spec_prefix is None or output_file is None:
        logging.error( 'Incorrect arguments!')
        usage()
        sys.exit(2)

    model_prefix = './data/tosca_model'
    meta_model = './data/meta_model/meta_tosca_schema.yaml'
        
    for ms in ['map', 'enrich', 'supplement']:
            
        builder = ToscaBuilder()
        
        builder.import_schema(meta_model)
        builder.import_spec(spec_prefix+'/dcae-event-proc/dcae-event-proc-cdap-' + ms+ '\\' + ms+ '_spec.json')
        builder.create_node_type()
        builder.export_schema(model_prefix+'/' + ms + '/schema.yaml')
        builder.import_schema(model_prefix+'/' + ms + '/schema.yaml')
        builder.create_model(ms)
        builder.export_model(model_prefix+'/' + ms + '/template.yaml')
        builder.create_translate(ms)
        builder.export_translation(model_prefix+'/' + ms + '/translate.yaml')
        
    workbook = ToscaWorkBook()
    
    workbook._import_dir(model_prefix)
    workbook._import_dir('./data/shared_model/')
    workbook._use('map','NO_PREFIX')
    workbook._use('supplement','NO_PREFIX')
    workbook._use('enrich','NO_PREFIX')
    
    if value_file is not None: 
        try: 
            with open(value_file) as data_file:
                data = json.load(data_file)
                for ms in ['map', 'enrich', 'supplement']:
#                    if data.has_key(ms):
                    if ms in data:
                        prop_sec = data[ms]
                        for key in prop_sec.keys():
                            workbook._assign(ms, key, prop_sec[key])
        except err :
            logging.error( "Unable to read " +value_file)
            logging.error( str(err))
    workbook._add_shared_node([{'dcae.capabilities.cdapHost':'cdap_host'}, {'dcae.capabilities.dockerHost': 'docker_host'}, {'dcae.capabilities.composition.host': 'composition_virtual'}])
    
    workbook._assign('supplement', 'stream_publish_0', 'map')
    workbook._assign('enrich', 'stream_publish_0', 'supplement')
         
    workbook.tran_db = workbook.db
         
    workbook._export_yaml('event_proc.yaml', 'no_expand,main')
    workbook._export_yaml(output_file, 'cloudify,main')
    
if __name__ == "__main__":
    main()