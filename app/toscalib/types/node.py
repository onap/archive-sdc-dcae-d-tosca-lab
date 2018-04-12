#Author: Shu Shi
#emaiL: shushi@research.att.com


from toscalib.templates.constant import *
from toscalib.types.property import PropertyDefinition
from toscalib.types.requirement import RequirementDefinition
from toscalib.types.capability import CapabilityDefinition
import copy, logging
from toscalib.types.interface import InterfaceDefinition

            
class NodeType(object):
    def __init__(self, name, content):
        if name is None or content is None:
            return None
        self.name = name
        self.parent_type = None
        self.parent = None
        self.id = PropertyDefinition('id')
        self.mapping_template = None
        self.raw_content = content
        self.used = False
        self.parsed = False
        self.properties = {}
        self.attributes = {}
        self.capabilities = {}
        self.requirements = []
        self.interfaces = {}
        
#         self._parse_content(content)
        
    def _parse_content(self, db):
        if self.parsed is True:
            return
        
        self.id._parse_content(db)
        
        if self.raw_content is None:
            self.parsed = True
            logging.warning( 'Parsing Node '+ self.name+ ', content is None')
            return
        
#        if self.raw_content.has_key(NOD_DERIVED_FROM):
        if NOD_DERIVED_FROM in self.raw_content:
            self.parent_type = self.raw_content[NOD_DERIVED_FROM]
#            if db.NODE_TYPES.has_key(self.parent_type):
            if self.parent_type in db.NODE_TYPES:
                self.parent = db.NODE_TYPES[self.parent_type]
                self.parent._parse_content(db)
            elif self.parent_type != 'tosca.nodes.Root':
                logging.warning( 'Node '+ self.parent_type+ ' not imported but used!')
        else:
            logging.warning( 'Node type '+ self.name+ ' has no parent type to derive from')
            
        if self.parent is not None:
            self.properties = copy.deepcopy(self.parent.properties)
            self.attributes = copy.deepcopy(self.parent.attributes)

#        if self.raw_content.has_key(NOD_PROPERTIES):
        if NOD_PROPERTIES in self.raw_content:
            prop_sec = self.raw_content[NOD_PROPERTIES]
            for prop_name in prop_sec.keys():
#                if self.properties.has_key(prop_name):
                if prop_name in self.properties:
#                     self.properties[prop_name].update(PropertyDefinition(prop_name, prop_sec[prop_name]))
#                 else:
                    logging.debug( 'Property name '+ prop_name+ ' has been defined in parent type, overwritten here!')
                self.properties[prop_name] = PropertyDefinition(prop_name, prop_sec[prop_name])
                self.properties[prop_name]._parse_content(db)

#        if self.raw_content.has_key(NOD_ATTRIBUTES):
        if NOD_ATTRIBUTES in self.raw_content:
            attr_sec = self.raw_content[NOD_ATTRIBUTES]
            for attr_name in attr_sec.keys():
#                if self.attributes.has_key(attr_name):
                if attr_name in self.attributes:
#                     self.properties[prop_name].update(PropertyDefinition(prop_name, prop_sec[prop_name]))
#                 else:
                    logging.debug( 'Attribute name '+ attr_name+ ' has been defined in parent type, overwritten here!')
                self.attributes[attr_name] = PropertyDefinition(attr_name, attr_sec[attr_name])
                self.attributes[attr_name]._parse_content(db)
                         
        if self.parent is not None:
            self.requirements = copy.deepcopy(self.parent.requirements)
        
#        if self.raw_content.has_key(NOD_REQUIREMENTS):
        if NOD_REQUIREMENTS in self.raw_content:
            req_sec = self.raw_content[NOD_REQUIREMENTS]
            for req in req_sec:
                req_item = RequirementDefinition(req)
                req_item._parse_content(db)
                if req_item.name is not None:
                    self.requirements.append(req_item)
         
        if self.parent is not None:
            self.capabilities = copy.deepcopy(self.parent.capabilities)
        
#        if self.raw_content.has_key(NOD_CAPABILITIES):
        if NOD_CAPABILITIES in self.raw_content:
            cap_sec = self.raw_content[NOD_CAPABILITIES]
            for cap_name in cap_sec.keys():
#                if self.capabilities.has_key(cap_name):
                if cap_name in self.capabilities:
                    logging.warning( 'Capability name '+ cap_name+ ' has been defined in parent type, overwritten here!')
                self.capabilities[cap_name] = CapabilityDefinition(cap_name, cap_sec[cap_name])
                self.capabilities[cap_name]._parse_content(db)
     
        self.parsed = True
        
        if self.parent is not None:
            self.interfaces = copy.deepcopy(self.parent.interfaces)
            
#        if self.raw_content.has_key(NOD_INTERFACES):
        if NOD_INTERFACES in self.raw_content:
            interface_sec = self.raw_content[NOD_INTERFACES]
            for interface_name in interface_sec.keys():
#                if self.interfaces.has_key(interface_name):
                if interface_name in self.interfaces:
                    logging.warning( 'Interface name'+ interface_name+ 'has been definend in parenty type, overwritten here')
                self.interfaces[interface_name] = InterfaceDefinition(interface_name, interface_sec[interface_name])
                self.interfaces[interface_name]._parse_content(db)
        
    def _verify_req_type(self, req_type):
        if self.name == req_type:
            return True
        if self.parent is not None:
            return self.parent._verify_req_type(req_type)
        else:
            logging.warning( 'Type '+ self.parent_type+ ' is not imported or defined')
            return self.parent_type == req_type
                
                
    def _create_rawcontent(self):
        self.raw_content= {}
        if self.parent_type != None:
            self.raw_content[YMO_NOD_DERIVED_FROM] = self.parent_type
        else:
            self.raw_content[YMO_NOD_DERIVED_FROM] = 'tosca.nodes.Root'
        prop_sec = {}
        for prop_key in self.properties.keys():
            if self.properties[prop_key].raw_content is  None:
                self.properties[prop_key]._create_rawcontent()
            prop_sec[prop_key] = self.properties[prop_key].raw_content
        if len(prop_sec) > 0:
            self.raw_content[YMO_NOD_PROPERTIES] = prop_sec    
        
        attr_sec = {}
        for prop_key in self.attributes.keys():
            if self.attributes[prop_key].raw_content is  None:
                self.attributes[prop_key]._create_rawcontent()
            attr_sec[prop_key] = self.attributes[prop_key].raw_content   
        if len(attr_sec)>0 :
            self.raw_content[YMO_NOD_ATTRIBUTES] = attr_sec    
            
        cap_sec = {}
        for cap_key in self.capabilities.keys():
            cap_sec[cap_key] = self.capabilities[cap_key].raw_content   
        if len(cap_sec)>0 :
            self.raw_content[YMO_NOD_CAPABILITIES] = cap_sec
    
        req_sec = []
        for req in self.requirements:
            req_sec.append(req.raw_content)
        if len(req_sec)>0 :
            self.raw_content[YMO_NOD_REQUIREMENTS] = req_sec
            
        if len(self.interfaces) > 0:
            int_sec = {}
            for int_name in self.interfaces.keys():
                int_sec[int_name] = self.interfaces[int_name].raw_content
            self.raw_content[YMO_NOD_INTERFACES] = int_sec
        
            