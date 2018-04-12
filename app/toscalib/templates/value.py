from toscalib.types.data import TYP_LIST, TYP_MAP, TYP_STR, DataType
from toscalib.templates.property_item import PropertyItem
import copy, logging

FUNCTIONS = (GET_INPUT, GET_PROPERTY, GET_ATTRIBUTE, GET_OPERATION, GET_NODES, GET_ARTIFACT, CONCAT) = \
            ('get_input', 'get_property', 'get_attribute', 'get_operation_output', 'get_nodes_of_type', 'get_artifact', 'concat')
            
VALUE_STATE = (VALID_VALUE, FUNCTION, NULL) = \
            (1, 2, 3)

def _is_function(value):
    if type(value) is not dict:
        return None
    if len(value.keys()) != 1:
        return None
    key = list(value.keys())[0]
    if key not in FUNCTIONS:
        return None
    
    if key == GET_INPUT:
        out_value = FunctionValue(key)
        out_value.target_property = value[key]
        return out_value
    elif key == CONCAT:
        out_value = FunctionValue(key)
        value_list = value[key]
        if type(value_list) is not list:
            return None
        out_value.extra_data = []
        for value_item in value_list:
            out_value.extra_data.append(Value(DataType(TYP_STR), value_item))
        return out_value
    else:
        out_value = FunctionValue(key)
        value_list = value[key]
        if type(value_list) is not list:
            return None        
        out_value.extra_data = value_list
                
        return out_value
    
        
class FunctionValue(object):
    def __init__(self, func_type):
        self.type = func_type
        self.target_property = None
        self.extra_data = []
        self.value_from_node = None
        self.value_from_item = None
        self.result = None
        
    def _update_prefix(self, prefix):
        if self.type == GET_INPUT:
            self.target_property = prefix + self.target_property
        elif (self.type == GET_PROPERTY or self.type == GET_ATTRIBUTE):
            if self.extra_data is not None and len(self.extra_data) > 1 and self.extra_data[0] != 'SELF':
                if self.extra_data[0] == 'NO_PREFIX':
                    self.extra_data[0] = prefix[:len(prefix)-1]
                else:
                    self.extra_data[0] = prefix + self.extra_data[0]
        elif self.type == CONCAT:
            for item in self.extra_data:
                if item.function is not None: 
                    item._update_prefix(prefix)
                
    def _update_function_reference(self, temp, self_node = None, self_item = None):
        if self.type == GET_INPUT:
#            if temp.inputs.has_key(self.target_property):
            if self.target_property in temp.inputs:
                self.value_from_item = temp.inputs[self.target_property]
                return
#            elif temp.aux_inputs.has_key(self.target_property):
            elif self.target_property in temp.aux_inputs:
                self.value_from_item = temp.aux_inputs[self.target_property]
                return
            else: 
                logging.debug( 'get_input function points to a non-existent input, autofill'+ self.target_property)
                def_item = copy.deepcopy(self_item.definition)
                def_item.name = self.target_property
                temp.inputs[self.target_property] = PropertyItem(def_item)
                self.value_from_item = temp.inputs[self.target_property]
                return 
        elif self.type == GET_PROPERTY:
            if self.extra_data is None or len(self.extra_data) < 2:
                logging.warning('Error, get_property has not enough parameters '+ self.extra_data)
                return 
#            if self.extra_data[0] != 'SELF' and temp.node_dict.has_key(self.extra_data[0]) is False:
            if self.extra_data[0] != 'SELF' and self.extra_data[0] not in temp.node_dict:
                logging.warning( 'Error, get_property from unrecognized node '+ self.extra_data[0])
                return 
            
            if self.extra_data[0] == 'SELF':
                node_item = self_node
            else:
                node_item = temp.node_dict[self.extra_data[0]]
            self.value_from_node = node_item
            
            if len(self.extra_data) == 2:
                self.value_from_item = node_item._get_property_item(self.extra_data[1])
                return
            elif len(self.extra_data) == 3: 
                self.value_from_item = node_item._get_capability_property(self.extra_data[1], self.extra_data[2])
                if self.value_from_item is not None:
                    return
                req_item = node_item._get_requirement_item_first(self.extra_data[1])
                if req_item is None:
                    return
                new_node_item = req_item.value
                if new_node_item is None:
                    self.value_from_node = None
                    return
                self.value_from_node = new_node_item
#                if req_item.cap_match.properties.has_key(self.extra_data[2]):
                if self.extra_data[2] in req_item.cap_match.properties:
                    self.value_from_item = req_item.cap_match.properties[self.extra_data[2]]
                else:
                    self.value_from_item = new_node_item._get_property_item(self.extra_data[2])
                 
            else:
                logging.warning( 'Too many parameters for get_property function '+ self.extra_data)
        elif self.type == GET_ATTRIBUTE:
            if self.extra_data is None or len(self.extra_data) < 2:
                logging.error( 'Error, get_attribute has not enough parameters '+ self.extra_data)
                return 
