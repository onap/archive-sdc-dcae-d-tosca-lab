from toscalib.templates.constant import *
from toscalib.types.node import NodeType
from toscalib.templates.requirement_item import RequirementItem
from toscalib.templates.property_item import PropertyItem
from toscalib.templates.capability_item import CapabilityItem
from toscalib.utils import tosca_import, tosca_heat

import copy, re, logging
from toscalib.templates.interface_item import InterfaceItem




class Node(object):
    def __init__(self, template, node_name, node_type):
        self.template = template
        self.name = node_name
        self.id = PropertyItem(node_type.id)   
        self_id_str = {} 
        self_id_str['get_attribute']= [node_name, 'id'] 
        self.id._assign(self_id_str)
        
        self.mapping_template = None
        self.tran_template = None
        
        self.fe_json = None
        self.fe_nid = None
         
        if node_type is None:
            logging.warning( 'Empty node type')
            return
        elif isinstance(node_type, NodeType) is False:
            logging.warning( 'Invalid NodeType passed to Node: '+ node_name+ 'construction')
            return
        else:
            self._instatiateWithType(node_type)

#Instantiate the node type, when substitution mapping is attached, create the new template for it
    def _instatiateWithType(self, node_type):
        self.type = node_type.name
        self.type_obj = node_type
        
        self.properties = {}
        for prop in node_type.properties.keys():
            self.properties[prop] = PropertyItem(node_type.properties[prop])
            
        self.attributes = {}
        for attr in node_type.attributes.keys():
            self.attributes[attr] = PropertyItem(node_type.attributes[attr])
        
        self.requirements = []
        for req in node_type.requirements:
            self.requirements.append(RequirementItem(req))
            
        self.capabilities = {}
        for cap in node_type.capabilities.keys():
            self.capabilities[cap] = CapabilityItem(node_type.capabilities[cap])
            
        self.interfaces = {}
        for intf in node_type.interfaces.keys():
            self.interfaces[intf] = InterfaceItem(node_type.interfaces[intf])

#         if node_type.mapping_template is not None:
#             from toscalib.templates.topology import  ToscaTopology
#             self.mapping_template = copy.deepcopy(node_type.mapping_template)
#             self.mapping_template._update_prefix(self.name + '_')
#             self.mapping_template._verify_substitution(self)
# #             for sub_rule in node_type.mapping_template.sub_rules:
# #                 sub_rule._update_pointer(self, self.mapping_template)

        self._update_parent_node()
        
#used to parse node template structure written in a template
#Assign values if needed
#For requirement fulfillment, add pending mode to check whether the value is a node template or type      
    def _parse_pre_defined_content(self, content):
#        if content.has_key(NOD_PROPERTIES):
        if NOD_PROPERTIES in content:
            prop_sec = content[NOD_PROPERTIES]
            if prop_sec is not None:
                for prop_name in prop_sec.keys():
                    prop_item = self._get_property_item(prop_name)
                    if prop_item is not None:
                        prop_item._assign(prop_sec[prop_name])
#                         if prop_sec[prop_name] == '__GET_NODE_NAME__':
#                             prop_item._assign(self.name)
                        
#        if content.has_key(NOD_REQUIREMENTS):
        if NOD_REQUIREMENTS in content:
            req_sec = content[NOD_REQUIREMENTS]
            if req_sec is not None:                
                for req in req_sec:
                    req_item_name, req_item_value = tosca_import._parse_requirement_name_and_value(req)
#TODO: the same requirement name can only appear once!!
                    req_item = self._get_requirement_item_first(req_item_name)
                    if req_item is not None:
                        req_item._parse_pre_defined_content(req_item_value) 
                    else:
                        logging.warning( 'Requirement '+ req_item_name +'not defined in Node '+ self.name + ' of type '+ self.type)

