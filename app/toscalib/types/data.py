#Author: Shu Shi
#emaiL: shushi@research.att.com

import ast
import copy, logging
from toscalib.templates.constant import *
from toscalib.types.constraints import PropertyConstraints
from toscalib.types.entry_schema import EntrySchema

BUILT_IN_TYPES= (TYP_BOOL, TYP_INT, TYP_FLT, TYP_STR, TYP_MAP, TYP_LIST, TYP_VER, TYP_SIZE, TYP_TIME, TYP_FREQ, TYP_ANY) = \
                ('boolean', 'integer', 'float', 'string', 'map', 'list', 'version', 'scalar-unit.size', 'scalar-unit.time', 'scalar-unit.frequency', 'output')                                          

def _is_integer(value):
    try: 
        int(value)
        return True
    except ValueError:
        return False   
    
def _is_float(value):
    try: 
        float(value)
        return True;
    except ValueError:
        return False

def _is_true(value):
    if value is True:
        return True
    elif value in TRUE_VALUES:
        return True
    else:
        return False 
        
             
class DataType:
    def __init__(self, name, content=None):
        self.name = name
        self.entry = EntrySchema(TYP_ANY)
        self.contraints = None
        self.used = False
        self.parent_type = None
        if content is None:
            self.built_in = True
            self.type = self.name
            self.raw_content = None
            self.parsed = False
        else:
            self.built_in = False
            self.type = None
            self.raw_content = content
            self.parsed = False
        
    @classmethod
    def _built_in_types(cls):
        return BUILT_IN_TYPES
    
    def _parse_content(self, db):
        if self.parsed is True:
            return
        
        self.properties = {}

        if self.raw_content is None:
            self.parsed = True
            self.entry._parse_content(db)        

            return
        
#        if self.raw_content.has_key(NOD_DERIVED_FROM):
        if NOD_DERIVED_FROM in self.raw_content:
            self.parent_type = self.raw_content[NOD_DERIVED_FROM]
#            if db.DATA_TYPES.has_key(self.parent_type):
            if self.parent_type in db.DATA_TYPES:
                self.parent = db.DATA_TYPES[self.parent_type]
                self.parent._parse_content(db)
                self.type = self.parent.type
                self.properties = copy.deepcopy(self.parent.properties)

            elif self.parent_type in BUILT_IN_TYPES:
                self.type = self.parent_type
            else:
                self.type = None
                logging.warning( 'Unrecognized data type: '+ self.parent_type)
        else:
            self.type = TYP_MAP
            
#        if self.raw_content.has_key(NOD_PROPERTIES):
        if NOD_PROPERTIES in self.raw_content:
            prop_sec = self.raw_content[NOD_PROPERTIES]
            for prop_name in prop_sec.keys():
                from toscalib.types.property import PropertyDefinition
                self.properties[prop_name] = PropertyDefinition(prop_name, prop_sec[prop_name])
                self.properties[prop_name]._parse_content(db)
         