#            if self.extra_data[0] != 'SELF' and temp.node_dict.has_key(self.extra_data[0]) is False:
            if self.extra_data[0] != 'SELF' and self.extra_data[0]  not in temp.node_dict:
                logging.error( 'Error, get_attribute from unrecognized node '+ self.extra_data[0])
                return 
            
            if self.extra_data[0] == 'SELF':
                node_item = self_node
            else:
                node_item = temp.node_dict[self.extra_data[0]]
            
            self.value_from_node = node_item            
            
            if len(self.extra_data) > 3:
                logging.warning( 'Too many parameters for get_attribute function '+ self.extra_data)
                return
            if self.extra_data[1] == 'id':
                self.value_from_item = node_item.id
            else:
                self.value_from_item = node_item._get_attribute_item(self.extra_data[1])
            
            if self.value_from_item is not None:
                return
            req_item = node_item._get_requirement_item_first(self.extra_data[1])
            if req_item is None:
                return
            new_node_item = req_item.value
            if new_node_item is None:
                self.value_from_node = None
                return
            self.value_from_node = new_node_item
            self.value_from_item = new_node_item._get_attribute_item(self.extra_data[2]) 
            return
        
        elif self.type == CONCAT:
            for item in self.extra_data:
                if item.function is not None: 
                    item._update_function_reference(temp, self_node)
        else:
            logging.warning( 'Function '+ self.type+ ' is not supported')
            return
        
    def _calculate_function_result(self, tags= '' ):
        if 'func' in tags:
            return self._get_function_representation(tags), FUNCTION
        
        if self.type == CONCAT:
            function_ret = VALID_VALUE
            function_str = ""
            for item in self.extra_data:
                item_str, item_value = item._get_value(tags)
                if item_value is FUNCTION:
                    function_ret = FUNCTION
                    break
                elif item_str is not None:
                    function_str = function_str + item_str
            if function_ret == FUNCTION:
                return self._get_function_representation(tags), FUNCTION
            else:
                return function_str, function_ret
        
        if 'w_default' in tags and self.type == GET_INPUT and self.value_from_item is not None and hasattr(self.value_from_item.definition, 'default') is True and self.value_from_item.definition.default is not None:
            return self.value_from_item.definition.default, VALID_VALUE
            
        if self.value_from_item is None or self.value_from_item.value is None or self.value_from_item.value.function == self:
            return self._get_function_representation(tags), FUNCTION
        else:
            return self.value_from_item.value._get_value(tags)
        
    def _get_value(self, tags = ''):
        return self._calculate_function_result(tags)
        
    def _get_function_representation(self, tags=''):
        if self.type == GET_INPUT:
            out_str = {}
            out_str[self.type]= self.target_property
        elif self.type == GET_PROPERTY:
            out_str = {}
            if self.value_from_node is  None or 'rawfunc' in tags:
                out_val = copy.deepcopy(self.extra_data)
            else:
                out_val = []
                out_val.append(self.value_from_node.name)
                out_val.append(self.extra_data[len(self.extra_data)-1])
               
            out_str[self.type] = out_val
        elif self.type == GET_ATTRIBUTE:
            out_str = {}
            if self.value_from_node is None or 'rawfunc' in tags:
                out_val = copy.deepcopy(self.extra_data)              
            else:
                out_val = []
                out_val.append(self.value_from_node.name)
                out_val.append(self.extra_data[len(self.extra_data)-1])
            if self.extra_data[1] == 'id' and 'heat' in tags:
                out_str['get_id'] = out_val[0]
            else:
                out_str[self.type] = out_val
        elif self.type == CONCAT:
            out_str = {}
            out_list = []
            for item in self.extra_data:
                item_str, item_value = item._get_value(tags)
                out_list.append(item_str)
            out_str[self.type] = out_list
        else:
            out_str = {}
            out_str[self.type]=  copy.deepcopy(self.extra_data)
        return out_str
    
    def _get_function_result(self):
        return self.result
        
class Value(object):
    def __init__(self, prop_type, value):
        self.type = prop_type.name
        self.type_obj = copy.deepcopy(prop_type)
        self.raw_value = value
        self.value = None
        self.function = _is_function(value)
        
        if self.function is None:
            self.value = self.type_obj._format_value(value)
    
    def _update_function_reference(self, temp, self_node = None, self_item = None):
        if self.value is not None:
            self.type_obj._update_function_reference(temp, self.value, self_node, self_item)
        if self.function is not None:
            self.function._update_function_reference(temp, self_node, self_item)
            
    def _update_prefix(self, prefix):
        if self.value is not None:
            self.type_obj._update_prefix(prefix, self.value)
        if self.function is not None: 
            self.function._update_prefix(prefix)
    
    def _get_value(self, tags = ''):
        if self.function is not None:
            return self.function._get_value(tags)
        if self.value is not None:
            return self.type_obj._get_value(self.value, tags)
        
        