#Author: Shu Shi
#emaiL: shushi@research.att.com


from toscalib.templates.database import ToscaDB
from toscalib.utils import tosca_operate, tosca_import, tosca_print, tosca_export
from toscalib.utils.tosca_import import import_context
from toscalib.templates.topology import ToscaTopology
from toscalib.utils.tosca_operate import _assign_property_value,\
    _assign_requirement_value, _assign_capability_property_value
import copy, logging

DEFAULT_TEMPLATE_NAME='default'

class ToscaWorkBook(object):
    def __init__(self):
        self.db = ToscaDB()
        self.tran_db = ToscaDB()
        self.template = ToscaTopology(DEFAULT_TEMPLATE_NAME)
        self.template.db = self.db
        self.imported_files = []
        
    def _reset(self):
        self.template = ToscaTopology(DEFAULT_TEMPLATE_NAME)
        self.template.db = self.db

        
    def _import(self, filename):
        self.db = tosca_import._file_import(self.imported_files, filename, self.db)

    def _import_dir(self, dirname):
        self.db = tosca_import._dir_import(self.imported_files, dirname, self.db)
        
    def _import_yml_str(self, content):
        self.db = tosca_import._yaml_str_import(content, self.db)
        
    def _load_translation_db(self, dir_name, prefix=''):
        self.tran_db = tosca_import._dir_import([], dir_name, self.tran_db)
    
    def _load_translation_library(self):
        if self.tran_db is None or len(self.tran_db.TEMPLATES) < 1:
            return
        
        for node_item in iter(self.template.node_dict.values()):  
            node_item.tran_template = None  
            for tran_temp in iter(self.tran_db.TEMPLATES.values()):
                if hasattr(tran_temp,'sub_type') and tran_temp.sub_type == node_item.type:
                    node_item.tran_template = copy.deepcopy(tran_temp)
                    node_item.tran_template._update_used_tag_for_translation()
                    node_item.tran_template._verify_substitution(node_item)
                    node_item.tran_template._update_prefix(node_item.name + '_')
                    break
    
    def _use(self, type_name, node_name=None):
        if type_name in self.db.NODE_TYPES.keys():
            return tosca_operate._create_new_node(self.template, type_name, node_name)
        elif type_name in self.db.TEMPLATES.keys():
            return tosca_operate._create_new_template(self.template, type_name, node_name)
        else:
            logging.warning('Name: ' + type_name + ' is neither a type or a template. ')
            return None
    
    def _assign(self, node_name, sub_name, value_1, value_2 = None):
#        if self.template.node_dict.has_key(node_name) is False:
        if node_name not in self.template.node_dict:
            logging.warning('Unrecognized node name: ' + node_name)
            return
        node = self.template.node_dict[node_name]
        if value_2 is not None:
#            if  node.capabilities.has_key(sub_name):
            if  sub_name in node.capabilities:
                node_cap = node.capabilities[sub_name]
#                if node_cap.properties.has_key(value_1):
                if value_1 in node_cap.properties:
                    _assign_capability_property_value(node, sub_name, value_1, value_2)
                else:
                    logging.warning( 'Unrecognized tag name: ' + value_1)
            else:
                logging('Unrecognized tag name: ' + sub_name)
#        elif node.properties.has_key(sub_name):
        elif sub_name in node.properties:
            _assign_property_value(node, sub_name, value_1)
        else:
            req_found = False
            for req in node.requirements:
                if req.name == sub_name:
                    req_found = req
                    break
            if req_found is False:
                logging.warning( 'Unrecognized tag name: ' + sub_name)
                return

#            if self.template.node_dict.has_key(value_1):
            if value_1 in self.template.node_dict:
                _assign_requirement_value(node, sub_name, self.template.node_dict[value_1])
            else:
                logging.warning( 'Incorrect node name: ' + value_1 + ', a node name is needed to fulfill requirement')
                return
    
    def _show_abstract(self):
        return tosca_print._print_template(self.template, tosca_print.LEVEL_NODE_NAME)
        
    def _show_details(self):
        return tosca_print._print_template(self.template, tosca_print.LEVEL_NODE_DETAILS)
        
    def _show_types(self):
        return tosca_print._print_node_types(self.db)
        
    def _show_type(self, type_name):
        if type_name in self.db.NODE_TYPES.keys():
            tosca_print._print_node_type(self.db.NODE_TYPES[type_name])
        else:
            logging.warning( 'Node type: '+ type_name+ ' not found!')
      
    def _show_templates(self):
        tosca_print._print_templates(self.db)
              
    def _show_template(self, temp_name):
        if temp_name in self.db.TEMPLATES.keys():
            tosca_print._print_template(self.db.TEMPLATES[temp_name])
        else:
            logging.warning( 'Template: '+ temp_name+ ' not found')
            
    def _translate_template_file(self, filename):
        ctx = import_context()
        self.db = tosca_import._single_template_file_import(filename, self.db, ctx)
        temp_name = ctx.temp_name
        
        self._reset()
        self.tran_db = self.db
        self._use(temp_name, 'NO_PREFIX')
        
    def _translate_template_yaml_str(self, content):
        ctx = import_context()
        self.db = tosca_import._yaml_str_import(content, self.db, ctx)
        temp_name = ctx.temp_name
        
        self._reset()
        self.tran_db = self.db
        self._use(temp_name, 'NO_PREFIX')
        
    def _add_shared_node(self, rel):
        if rel is None or type(rel) is not list:
            return
        
#        node_index = 0;
        
        for rel_entry in rel:
            rel_name = list(rel_entry.keys())[0]
            new_node_name = None
#            temp_node_base= 'node_'

            while True:
                ret_node = self._find_open_requirement(rel_name)
                if ret_node is None:
                    break
                if new_node_name == None:
#                    while True:
#                        temp_node_name = temp_node_base + str(node_index)
#                        if self.template.node_dict.has_key(temp_node_name):
#                            node_index += 1
#                            continue
#                        else:
#                            break
                    if self._use(rel_entry[rel_name], 'NO_PREFIX') == None:
                        break
                    new_node_name = True
                self._assign(ret_node[0], ret_node[1], rel_entry[rel_name])
                
    def _find_open_requirement(self, cap_type):
        for node in iter(self.template.node_dict.values()):
            for req_item in node.requirements:
                if req_item.filled is True:
                    continue
                if req_item.req_capability == cap_type:
                    return [node.name, req_item.name]    
        
        
        
    
    def _export_generic(self, tags=''):        
        self.template._update_function_pointer()
        self._load_translation_library()
#        self.template._auto_generate_aux_inputs()
        self.template._propagate_substitution_value()
        self.template._update_translation_function_pointer()

        return self.template._prepare_output(tags)

    def _export_yaml(self, filename, tags='main,nodetype'):
        return tosca_export._yaml_export(filename, self._export_generic(tags))
    
    def _export_yaml_web(self, tags= 'main,nodetype'):
        return tosca_export._yaml_export('WEB', self._export_generic(tags))
        
    def _export_heat(self, filename):
        tags ='heat,main'
        return tosca_export._heat_export(filename, self._export_generic(tags))
    
    def toJson(self):
        return self.template.toJson()
    