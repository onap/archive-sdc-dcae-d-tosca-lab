#Author: Shu Shi
#emaiL: shushi@research.att.com

from toscalib.tosca_workbook import ToscaWorkBook
from toscalib.tosca_builder import ToscaBuilder

import getopt, sys, json, os, base64, logging

def usage():
    print('OPTIONS:')
    print('\t-h|--help: print this help message')
    print('\t-i|--input: The PATH to spec file')
    print('\t-o|--output: the folder for the output model ')
    print('\t-n|--name: the name of the service')
    print('\t-t|--import: the PATH to import file')
    print('\t-m|--meta: the PATH to meta model file (default: ./data/meta_model/meta_tosca_schema.yaml')

    
def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hi:o:n:t:m:", ["help", "input=", "output=", "name=", "import=", "meta="])
    except getopt.GetoptError as err:
        # print help information and exit:
        logging.error(str(err)) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)

    spec_file = None
    output_file = './data/tosca_model/temp'
    name = None
    meta_model = './data/meta_model/meta_tosca_schema.yaml'
    import_file = None

    for o, a in opts:
        if  o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-i", "--input"):
            spec_file = a
        elif o in ("-o", "--output"):
            output_file = a
        elif o in ("-n", "--name"):
            name = a
        elif o in ("-t", "--import"):
            import_file = a
        elif o in ("-m", "--meta"):
            meta_model = a
        else:
            logging.error('Unrecognized option: ' + o)
            usage()
            sys.exit(2)
            
    if spec_file is None:
        logging.error('Incorrect arguments!')
        usage()
        sys.exit(2)

    if output_file is None:
        model_prefix = './data/tosca_model'
    else:
        filename = output_file + '/schema.yaml'
        dirname = os.path.dirname(filename)           
        try:
            os.stat(dirname)
        except:
            os.mkdir(dirname) 
        model_prefix = output_file
        
                    
    builder = ToscaBuilder()
        
    builder.import_schema(meta_model)
    if spec_file in ['stdin', '-']:
        builder.import_spec_str(json.load(sys.stdin))
    else:
        builder.import_spec(spec_file)
    if import_file is not None:
        builder.import_import(import_file)
    
    if name is None:
        name = builder.spec_import.name
    
    builder.create_node_type(name)
    schema_str = builder.export_schema(model_prefix+ '/schema.yaml')
    builder.import_schema(model_prefix+ '/schema.yaml')
    builder.create_model(name)
    template_str = builder.export_model(model_prefix+ '/template.yaml')
    builder.create_translate(name)
    translate_str = builder.export_translation(model_prefix+ '/translate.yaml')    
    
    if spec_file in ['stdin', '-']:
        ret = {}
        ret['schema'] = base64.encodestring(schema_str)
        ret['template'] = base64.encodestring(template_str)
        ret['translate'] = base64.encodestring(translate_str) 
        
        print (json.dumps(ret))

if __name__ == "__main__":
    main()