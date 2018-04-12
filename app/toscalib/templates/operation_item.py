from toscalib.templates.property_item import PropertyItem
from toscalib.types.property import PropertyDefinition
from toscalib.templates.constant import *


class OperationItem(object):
    def __init__(self, definition, name = None, content = None):
        if definition is not None:
            self.name = definition.name
            self.implementation = definition.implementation
            self.definition = definition
            self.inputs = {}
            self.parent_node = None

            for prop in definition.inputs.keys():
                self.inputs[prop] = PropertyItem(definition.inputs[prop])
        else:
            self.name = name
            self.implementation = None
            self.definition = None
            self.inputs = {}
            self.parent_node = None
        
        if content is not None: 
            self._parse_pre_defined_content(content)
        
    def _parse_pre_defined_content(self, content):
        if content is None:
            return

        if type(content) is not dict:
            self.implementation = content
            return
        
        for key_name in content.keys():         
            if key_name == 'implementation':
                self.implementation = content[key_name]
            if key_name == 'inputs':
                input_sec = content['inputs']
                for input_item in input_sec.keys():
                    self.inputs[input_item] = PropertyItem(PropertyDefinition(input_item))
                    self.inputs[input_item]._assign(input_sec[input_item])
            
    def _update_parent_node(self, parent):
        self.parent_node = parent
        for prop in iter(self.inputs.values()):
            prop._update_parent_node(parent)
        
    def _prepare_output(self, tags=''):
        output = {}
#         if self.implementation is not None:
#             output[YMO_OP_IMPLEMENTATION] = self.implementation
#             if 'cloudify' in tags:
#                 output[YMO_OP_EXECUTOR] = 'central_deployment_agent'
        if len(self.inputs) > 0: 
            inputs = {}
            for prop_name in self.inputs.keys():
                prop_item = self.inputs[prop_name]
                if prop_item.value is None:
                    prop_value = None
                else:
                    prop_value = prop_item.value._get_value(tags)[0]
                inputs[prop_name] = prop_value
            output[YMO_OP_INPUTS] = inputs
        return output
