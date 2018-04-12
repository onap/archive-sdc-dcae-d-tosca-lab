from toscalib.templates.constant import *
from toscalib.templates.property_item import PropertyItem
import logging

class CapabilityItem(object):
    def __init__(self, definition):
        self.name = definition.name
        self.type = definition.type
        self.definition = definition
        self.properties = {}
        self.id = PropertyItem(definition.id)
        self.sub_pointer = None
        self.parent_node = None
        for prop in definition.properties.keys():
            self.properties[prop] = PropertyItem(definition.properties[prop])
        
    def _parse_pre_defined_content(self, content):
        if content is None:
            return
#        if content.has_key(CAP_PROPERTIES):
        if CAP_PROPERTIES in content:
            prop_sec = content[CAP_PROPERTIES]
            for prop_name in prop_sec.keys():
                prop_item = self._get_property_item(prop_name)
                if prop_item is not None:
                    prop_item._assign(prop_sec[prop_name])

    def _propagate_substitution_value(self):
        converge = True
        for prop_item in iter(self.properties.values()):
            converge = converge and prop_item._propagate_substitution_value()
        
        if self.sub_pointer is None:
            return converge
        
        if self.id.value is None:
            old_val = None
        else:
            old_val = self.id.value._get_value()[0]
        
        if isinstance(self.sub_pointer, PropertyItem):
            if self.sub_pointer.value is None:
                logging.warning( 'Something is wrong, the cap id mapping target'+ self.sub_pointer.name+ ' should have a value!')
                return converge
            self.id._direct_assign(self.sub_pointer.value)
        from toscalib.templates.node import Node
        if isinstance(self.sub_pointer, Node):
            if self.sub_pointer.id is None or self.sub_pointer.id.value is None:
                logging.warning( 'Something is wrong, the cap id mapping target'+ self.sub_pointer.name+ ' should have a value!')
                return converge
            self.id._direct_assign(self.sub_pointer.id.value)
        
        if self.id.value is None:
            new_val = None
        else:      
            new_val = self.id.value._get_value()[0]
        return converge and (old_val == new_val)

    def _get_property_item(self, prop_name):
#        if self.properties.has_key(prop_name):
        if prop_name in self.properties:
            return self.properties[prop_name]
        else:
            logging.warning('Capability: '+ self.name+ ' of type: '+ self.type+ ' has no property: '+ prop_name)
            return None
    
    def _validate_capability(self, cap_name):
        return self.definition._validate_capability(cap_name)
            
    def _update_parent_node(self, parent):
        self.parent_node = parent
        for prop in iter(self.properties.values()):
            prop._update_parent_node(parent)
