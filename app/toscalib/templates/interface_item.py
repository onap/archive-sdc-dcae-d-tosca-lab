from toscalib.templates.property_item import PropertyItem
from toscalib.templates.operation_item import OperationItem
from toscalib.types.property import PropertyDefinition
from toscalib.templates.constant import *
import logging

class InterfaceItem(object):
    def __init__(self, definition, name = None, content = None):
        if definition is not None:
            self.name = definition.name
            self.type = definition.type
            self.definition = definition
            self.inputs = {}
            self.operations = {}
            self.parent_node = None
            for prop in definition.inputs.keys():
                self.inputs[prop] = PropertyItem(definition.inputs[prop])
            for oper in definition.operations.keys():
                self.operations[oper] = OperationItem(definition.operations[oper])
        else:
            self.name = name
            self.type = None
            self.definition = None
            self.inputs = {}
            self.operations = {}
            self.parent_node = None
        
        self._parse_pre_defined_content(content)
        
    def _parse_pre_defined_content(self, content):
        if content is None:
            return
        
        for key_name in content.keys():         
            if key_name == 'type':
                if self.type is not None and self.type != content[key_name]:
                    logging.warning( 'interface: '+ self.name+ 'type is different in definition: '+ self.type+ ' overwritten here to '+ self.raw_content[key_name])
                self.type = content[key_name]
                continue
            if key_name == 'inputs':
                input_sec = content['inputs']
                for input_item in input_sec.keys():
                    self.inputs[input_item] = PropertyItem(PropertyDefinition(input_item))
                    self.inputs[input_item]._assign(input_sec[input_item])
                continue
            
#            if self.operations.has_key(key_name):
            if key_name in self.operations:
                self.operations[key_name]._parse_pre_defined_content(content[key_name])
            else:
                self.operations[key_name] = OperationItem(None, key_name, content[key_name]) 
            
    def _update_parent_node(self, parent):
        self.parent_node = parent
        for prop in iter(self.inputs.values()):
            prop._update_parent_node(parent)
        for ops in iter(self.operations.values()):
            ops._update_parent_node(parent)

    def _prepare_output(self, tags=''):
        output = {}
        if 'cloudify' not in tags:
            if self.type is not None:
                output[YMO_INT_TYPE] = self.type
            if len(self.inputs) > 0: 
                inputs = {}
                for prop_name in self.inputs.keys():
                    prop_item = self.inputs[prop_name]
                    if prop_item.value is None:
                        prop_value = None
                    else:
                        prop_value = prop_item.value._get_value(tags)[0]
                    inputs[prop_name] = prop_value
                output[YMO_INT_INPUTS] = inputs
        if len(self.operations) > 0:
            for op_name in self.operations.keys():
                output[op_name] = self.operations[op_name]._prepare_output(tags)
 
        return output
    