#        if self.raw_content.has_key(PROP_CONSTRAINT):
        if PROP_CONSTRAINT in self.raw_content:
            self.constraints = PropertyConstraints(self.raw_content[PROP_CONSTRAINT])
            self.constraints._parse_content()
        else:
            self.constraints = None
        
        self.entry._parse_content(db)        
        
        self.parsed = True
        pass
    
    def _customozed_format_value(self, value):
        if self.type == TYP_INT:
            if _is_integer(value):
                return int(value)
            else:
                return None
        if self.type == TYP_FLT:
            if _is_float(value):
                return float(value)
            else:
                return None
        if self.type == TYP_BOOL:
            if _is_true(value):
                return True
            else:
                return False
        elif self.type == TYP_STR:
            return value
        elif self.type == TYP_LIST:
            return self._parse_string_to_list(value)
        elif self.type == TYP_MAP:
            return self._parse_string_to_map(value, self.properties)
               
        else:
        #TODO add support for version, scalar-unit
            return value

    
    def _format_value(self, value):
        if self.built_in is True:
            if self.type == TYP_INT:
                if _is_integer(value):
                    return int(value)
                else:
                    return None
            if self.type == TYP_BOOL:
                if _is_true(value):
                    return True
                else:
                    return False
            elif self.type == TYP_STR:
                return str(value)
            elif self.type == TYP_LIST:
                return self._parse_string_to_list(value)
            elif self.type == TYP_MAP:
                return self._parse_string_to_map(value)
            elif self.type == TYP_ANY:
                if type(value) is int:
                    self.type = TYP_INT
                    return value
                if type(value) is bool:
                    self.type = TYP_BOOL
                    return value
                if type(value) is list:
                    self.type = TYP_LIST
                    self.entry = EntrySchema(TYP_ANY)
                    self.entry._parse_content(None)
                    return self._parse_string_to_list(value)
                if type(value) is dict:
                    self.type = TYP_MAP
                    self.entry = EntrySchema(TYP_ANY)
                    self.entry._parse_content(None)
                    return self._parse_string_to_map(value)        
                self.type = TYP_STR
                return str(value)
        
            else:
            #TODO add support for version, scalar-unit
                return value
        else:
            return self._customozed_format_value(value)  
    
    def _update_prefix(self, prefix, value):
        if self.type == TYP_LIST:
            for value_item in value:
                value_item._update_prefix(prefix)
        elif self.type == TYP_MAP:
            for value_item in iter(value.values()):
                value_item._update_prefix(prefix)
        else:
            return
    
    def _update_function_reference(self, temp, value, self_node = None, self_item= None):
        if self.type == TYP_LIST:
            for value_item in value:
                value_item._update_function_reference(temp, self_node, self_item)
        elif self.type == TYP_MAP:
            for value_item in iter(value.values()):
                value_item._update_function_reference(temp, self_node, self_item)
        else:
            return
        
    def _get_value(self, value, tags=''):
        from toscalib.templates.value import VALID_VALUE, FUNCTION, NULL
        if self.type == TYP_LIST:
            out_str = []
            real_value = VALID_VALUE
            for value_item in value:
                out_item, real_item = value_item._get_value(tags)
                if real_item is NULL:
                    continue

                out_str.append(out_item)
                if real_item is FUNCTION:
                    real_value = real_item
            return out_str, real_value
        elif self.type == TYP_MAP:
            out_str = {}
            real_value = VALID_VALUE
            for value_key in value.keys():
                temp_out, real_item = value[value_key]._get_value(tags)
                if real_item is NULL:
                    continue
                
                out_str[value_key] = temp_out
                if real_item is FUNCTION:
                    real_value = real_item
            return out_str, real_value
        else:
            return value, VALID_VALUE
            
    def _parse_string_to_list(self, value):
        try: 
            list_value = ast.literal_eval(str(value))
            if type(list_value) is list:
                out_list = []
                for list_item in list_value:
                    from toscalib.templates.value import Value
                    out_list.append(Value(self.entry.type_obj, list_item))
                return out_list
            else:
                logging.debug( 'List formatted string required for list type: ')
                logging.debug('Value is 1: '+ value)
                return None
        except ValueError:
            logging.error( 'List formatted string required for list type: ')
            logging.error( 'Value is 2: '+ value)
            return None
     
    def _parse_string_to_map(self, value, property_set = None):
        try: 
            map_value = ast.literal_eval(str(value))
            if type(map_value) is dict:
                out_map = {}
                from toscalib.templates.value import Value

                if property_set is None: 
                    for key_item in map_value.keys():
                        out_map[key_item] = Value(self.entry.type_obj, map_value[key_item])
                    return out_map
                else:
                    for key_item in property_set.keys():
                        if key_item in map_value.keys():
                            out_map[key_item] = Value(property_set[key_item].type_obj, map_value[key_item])
                    return out_map
            else:
                logging.debug( 'Map formatted string required for map type: ')
                logging.debug( 'Value is 1: '+ value)
                return None
        except ValueError:
            logging.error( 'Map formatted string required for map type: ')
            logging.error( 'Value is 2: '+ value)
            return None  
        
    def _create_rawcontent(self):
        self.raw_content= {}
        if self.parent_type is not None:
            self.raw_content[YMO_NOD_DERIVED_FROM] = self.parent_type
        prop_sec = {}
        for prop_key in self.properties.keys():
            if self.properties[prop_key].raw_content is  None:
                self.properties[prop_key]._create_rawcontent()
            prop_sec[prop_key] = self.properties[prop_key].raw_content
        if len(prop_sec) > 0:
            self.raw_content[YMO_NOD_PROPERTIES] = prop_sec    
