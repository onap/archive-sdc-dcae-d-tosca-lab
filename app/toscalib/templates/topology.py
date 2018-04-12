#Author: Shu Shi
#emaiL: shushi@research.att.com


from toscalib.templates.constant import *
from toscalib.templates.heat_constants import *
from toscalib.templates.substitution_rule import SubstitutionRule
from toscalib.types.property import PropertyDefinition
from toscalib.templates.property_item import PropertyItem
from toscalib.templates.heat_constants import HOT_VERSION_NUM
import copy, logging

class ToscaTopology(object):
    def __init__(self, name, metadata_section=None, content_section=None):
        self.name = name
        self.metadata = metadata_section
        self.raw_content = content_section
        self.db  = None

        self.node_dict = {}
        self.inputs = {}
        self.aux_inputs = {}
        self.outputs = {}
        self.sub_rules = []

        self.node_index = 0
        self.temp_index = 0
        
        self.extra_imports = []
        
    def _parse_content(self, db):
        if self.db is not None:
            return
        
        self.db = db
        
        if self.raw_content is None:
            return
        
#        if self.raw_content.has_key(TOPO_INPUTS):
        if TOPO_INPUTS in self.raw_content:
            self._parse_input(db, self.raw_content[TOPO_INPUTS])
        
#        if self.raw_content.has_key(TOPO_NODE_TEMPLATES):
        if TOPO_NODE_TEMPLATES in self.raw_content:
            self._parse_node_template(db, self.raw_content[TOPO_NODE_TEMPLATES])
        else:
            logging.warning( 'Topology template: ' + self.name+ ' has NO node templates!')
        
#        if self.raw_content.has_key(TOPO_OUTPUTS):
        if TOPO_OUTPUTS in self.raw_content:
            self._parse_output(db, self.raw_content[TOPO_OUTPUTS])
            
#        if self.raw_content.has_key(TOPO_SUBSTITUION_MAPPINGS):
        if TOPO_SUBSTITUION_MAPPINGS in self.raw_content:
            self._parse_substitution(db, self.raw_content[TOPO_SUBSTITUION_MAPPINGS])
        else:
            self.sub_type = None        
        self._verify_substitution() 
        self._update_function_pointer()   
        
    def _parse_substitution(self, db, sub_sec):
#        if sub_sec.has_key(SUB_NODE_TYPE):
        if SUB_NODE_TYPE in sub_sec:
            self.sub_type = sub_sec[SUB_NODE_TYPE]
#            if db.NODE_TYPES.has_key(self.sub_type):
            if self.sub_type in db.NODE_TYPES:
                db.NODE_TYPES[self.sub_type].mapping_template = self
        else:
            logging.warning( 'substitution mapping section does not have node_type defined')
            return  
                 
#        if sub_sec.has_key(SUB_PROPERTY):
#            sub_prop = sub_sec[SUB_PROPERTY]
#            for sub_prop_name in sub_prop.keys():
#                self.sub_rules.append(SubstitutionRule(SUB_PROPERTY, None, sub_prop_name, sub_prop[sub_prop_name]))
 
        for sub_prop in db.NODE_TYPES[self.sub_type].properties.keys():
#            if self.inputs.has_key(sub_prop):
            if sub_prop in self.inputs:
                self.sub_rules.append(SubstitutionRule(SUB_PROPERTY, None, sub_prop, [SUB_INPUT, sub_prop]))

        for sub_attr in db.NODE_TYPES[self.sub_type].attributes.keys():
#            if self.outputs.has_key(sub_attr):
            if sub_attr in self.outputs:
                self.sub_rules.append(SubstitutionRule(SUB_ATTRIBUTE, None, sub_attr, [SUB_OUTPUT, sub_attr]))
                   
#        if sub_sec.has_key(SUB_CAPABILITY):
        if SUB_CAPABILITY in sub_sec:
            sub_cap = sub_sec[SUB_CAPABILITY]
            for sub_cap_name in sub_cap.keys():
                sub_cap_item = sub_cap[sub_cap_name]
                #standard capability mapping rule
                if type(sub_cap_item) is not dict: 
                    self.sub_rules.append(SubstitutionRule(SUB_CAPABILITY, sub_cap_name, None, sub_cap_item))
                #self-proposed capability mapping rules 
                else: 