#        if content.has_key(NOD_CAPABILITIES):
        if NOD_CAPABILITIES in content:
            cap_sec = content[NOD_CAPABILITIES]
            if cap_sec is not None:
                for cap_name in cap_sec.keys():
                    cap_item = self._get_capability_item(cap_name)
                    if cap_item is not None: 
                        cap_item._parse_pre_defined_content(cap_sec[cap_name])
                        
#        if content.has_key(NOD_INTERFACES):
        if NOD_INTERFACES in content:
            interface_sec = content[NOD_INTERFACES]
            if interface_sec is not None:
                for interface_name in interface_sec.keys():
                    interface_item = self._get_interface_item(interface_name)
                    if interface_item is not None:
                        interface_item._parse_pre_defined_content(interface_sec[interface_name])
                    else:
                        self.interfaces[interface_name] = InterfaceItem(None, interface_name, interface_sec[interface_name])  
         
        self._update_parent_node()   
    
    def _get_property_item(self, prop_name):
#        if self.properties.has_key(prop_name):
        if prop_name in self.properties:
            return self.properties[prop_name]
        else:
            logging.warning('Node: '+ self.name+ ' of type: '+ self.type+ ' has no property: '+ prop_name)
            return None

    def _get_attribute_item(self, attr_name):
#        if self.attributes.has_key(attr_name):
        if attr_name in self.attributes:
            return self.attributes[attr_name]
        else:
            logging.warning('Node: '+ self.name+ ' of type: '+ self.type+ ' has no attribute: '+ attr_name)
            return None
        
    def _get_interface_item(self, interface_name):
#        if self.interfaces.has_key(interface_name):
        if interface_name in self.interfaces:
            return self.interfaces[interface_name]
        else:
            logging.warning( 'Node: '+ self.name+ ' of type: '+ self.type+ ' has no interface: '+ interface_name)
            return None    
        
    def _get_capability_item(self, cap_name):
