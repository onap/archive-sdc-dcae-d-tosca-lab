#Author: Shu Shi
#emaiL: shushi@research.att.com

from toscalib.tosca_workbook import ToscaWorkBook
from toscalib.tosca_builder import ToscaBuilder

import getopt, sys, json, os, logging

def usage():
    print('OPTIONS:')
    print('\t-h|--help: print this help message')
    print('\t-i|--input: The PATH to spec file')
    print('\t-o|--output: the output file name')
    print('\t-n|--name: the name of the service')

    
def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hi:o:n:", ["help", "input=", "output=", "name="])
    except getopt.GetoptError as err:
        logging.error( str(err)) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)

    spec_file = None
    output_file = None
    name = None
    
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
        else:
            logging.error( 'Unrecognized option: ' + o)
            usage()
            sys.exit(2)
            
    if spec_file is None or output_file is None:
        logging.error( 'Incorrect arguments!')
        usage()
        sys.exit(2)

    dirname = os.path.dirname(output_file)           
    
    if dirname is not None and len(dirname) > 0:
        try:
            os.stat(dirname)
        except:
            os.mkdir(dirname) 

    meta_model = './data/meta_model/meta_policy_schema.yaml'
                    
    builder = ToscaBuilder()
    
    builder.import_schema(meta_model)
    builder.import_spec(spec_file)
    if name is None:
        name = builder.spec_import.name
    if builder._using_policy() is False:
        logging.warning( 'NO policy is defined in the spec')
        return
    builder.create_policy()
    builder.export_policy(output_file)

if __name__ == "__main__":
    main()