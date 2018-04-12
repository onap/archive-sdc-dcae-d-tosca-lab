#Author: Shu Shi
#emaiL: shushi@research.att.com


import os
from toscalib.utils.yamlparser import load_yaml, simple_parse
from toscalib.templates.database import ToscaDB
from toscalib.types.node import NodeType
from toscalib.types.data import DataType
from toscalib.types.capability import CapabilityType
from toscalib.types.relationship import RelationshipType
from toscalib.templates.constant import *
from toscalib.templates.topology import ToscaTopology
from macpath import dirname
import logging


# _TRUE_VALUES = ('True', 'true', '1', 'yes')

class import_context(object):
    def __init__(self):
        self.curr_path = os.getcwd()
        self.curr_file_name = ''
        self.metadata = None
        self.temp_name = None
        self.extra_imports = []
        
def _dir_import(files_imported, dir_name, db=None, ctx=None):
    if db is None:
        db = ToscaDB()
    
    if os.path.isdir(dir_name) is False:
        logging.warning( 'Dir: '+ dir_name+ ' not exist! Loading failed!')
        return db
    
    for f in os.listdir(dir_name):
        filename = os.path.join(dir_name, f)
        if os.path.isfile(filename):
            try:
                db = _file_import(files_imported, filename, db)
            except ValueError:
                logging.error( 'Fail to import file: '+ filename)
                continue
        if os.path.isdir(filename):
            try: 
                db = _dir_import(files_imported, filename, db)
            except ValueError:
                logging.error( 'Fail to import dir: '+ filename)
                continue
    
    return db  
 
     
    
def _file_import(files_imported, filename, db=None, ctx=None):
    logging.debug( 'Start to import file: '+ filename)

    if db is None:
        db = ToscaDB()
        
    if ctx is None:
        orig_import = True
        ctx = import_context()
    else:
        orig_import = False
            
    if filename == os.path.abspath(filename):
        full_file_path = filename
    else:
        full_file_path = os.path.abspath(os.path.join(ctx.curr_path, filename))
        
    if os.path.isfile(full_file_path) == False:
        logging.debug( 'File: ' + filename + ' not exist! Import as extra import!')
        ctx.extra_imports.append({filename:filename})
        return db
    
    if full_file_path in files_imported:
        logging.debug( 'File: ' + filename + ' has been imported!')
        return db
    
    ctx.curr_path = os.path.dirname(full_file_path)
    ctx.curr_file_name = os.path.basename(full_file_path)
    parser = load_yaml(full_file_path)

    ctx.extra_imports = []
    
#    if parser.has_key(IMPORT):
    if IMPORT in parser:
        db = _parse_import(files_imported, parser[IMPORT], db, ctx)
#    if parser.has_key(METADATA):
    if METADATA in parser:
        ctx.metadata = parser[METADATA]
#    if parser.has_key(DATA_TYPE):
    if DATA_TYPE in parser:
        db = _parse_data_type(parser[DATA_TYPE], db, ctx)
#    if parser.has_key(NODE_TYPE):
    if NODE_TYPE in parser:
        db = _parse_node_type(parser[NODE_TYPE], db, ctx)
#    if parser.has_key(TOPOLOGY):
    if TOPOLOGY in parser:
        db = _parse_topology_template(parser[TOPOLOGY], db, ctx)
#    if parser.has_key(CAPABILITY_TYPE):
    if CAPABILITY_TYPE in parser:
        db = _parse_capability_type(parser[CAPABILITY_TYPE], db, ctx)
#    if parser.has_key(RELATIONSHIP_TYPE):
    if RELATIONSHIP_TYPE in parser:
        db = _parse_relationship_type(parser[RELATIONSHIP_TYPE], db, ctx)
    
    if orig_import:
        db._parse_objects()
    
    files_imported.append(full_file_path)
    logging.debug( 'File '+ filename+ ' imported!')
    return db

def _single_template_file_import(filename, db=None, ctx=None):
    logging.debug( 'Start to import file: '+ filename)

    if db is None:
        db = ToscaDB()
        
    if ctx is None:
        ctx = import_context()
            
    if filename == os.path.abspath(filename):
        full_file_path = filename
    else:
        full_file_path = os.path.abspath(os.path.join(ctx.curr_path, filename))
        
    if os.path.isfile(full_file_path) == False:
        logging.warning( 'File: ' +filename + ' not exist! Import failed!')
        return db
    
    
    ctx.curr_path = os.path.dirname(full_file_path)
    ctx.curr_file_name = os.path.basename(full_file_path)
    parser = load_yaml(full_file_path)
    
#     if parser.has_key(IMPORT):
#         db = _parse_import(files_imported, parser[IMPORT], db, ctx)
    ctx.extra_imports = []
#    if parser.has_key(IMPORT):
    if IMPORT in parser:
        db = _parse_import([], parser[IMPORT], db, ctx)
#    if parser.has_key(METADATA):
    if METADATA in parser:
        ctx.metadata = parser[METADATA]
#    if parser.has_key(DATA_TYPE):
    if DATA_TYPE in parser:
        db = _parse_data_type(parser[DATA_TYPE], db, ctx)