#        if self.capabilities.has_key(cap_name):
        if cap_name in self.capabilities:
            return self.capabilities[cap_name]
        else:
            #logging.debug('Node: '+ self.name+ ' of type: '+ self.type+ ' has no capability: '+ cap_name)
            return None
        
    def _get_capability_property(self, cap_name, prop_name):
        cap_item = self._get_capability_item(cap_name)
        if cap_item is not None:
            return cap_item._get_property_item(prop_name)
        else:
            #logging.debug( 'Node: '+ self.name+ ' of type: '+ self.type+ ' has no capability: '+ cap_name)
            return None
        
    def _get_requirement_item_first(self, req_name):
        for req_item in self.requirements:
            if req_item.name == req_name:
                return req_item
        logging.warning( 'Node: '+ self.name+ ' of type: '+ self.type+ ' has no requirement: '+ req_name)
        return None
        
    def _verify_requirements(self, node_dict):
        for req in self.requirements:
            req._verify_requirement(node_dict)
     
    def _verify_functions(self, parent_temp = None):
        if parent_temp is not None:
            temp = parent_temp
        else:
            temp = self.template
        if self.id.value is not None:
            self.id.value._update_function_reference(temp, self, self.id)
        for prop_item in iter(self.properties.values()):
            if prop_item.value is not None:
                prop_item.value._update_function_reference(temp, self, prop_item)     
        for cap_item in iter(self.capabilities.values()):
            for cap_item_prop in iter(cap_item.properties.values()):
                if cap_item_prop.value is not None:
                    cap_item_prop.value._update_function_reference(temp, self, cap_item_prop)  
        for interface_item in iter(self.interfaces.values()):
            for interface_item_input in iter(interface_item.inputs.values()):
                if interface_item_input.value is not None: 
                    interface_item_input.value._update_function_reference(temp, self, interface_item_input)
            for operation_item in iter(interface_item.operations.values()):
                for input_item in iter(operation_item.inputs.values()):
                    if input_item.value is not None:
                        input_item.value._update_function_reference(temp, self, input_item)
    
    def _update_parent_node(self):
        for prop in iter(self.properties.values()):
            prop._update_parent_node(self)
        for cap in iter(self.capabilities.values()):
            cap._update_parent_node(self)
        for req in self.requirements:
            req._update_parent_node(self)
        for interface in iter(self.interfaces.values()):
            interface._update_parent_node(self)
    
    def _update_get_node_name(self):
        for prop_item in iter(self.properties.values()):
            if prop_item.value is not None:
                if prop_item.value.value == '__GET_NODE_NAME__':
                    prop_item._assign(self.name)
                    
        for cap_item in iter(self.capabilities.values()):
            for cap_item_prop in iter(cap_item.properties.values()):
                if cap_item_prop.value is not None:
                    if cap_item_prop.value.value == '__GET_NODE_NAME__':
                        cap_item_prop._assign(self.name)    
    
    def _update_template(self, template):
        self.template = template
                
    def  _update_prefix(self, prefix):
        if self.name == 'NO_PREFIX':
            self.name = prefix[:len(prefix)-1]
        else:
            self.name = prefix + self.name
        self.id.value._update_prefix(prefix)
        
        for prop_item in iter(self.properties.values()):
            if prop_item.value is not None:
                prop_item.value._update_prefix(prefix)
        for cap_item in iter(self.capabilities.values()):
            for cap_item_prop in iter(cap_item.properties.values()):
                if cap_item_prop.value is not None:
                    cap_item_prop.value._update_prefix(prefix)
        for interface_item in iter(self.interfaces.values()):
            for interface_item_input in iter(interface_item.inputs.values()):
                if interface_item_input.value is not None: 
                    interface_item_input.value._update_prefix(prefix)
            for operation_item in iter(interface_item.operations.values()):
                for input_item in iter(operation_item.inputs.values()):
                    if input_item.value is not None:
                        input_item.value._update_prefix(prefix)
       
        for req in self.requirements:
            req._update_prefix(prefix)
    
        self._update_parent_node()

    def _verify_req_node(self, req_type, req_cap, req_filter):
        if req_type is not None and self.type_obj._verify_req_type(req_type) is False:
            logging.warning( 'Type matching failed')
            return False

        if req_cap is not None:
            cap_found = None
            for cap_item in iter(self.capabilities.values()):
                if cap_item._validate_capability(req_cap) is True:
                    cap_found = cap_item
                    break
            if cap_found is None:
                logging.warning( 'Capability matching failed')
                return False
            
        return self._verify_node_filter(req_filter)
    
    def _verify_node_filter(self, req_filter):
        return True
    
    def _propagate_substitution_value(self):
        converge = True
        for prop_item in iter(self.properties.values()):
            converge = converge and prop_item._propagate_substitution_value()
        for req_item in self.requirements:
            converge = converge and req_item._propagate_substitution_value()
        for cap_item in iter(self.capabilities.values()):
            converge = converge and cap_item._propagate_substitution_value()
        for attr_item in iter(self.attributes.values()):
            converge = converge and attr_item._propagate_attr_substitution_value()

        
        if self.mapping_template is not None:
            self.mapping_template._propagate_substitution_value()
        if self.tran_template is not None:
            self.tran_template._propagate_substitution_value()
        
        return converge
    
    def _prepare_extra_imports(self, tags = ''):
        if 'noexpand' in tags:
            return []
        if self.tran_template is not None:
            return self.tran_template._prepare_extra_imports(tags)
        if self.mapping_template is not None:
            return self.mapping_template._prepare_extra_imports(tags)
        return []
    
    def _prepare_output(self, tags=''):
        if 'noexpand' not in tags:
            newtags = tags.replace('main', 'part')
            if self.tran_template is not None:
                return self.tran_template._prepare_output(newtags)
            if self.mapping_template is not None:
                return self.mapping_template._prepare_output(newtags)
        output = {}
        if 'heat' in tags:
            heat_type = re.sub('tosca.heat.', '', self.type)
            heat_type = re.sub('\.', '::', heat_type)
            output[YMO_NOD_TYPE] = heat_type
        else:
            output[YMO_NOD_TYPE] = self.type
        prop_out = {}
        for prop in self.properties.keys():
            prop_item = self.properties[prop]
