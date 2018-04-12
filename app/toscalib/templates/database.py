#Author: Shu Shi
#emaiL: shushi@research.att.com

from toscalib.templates.constant import *
import logging

class ToscaDB(object):
    """ The database that stores all node types and TEMPLATES """
    def __init__(self):
        self.NODE_TYPES = {}
        self.CAPABILITY_TYPES = {}
        self.RELATIONSHIP_TYPES = {}
        self.DATA_TYPES = {}
        self.TEMPLATES = {}
        
    def _import_node_type(self, new_type):
        if new_type is None:
            return
#        if self.NODE_TYPES.has_key(new_type.name) == True:
        if new_type.name in self.NODE_TYPES:
            logging.debug( 'Node type: '+ new_type.name+ ' already defined and will be overwritten')
        self.NODE_TYPES[new_type.name]=new_type
            
    def _import_capability_type(self, new_type):
        if new_type is None:
            return
#        if self.CAPABILITY_TYPES.has_key(new_type.name) == True:
        if new_type.name in self.CAPABILITY_TYPES:
            logging.debug( 'Capability type: '+ new_type.name+ ' already defined and will be overwritten')

        self.CAPABILITY_TYPES[new_type.name]=new_type

    def _import_relationship_type(self, new_type):
        if new_type is None:
            return
#        if self.RELATIONSHIP_TYPES.has_key(new_type.name) == True:
        if new_type.name in self.RELATIONSHIP_TYPES:
            logging.debug( 'Relationship type: '+ new_type.name+ ' already defined and will be overwritten')

        self.RELATIONSHIP_TYPES[new_type.name]=new_type

    def _import_data_type(self, new_type):
        if new_type is None:
            return
#        if self.DATA_TYPES.has_key(new_type.name) == True:
        if new_type.name in self.DATA_TYPES:
            logging.debug( 'Data type: '+ new_type.name+ ' already defined and will be overwritten')
        self.DATA_TYPES[new_type.name]=new_type

    def _import_template(self, new_template):
        if new_template is None:
            return
#        if self.TEMPLATES.has_key(new_template.name) == False:
        if new_template.name not in self.TEMPLATES :
            self.TEMPLATES[new_template.name]= new_template        
    
    def _parse_objects(self):
        logging.debug( 'parsing database')
#        for objs in self.NODE_TYPES.itervalues():
        for objs in iter(self.NODE_TYPES.values()):
            objs._parse_content(self)
#        for objs in self.CAPABILITY_TYPES.itervalues():
        for objs in iter(self.CAPABILITY_TYPES.values()):
            objs._parse_content(self)
#        for objs in self.DATA_TYPES.itervalues():
        for objs in iter(self.DATA_TYPES.values()):
            objs._parse_content(self)
#        for objs in self.RELATIONSHIP_TYPES.itervalues():
        for objs in iter(self.RELATIONSHIP_TYPES.values()):
            objs._parse_content(self)
#        for objs in self.TEMPLATES.itervalues():
        for objs in iter(self.TEMPLATES.values()):
            objs._parse_content(self)
            
            
    def _prepare_schema(self):
        schema_output = {}
        data_sec = {}
        for key in self.DATA_TYPES.keys():
            objs = self.DATA_TYPES[key]
            data_sec[key] = objs.raw_content
        node_sec = {}
        for key in self.NODE_TYPES.keys():
            objs = self.NODE_TYPES[key]
            if objs.raw_content is None:
                objs._create_rawcontent()
            node_sec[key]=objs.raw_content
        cap_sec = {}
        for key in self.CAPABILITY_TYPES.keys():
            objs = self.CAPABILITY_TYPES[key]
            cap_sec[key]=objs.raw_content
        rel_sec = {}
        for key in self.RELATIONSHIP_TYPES.keys():
            objs = self.RELATIONSHIP_TYPES[key]
            rel_sec[key]=objs.raw_content
            
        if len(data_sec) > 0:
            schema_output[YMO_DATA_TYPE] = data_sec
        if len(node_sec) > 0:
            schema_output[YMO_NODE_TYPE] = node_sec
        if len(cap_sec) > 0:
            schema_output[YMO_CAPABILITY_TYPE] = cap_sec
        if len(rel_sec) > 0:
            schema_output[YMO_RELATIONSHIP_TYPE] = rel_sec
        
        schema_output[YMO_VERSION]= 'tosca_simple_yaml_1_0_0'
        
        return schema_output
            
    
            
            
            