#                    if sub_cap_item.has_key(SUB_CAP_ID):
                    if SUB_CAP_ID in sub_cap_item:
                        self.sub_rules.append(SubstitutionRule(SUB_CAPABILITY, sub_cap_name, SUB_CAP_ID, sub_cap_item[SUB_CAP_ID]))
#                    if sub_cap_item.has_key(SUB_CAP_PROPERTY):
                    if SUB_CAP_PROPERTY in sub_cap_item:
                        sub_cap_item_prop = sub_cap_item[SUB_CAP_PROPERTY] 
                        for sub_cap_item_prop_name in sub_cap_item_prop.keys():
                            self.sub_rules.append(SubstitutionRule(SUB_CAPABILITY, sub_cap_name, sub_cap_item_prop_name, sub_cap_item_prop[sub_cap_item_prop_name]))
        
#        if sub_sec.has_key(SUB_REQUIREMENT):
        if SUB_REQUIREMENT in sub_sec:
            sub_req = sub_sec[SUB_REQUIREMENT]
            for sub_req_name in sub_req.keys():
                sub_req_item = sub_req[sub_req_name]
            #standard requirement mapping rule
                if type(sub_req_item) is not dict: 
                    self.sub_rules.append(SubstitutionRule(SUB_REQUIREMENT, sub_req_name, None, sub_req_item))
            #self-proposed requirement mapping rules 
                else: 
#                    if sub_req_item.has_key(SUB_REQ_ID):   
                    if SUB_REQ_ID in sub_req_item:   
                        self.sub_rules.append(SubstitutionRule(SUB_REQUIREMENT, sub_req_name, SUB_REQ_ID, sub_req_item[SUB_REQ_ID]))
                    else:
                        logging.warning( 'Incorrect substitution mapping rules')
    
    def _verify_substitution(self, target_node=None):
        for rule in self.sub_rules:
            rule._update_pointer(target_node, self)       
    
    def _parse_input(self, db, input_sec):
        for input_name in input_sec.keys():
            input_def = PropertyDefinition(input_name, input_sec[input_name])
            input_def._parse_content(db)
            self.inputs[input_name] = PropertyItem(input_def)

    def _parse_output(self, db, output_sec):
        for output_name in output_sec.keys():
            output_def = PropertyDefinition(output_name)
#            output_def._parse_content(db)
            self.outputs[output_name] = PropertyItem(output_def)
#            if output_sec[output_name].has_key('value'):
            if 'value' in output_sec[output_name]:
                self.outputs[output_name]._assign(output_sec[output_name]['value'])
              
    def _parse_node_template(self, db, template_sec):
        self.node_dict = {}
        for name in template_sec.keys():
#            if template_sec[name].has_key(NOD_TYPE):
            if NOD_TYPE in template_sec[name]:
                node_type_name = template_sec[name][NOD_TYPE]
            else:
                logging.warning( 'Invalid template: node section has no type')
                continue
            