#    if parser.has_key(NODE_TYPE):
    if NODE_TYPE in parser:
        db = _parse_node_type(parser[NODE_TYPE], db, ctx)
#    if parser.has_key(TOPOLOGY):
    if TOPOLOGY in parser:
        db = _parse_topology_template(parser[TOPOLOGY], db, ctx)
#    if parser.has_key(CAPABILITY_TYPE):
    if CAPABILITY_TYPE in parser:
        db = _parse_capability_type(parser[CAPABILITY_TYPE], db, ctx)
#    if parser.has_key(RELATIONSHIP_TYPE):
    if RELATIONSHIP_TYPE in parser:
        db = _parse_relationship_type(parser[RELATIONSHIP_TYPE], db, ctx)
    
    db._parse_objects()
    
    logging.debug( 'File '+ filename+ ' imported!')
    return db

def _yaml_str_import(yml_str, db=None, ctx=None):
    parser = simple_parse(yml_str)
    
    if ctx is None:
        ctx = import_context()

    ctx.extra_imports = []
    
#    if parser.has_key(IMPORT):
    if IMPORT in parser:
        db = _parse_import([], parser[IMPORT], db, ctx)
#    if parser.has_key(METADATA):
    if METADATA in parser:
        ctx.metadata = parser[METADATA]
#    if parser.has_key(DATA_TYPE):
    if DATA_TYPE in parser:
        db = _parse_data_type(parser[DATA_TYPE], db, ctx)
#    if parser.has_key(NODE_TYPE):
    if NODE_TYPE in parser:
        db = _parse_node_type(parser[NODE_TYPE], db, ctx)
#    if parser.has_key(TOPOLOGY):
    if TOPOLOGY in parser:
        db = _parse_topology_template(parser[TOPOLOGY], db, ctx)
#    if parser.has_key(CAPABILITY_TYPE):
    if CAPABILITY_TYPE in parser:
        db = _parse_capability_type(parser[CAPABILITY_TYPE], db, ctx)
#    if parser.has_key(RELATIONSHIP_TYPE):
    if RELATIONSHIP_TYPE in parser:
        db = _parse_relationship_type(parser[RELATIONSHIP_TYPE], db, ctx)
    
    db._parse_objects()
    
    return db

def _parse_data_type(data_type_section, db, ctx):
    if data_type_section is None:
        return db
    if db is None: 
        db = ToscaDB()
        
    for data_type_name in data_type_section.keys():
        db._import_data_type(DataType(data_type_name, data_type_section[data_type_name]))
    return db

def _parse_node_type(node_type_section, db, ctx):    
    if node_type_section is None:
        return db
    if db is None:
        db = ToscaDB()
            
    for node_type_def_name in node_type_section.keys():
        db._import_node_type(NodeType(node_type_def_name, node_type_section[node_type_def_name]))
    return db

def _parse_capability_type(cap_type_section, db, ctx):    
    if cap_type_section is None:
        return db
    if db is None:
        db = ToscaDB()
            
    for cap_type_def_name in cap_type_section.keys():
        db._import_capability_type(CapabilityType(cap_type_def_name, cap_type_section[cap_type_def_name]))
    return db

def _parse_relationship_type(rel_type_section, db, ctx):    
    if rel_type_section is None:
        return db
    if db is None:
        db = ToscaDB()
            
    for rel_type_def_name in rel_type_section.keys():
        db._import_relationship_type(RelationshipType(rel_type_def_name,rel_type_section[rel_type_def_name]))
    return db

def _parse_topology_template(topology_section, db, ctx):    
    if topology_section is None:
        return db
    if db is None:
        db = ToscaDB()
        
    if ctx.metadata is None or ctx.metadata['template_name'] is None or ctx.metadata['template_name']=='':
        template_key = ctx.curr_file_name
    else:
        template_key = ctx.metadata['template_name']
        
    if template_key is None or template_key == '':
        index = 0
        while True:
#            if db.TEMPLATES.has_key('template'+str(index)):
            if 'template'+str(index) in db.TEMPLATES:
                index+=1
                continue
            break
        template_key = 'template'+str(index)
        
    ctx.temp_name = template_key
    
    new_topology = ToscaTopology(template_key, ctx.metadata, topology_section)
    new_topology.extra_imports = ctx.extra_imports
    db._import_template(new_topology)
            
    return db

def _parse_requirement_name_and_value(content):
    list_size = len(content.keys())
    if list_size != 1:
        logging.warning( 'Requirement section does not have exact one element: '+ list_size)
        return
    ck = list(content.keys())[0]
    return ck, content[ck]        
        
def _parse_import(file_imported, import_section, db, ctx):
    if db is None:
        db = ToscaDB()
        
    if import_section is None:
        return db
    
    for new_file_sec in import_section:
#        for new_file in new_file_sec.itervalues():
        for new_file in iter(new_file_sec.values()):
            curr_path_bk = ctx.curr_path
            curr_filename_bk = ctx.curr_file_name
            _file_import(file_imported, new_file, db, ctx)
            ctx.curr_path = curr_path_bk
            ctx.curr_file_name = curr_filename_bk
        
    return db