#             if prop_item.required is False and prop_item.used is not True and prop_item.filled is not True:
            if prop_item.required is False and prop_item.filled is not True:
                continue
            if prop_item.filled is not True or prop_item.value is None:
                prop_value = None
            else:
                prop_value = prop_item.value._get_value(tags)[0]
            if prop_item.required is False and prop_value in [None, [], {}]:
                continue
            else:            
                prop_out[prop] = prop_value
        cap_out={}
        for cap in iter(self.capabilities.values()):
            cap_item = {}
            for cap_prop in iter(cap.properties.values()):
                if cap_prop.filled is True:
                    cap_item[cap_prop.name] = cap_prop.value._get_value(tags)[0]
            if len(cap_item) > 0:
                cap_out[cap.name] = {'properties': cap_item}

        req_out = []            
        for req in self.requirements:
            if req.filled is True:
                req_item = dict()
                if 'cloudify' in tags:
                    if req.relationship is not None :
                        req_item['type'] = req.relationship
                    else:                    
                        req_item['type'] = 'cloudify.relationships.connected_to'
                    req_item['target'] = req.str_value
                else:
                    req_item[req.name] = req.str_value
                req_out.append(req_item)
            elif req.filter is not None and 'cloudify' not in tags:
                req_item = {}
                if req.req_capability is not None:
                    req_item[YMO_REQ_CAPABILITY] = req.req_capability
                if req.req_type is not None:
                    req_item[YMO_REQ_NODE] = req.req_type
                if req.relationship is not None:
                    req_item[YMO_REQ_RELATIONSHIP] = req.relationship
                req_item[YMO_REQ_FILTER] = req.filter
                req_out.append({req.name:req_item})
        int_out = {}
        for interface_name in self.interfaces.keys():
            int_out[interface_name] = self.interfaces[interface_name]._prepare_output(tags) 
            
        if len(prop_out) > 0:
            output[YMO_NOD_PROPERTIES]=prop_out
        if len(req_out) > 0 and 'java_sim' not in tags:
            if 'cloudify' in tags:
                output[YMO_NOD_RELATIONSHIPS] = req_out
            else:
                output[YMO_NOD_REQUIREMENTS] = req_out
        if len(cap_out) > 0 and 'cloudify' not in tags:
            output[YMO_NOD_CAPABILITIES] = cap_out
        if len(int_out) > 0 :
            output[YMO_NOD_INTERFACES] = int_out
        final_out = {}
        final_out[self.name] = output
        return final_out
                   
    def _prepare_heat_output(self, parameters_type, parameters_val):
        if self.mapping_template is not None:
            return self.mapping_template._prepare_heat_output(parameters_type, parameters_val, True)
        else:
            if tosca_heat._type_validate(self.type) is not True:
                return None
            output = {}
            output[YMO_NOD_TYPE] = tosca_heat._type_translate(self.type)
            prop_out = {}
            for prop_item in iter(self.properties.values()):
                if prop_item.filled:
                    prop_out[prop_item.name] = prop_item.value
                else:
                    input_name = self.name + '_' + prop_item.name
                    prop_out[prop_item.name] = '{ get_param: ' + input_name + ' }'
                    input_type = {}
                    input_type[input_name] = prop_item.type
                    input_val = {}
                    input_val[input_name] = prop_item.value
                    parameters_type.update(input_type)
                    parameters_val.udpate(input_val)
            if len(prop_out) > 0:
                output[YMO_NOD_PROPERTIES] = prop_out
            final_out = {}
            final_out[self.name] = output
            return final_out
             
             
    def toJson(self):
        return self.fe_json   