#            if db.NODE_TYPES.has_key(node_type_name) is False:
            if node_type_name not in db.NODE_TYPES:
                logging.warning( 'Invalid template: node type: '+ str(node_type_name)+ ' not defined or imported')
                continue
                
            from toscalib.templates.node import Node
            new_node = Node(self, name, db.NODE_TYPES[node_type_name])
            new_node._parse_pre_defined_content(template_sec[name])

            self._add_node(new_node)
        
        for node in iter(self.node_dict.values()):
            node._verify_requirements(self.node_dict)
            node._verify_functions()

            
        self.edge_list = self._create_edges()
        
    def _create_edges(self):
        edges = []
        for node in iter(self.node_dict.values()):
            for req in node.requirements:
                if req.filled is True:
                    new_edge = (node, self.node_dict[req.str_value])
                    logging.debug( 'edge created: '+ new_edge[0].name+ ' --> '+ new_edge[1].name)
                    edges.append(new_edge)
        return edges

    def _update_function_pointer(self):   
        for node in iter(self.node_dict.values()):
            #node._verify_requirements(self.node_dict)
            node._verify_functions()
        for output in iter(self.outputs.values()):
            if output.value is not None:
                output.value._update_function_reference(self)

    def _update_translation_function_pointer(self):
        for node in iter(self.node_dict.values()):
            if node.tran_template is not None:
                node.tran_template._update_function_pointer()
    
    def _update_prefix(self, prefix):
        exist_key_list = list(self.node_dict.keys())
        for node_key in exist_key_list:
            if node_key == 'NO_PREFIX':
                new_node_key = prefix[:len(prefix)-1]
            else:
                new_node_key = prefix + node_key
            node = self.node_dict.pop(node_key)
            node._update_prefix(prefix)
            self.node_dict[new_node_key] = node
            
        exist_key_list = list(self.inputs.keys())
        for item_key in exist_key_list:
            new_item_key = prefix + item_key
            item = self.inputs.pop(item_key)
            item._update_prefix(prefix)
            self.inputs[new_item_key] = item
            
        exist_key_list = list(self.outputs.keys())
        for item_key in exist_key_list:
            ###don't update output name prefix here
            ###temporary solution for cloudify generation
            ###but still need to update pointer for the value
            new_item_key = prefix + item_key
            #item = self.outputs.pop(item_key)
            #item._update_prefix(prefix)
            item = self.outputs[item_key]
            item.value._update_prefix(prefix)   
            item.value._update_function_reference(self)
            #self.outputs[new_item_key] = item
        
        #self._update_function_pointer()

            
    def _update_used_tag_for_translation(self):
        for item in iter(self.inputs.values()):
            item.used = False
        for node_item in iter(self.node_dict.values()):
            for prop_item in iter(node_item.properties.values()):
                prop_item.used = False
            
    def _add_node(self, new_node):
        if new_node is None:
            return
        self.node_dict[new_node.name] = new_node
        
    def _propagate_substitution_value(self):
        converge = False
        while converge is not True:
            converge = True
            for node_item in iter(self.node_dict.values()):
                converge = converge and node_item._propagate_substitution_value() 
            
     
    def _auto_generate_aux_inputs(self):
        for node_name in self.node_dict.keys():
            node = self.node_dict[node_name]
            for prop_name in  node.properties.keys():
                prop_item = node.properties[prop_name]
                if prop_item.value is None or prop_item.filled is False:
                    new_input_name = node_name + '_' + prop_name
