#Author: Shu Shi
#emaiL: shushi@research.att.com


from toscalib.templates.constant import *
import ast, logging

class PropertyItem(object):
    def __init__(self, definition):
        self.name = definition.name
        self.type_obj = definition.type_obj
        self.filled = False
        self.definition = definition
        self.value = None
        self.required = definition.required
        self.sub_pointer = None
        self.used = True
        self.parent_node = None
    
    def _assign(self, value):
#         from toscalib.templates.capability_item import CapabilityItem
        from toscalib.templates.value import Value
        if value is None:
            return False
#         elif isinstance(value, CapabilityItem):
#             self.value = value
#             self.filled = True
        else:
            self.value = Value(self.type_obj, value)
#             formatted_value = self.type._format_value(value) 
            if self.value is None:
                logging.warning( 'Value can not be assigned: validation failed!')
            else:
                self.filled = True
        
#         if self.sub_pointer is not None:
#             self.sub_pointer._assign(value)
        
        return True

    def _direct_assign(self, value):
        self.value = value
        if value is not None:
            self.filled = True
            
    def _update_prefix(self, prefix):
        self.name = prefix + self.name
        
    def _update_parent_node(self, parent):
        self.parent_node = parent

    def _propagate_substitution_value(self):
        if self.sub_pointer is None:
            return True
        if self.value is not None:
#            self.sub_pointer._direct_assign(self.value)
            self.sub_pointer._assign(self.value._get_value()[0])
            
        return True
    
    def _propagate_attr_substitution_value(self):
        if self.sub_pointer is None or hasattr(self.sub_pointer, 'value') is False:
            return True
        self._direct_assign(self.sub_pointer.value)        
        return True   
     
    def _prepare_input_type_output(self, tags):
        out_details= {}
        out_details[YMO_PROP_TYPE] = self.type_obj.name
        if hasattr(self.definition, 'default') is True and self.definition.default is not None:
            if 'w_default' in tags:
                return {}
            out_details[YMO_PROP_DEFAULT] = self.definition.default
            
        out_val = {}
        out_val[self.name] =out_details
        return out_val

    def _prepare_output_type_output(self):
        out_val = {}
        val_body = self.value._get_value()[0]
        out_val[self.name] =dict(value=val_body)
        return out_val
    
    def _prepare_heat_output(self):
        type_out = {}
        type_out[self.name] =dict(type=self.type.name)
        val_out = {}
        if self.filled:
            val_out[self.name] = self.value
        else:
            val_out[self.name] = None
        
        return type_out, val_out
        
