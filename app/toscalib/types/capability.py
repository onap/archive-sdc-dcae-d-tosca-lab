#Author: Shu Shi
#emaiL: shushi@research.att.com


from toscalib.templates.constant import *
from toscalib.types.property import PropertyDefinition
import copy,logging


class CapabilityDefinition:
    def __init__(self, name, content):
        if name is None:
            return None
        self.name = name
        self.type = None
        self.type_obj = None
        self.valid_source = None
        self.parsed = False
        self.id = PropertyDefinition('id')
        self.raw_content = content
        
    def _parse_content(self, db):
        if self.parsed:
            return 
        
        self.id._parse_content(db)
        
        content = self.raw_content
        
        if content is None:
            logging.warning( 'Capability definition'+ self.name+ ' is None!')
            self.parsed = True
            
#        if content.has_key(CAP_TYPE):
        if CAP_TYPE in content:
            self.type = content[CAP_TYPE]
#            if db.CAPABILITY_TYPES.has_key(self.type):
            if self.type in db.CAPABILITY_TYPES:
                self.type_obj = db.CAPABILITY_TYPES[self.type]
                self.type_obj._parse_content(db)
            elif self.type != 'tosca.capabilities.Root':
                logging.warning( 'Capability type '+ self.type+ ' not imported or defined!')
        else:
            logging.warning( 'Capability definition '+ self.name+ ' has no type defined!')         
        
#        if content.has_key(CAP_SOURCE):
        if CAP_SOURCE in content:
            self.valid_source = content[CAP_SOURCE]
        elif self.type_obj is not None :
            self.valid_source = self.type_obj.valid_source
            
        if self.type_obj is not None:
            self.properties = copy.deepcopy(self.type_obj.properties)
        else:
            self.properties = {}

#        if content.has_key(CAP_PROPERTIES):
        if CAP_PROPERTIES in content:
            prop_sec = content[CAP_PROPERTIES]
            for prop_name in prop_sec.keys():
#                if self.properties.has_key(prop_name):
                if prop_name in self.properties:
#                     self.properties[prop_name].update(PropertyDefinition(prop_name, prop_sec[prop_name]))
#                 else:
                    logging.warning( 'Property name '+ prop_name+ ' has been defined in type definition, overwritten here!')
                    self.properties[prop_name] = PropertyDefinition(prop_name, prop_sec[prop_name])
                    self.properties[prop_name]._parse_content(db)
        
        self.parsed = True
        pass

    def _validate_capability(self, cap_name):
        if self.type_obj is not None:
            return self.type_obj._validate_capability(cap_name)
        else:
            return self.type == cap_name


class CapabilityType:
    def __init__(self, name, content):
        if name is None or content is None:
            return None
        self.name = name        
        self.parent_type = None
        self.parent = None
        self.valid_source = None
        self.parsed = False
        self.raw_content = content
                
    def _parse_content(self, db):
        if self.parsed is True:
            return
        
        content = self.raw_content
        if content is None:
            logging.warning( 'Capability type '+ self.name+ ' has None content')
            return
        
#        if content.has_key(CAP_DERIVED_FROM):
        if CAP_DERIVED_FROM in content:
            self.parent_type = content[CAP_DERIVED_FROM]
#            if db.CAPABILITY_TYPES.has_key(self.parent_type):
            if self.parent_type  in db.CAPABILITY_TYPES:
                self.parent = db.CAPABILITY_TYPES[self.parent_type]
                self.parent._parse_content(db)
            elif self.parent_type != 'tosca.capabilities.Root':
                logging.warning( 'Capability type '+ self.parent_type+ ' not imported but defined!')
        else:
            logging.warning( 'Capability type '+ self.name+ ' has no parent type to derive from')
            
        if self.parent is not None:
            self.properties = copy.deepcopy(self.parent.properties)
        else:
            self.properties = {}

#        if content.has_key(CAP_PROPERTIES):
        if CAP_PROPERTIES in content:
            prop_sec = content[CAP_PROPERTIES]
#            for prop_name in prop_sec.keys():
            for prop_name in prop_sec.keys():
#                if self.properties.has_key(prop_name):
                if prop_name in self.properties:
#                     self.properties[prop_name].update(PropertyDefinition(prop_name, prop_sec[prop_name]))
#                 else:
                    logging.warning( 'Property name '+ prop_name+ ' has been defined in parent type, overwritten here!')
                self.properties[prop_name] = PropertyDefinition(prop_name, prop_sec[prop_name])
                self.properties[prop_name]._parse_content(db)
                    
#        if content.has_key(CAP_SOURCE):
        if CAP_SOURCE in content:
            self.valid_source = content[CAP_SOURCE]
                    
        self.parsed = True
        
    def _validate_capability(self, cap_name):
        if self.name == cap_name:
            return True
        if self.parent is not None:
            return self.parent._validate_capability(cap_name)
        else:
            return False
        

                    