#                    while self.inputs.has_key(new_input_name) or self.aux_inputs.has_key(new_input_name):
                    while new_input_name in self.inputs or new_input_name in self.aux_inputs:
                        new_input_name = new_input_name + '_'
                    def_item = copy.deepcopy(prop_item.definition)
                    def_item.name = new_input_name
                    self.aux_inputs[new_input_name] = PropertyItem(def_item)
                    fun_item = {}
                    fun_item['get_input'] = new_input_name
                    prop_item._assign(fun_item)
                    prop_item.value._update_function_reference(self)
                
    def _prepare_node_types(self):
        for node_type in iter(self.db.NODE_TYPES.values()):
            node_type.used = False
            
        for node in iter(self.node_dict.values()):
            node_type = node.type_obj
            while node_type is not None:
                self.db.NODE_TYPES[node_type.name].used = True
                node_type = node_type.parent
    
    def _prepare_node_types_output(self, tags=''):
        self._prepare_node_types()
        node_type = {}
        if 'noexpand' not in tags:
            for node in iter(self.node_dict.values()):
                if node.tran_template is not None: 
                    node_type.update(node.tran_template._prepare_node_types_output(tags))
        if len(node_type) < 1:
            for ntype in iter(self.db.NODE_TYPES.values()):
                if ntype.used is False:
                    continue
                type_content = copy.deepcopy(ntype.raw_content)
                if 'cloudify' in tags:
                    if ntype.name == 'cloudify.nodes.Root':
                        continue
                    
                    type_content.pop('capabilities', None)
                    type_content.pop('requirements', None)
                    type_content.pop('attributes', None)
                else: 
                    if ntype.name == 'tosca.nodes.Root':
                        continue

                node_type[ntype.name] = type_content
                
        return node_type
            
    def _prepare_extra_imports(self, tags):
        if 'cloudify' in tags:
            ret_val = []
            for item in self.extra_imports:
                ret_val += list(item.values())
            return ret_val
        else:
            return self.extra_imports
           
    def _prepare_output(self, tags=''):

        output ={} 
        import_sec = []
        
        if 'cloudify' in tags:
            output[YMO_VERSION]= 'cloudify_dsl_1_3'
            for item in self.extra_imports:
                import_sec += list(item.values()) 
            #import_sec.append('http://www.getcloudify.org/spec/cloudify/3.4/types.yaml')
        else:
            import_sec += self.extra_imports 
            output[YMO_VERSION]= 'tosca_simple_yaml_1_0_0'
        
        if 'import_schema' in tags: 
            output[YMO_IMPORT] = [{'schema': 'schema.yaml'}]
            
        if self.metadata is not None and 'java_sim' not in tags:
            output[YMO_METADATA] = self.metadata
        topo_sec = {}
        node_temp = {}
        for node in iter(self.node_dict.values()):
            node_temp.update(node._prepare_output(tags))
            import_sec += node._prepare_extra_imports(tags)
            
        if 'part' in tags: 
            return node_temp
        
        if len(node_temp.keys())> 0:
            topo_sec[YMO_TOPO_NODE_TEMPLATES] = node_temp
       
        input_sec = {}
        for name in self.inputs.keys():
            input_sec.update(self.inputs[name]._prepare_input_type_output(tags))
        for name in self.aux_inputs.keys():
            input_sec.update(self.aux_inputs[name]._prepare_input_type_output(tags))
        if (len(input_sec.keys())> 0) and 'java_sim' not in tags:
            topo_sec[YMO_TOPO_INPUTS] = input_sec
        output_sec = {}
        for name in self.outputs.keys():
            output_sec.update(self.outputs[name]._prepare_output_type_output())
        if (len(output_sec.keys())> 0) and 'java_sim' not in tags:
            topo_sec[YMO_TOPO_OUTPUTS] = output_sec
            
            
        if 'w_sub' in tags and self.sub_type is not None:
            sub_sec = {}
            sub_sec[YMO_SUB_NODE_TYPE] = self.sub_type
            sub_cap = {}
            sub_req = {}
            for sub_rule in self.sub_rules:
                if sub_rule.type is SUB_CAPABILITY:
                    sub_cap[sub_rule.item] = sub_rule.value
                if sub_rule.type is SUB_REQUIREMENT:
                    sub_req[sub_rule.item] = sub_rule.value
            sub_sec[YMO_SUB_CAPABILITY] = sub_cap
            sub_sec[YMO_SUB_REQUIREMENT] = sub_req
            
            topo_sec[YMO_TOPO_SUBSTITUION_MAPPINGS] = sub_sec 
    
        if 'cloudify' in tags:
            output.update(topo_sec)
        else:
            output[YMO_TOPOLOGY] = topo_sec
        
        if 'nodetype' in tags and 'java_sim' not in tags:
            output[YMO_NODE_TYPE] = self._prepare_node_types_output(tags)
        
        if len(import_sec) > 0:
            output[YMO_IMPORT] = import_sec

        
        return output
        
        
    def _prepare_heat_output(self, parameters_type = {}, parameters_val = {}, stripped = False):
        output = {}
        env_output = {}
        output[YMO_HOT_VERSION] = HOT_VERSION_NUM  

        for input_item in iter(self.inputs.values()):
            out1, out2 = input_item._prepare_heat_output()
            parameters_type.update(out1)
            parameters_val.update(out2)
        resources = {}
        for node in iter(self.node_dict.values()):
            resources.udpate(node._prepare_heat_output(parameters_type, parameters_val))
            
        output[YMO_HOT_PARAMETERS] = parameters_type
        output[YMO_HOT_RESOURCES]  = resources
        env_output[YMO_HOT_PARAMETERS] = parameters_val
        
        if stripped is True: 
            return resources
        else:
            return output, env_output
        
        
    def toJson(self):
        ret_json = {}
        tmp_json = {}
        for node in iter(self.node_dict.values()):
            tmp_json[node.name] = node.toJson()
        ret_json['nodes'] = tmp_json
        ret_json['relations'] = {}
        ret_json['inputs'] = {}
        ret_json['outputs'] = {}
        return ret_json
          