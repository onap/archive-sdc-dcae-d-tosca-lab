#Author: Shu Shi
#emaiL: shushi@research.att.com


from toscalib.templates.constant import *
from toscalib.templates.property_item import PropertyItem
import logging

class RequirementItem(object):
    def __init__(self, definition):
        self.name = definition.name
        self.value = None
        self.str_value = None
        self.cap_match = None
        self.filled = False
        self.pending = False
        
        self.req_capability = definition.req_capability        
        self.relationship = definition.relationship
        self.req_type = definition.req_type
        self.filter = None
        self.sub_pointer = None
        self.parent_node = None


    def _assign(self, value):
        if value is None:
            logging.warning( 'Assign None to fulfill requirement')
            return False
        
        for cap_item in iter(value.capabilities.values()):
            if cap_item._validate_capability(self.req_capability) is True:
                self.cap_match = cap_item
                break
        if self.cap_match is None:
            logging.warning( 'No matching capabilities in requirement assignment')
            return False
        else:
            self.value = value
            self.str_value = value.name
            self.filled = True
        
            return True
    
    def _propagate_substitution_value(self):
        if self.sub_pointer is None:
            return True
        if self.filled is not True:
            return True

        if isinstance(self.sub_pointer, RequirementItem):
            if self.cap_match.sub_pointer is None:
                self.sub_pointer._assign(self.value)
            else:
                self.sub_pointer._assign(self.cap_match.sub_pointer.parent_node)
        elif isinstance(self.sub_pointer, PropertyItem):
            if self.cap_match.id.value is not None:
                self.sub_pointer._direct_assign(self.cap_match.id.value)
            
        return True    
        
    
    def _verify_requirement(self, node_dict):
        if self.filled is True:
#            if node_dict.has_key(self.str_value):
            if self.str_value in node_dict:
                self._assign(node_dict[self.str_value])
            else:
                logging.warning( 'Error! the node requires \''+ self.str_value+ '\' not defined in the template!')
                self.str_value = None
                self.filled = False
        if self.pending is True:
#            if node_dict.has_key(self.str_value):
            if self.str_value in node_dict:
                self._assign(node_dict[self.str_value])
                self.pending = None
            else:
                self.req_type = self.str_value
                self.str_value = None
                self.pending = None
                
    def _verify_node(self, node):
        if node._verify_req_node(self.req_type, self.req_capability, self.filter) is False:
            logging.warning( 'requirement matching failed')
            return False
        
        return True
        
    
    def _update_prefix(self, prefix):
        if self.filled is True:
            self.str_value = prefix + self.str_value        
            
    def _update_parent_node(self, parent):
        self.parent_node = parent    
        
    def _parse_pre_defined_content(self, content):
        if type(content) is str:
            self.str_value = content
            self.filled = True
        elif type(content) is dict:
#            if content.has_key(REQ_NODE):
            if REQ_NODE in content:
                self.str_value = content[REQ_NODE]
                self.pending = True
#            if content.has_key(REQ_CAPABILITY):
            if REQ_CAPABILITY in content:
                self.req_capability = content[REQ_CAPABILITY]
#            if content.has_key(REQ_RELATIONSHIP):
            if REQ_RELATIONSHIP in content:
                self.relationship = content[REQ_RELATIONSHIP]
#            if content.has_key(REQ_FILTER):
            if REQ_FILTER in content:
                self.filter = content[REQ_FILTER]
        else:
            logging.warning( 'Can not parse requirement assignment for '+self.name)
