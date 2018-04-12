from toscalib.templates.database import ToscaDB
from toscalib.utils import tosca_import, tosca_export, tosca_operate
from toscalib.types.node import NodeType

import copy
import json
import yaml
import uuid
import logging
from toscalib.types.property import PropertyDefinition
from toscalib.types.capability import CapabilityDefinition
from toscalib.types.requirement import RequirementDefinition
from toscalib.types.data import DataType, TYP_INT, TYP_STR, TYP_ANY, TYP_MAP, TYP_FLT, TYP_LIST
from toscalib.templates import topology
from toscalib.templates.topology import ToscaTopology
from toscalib.tosca_workbook import DEFAULT_TEMPLATE_NAME
from distutils.ccompiler import new_compiler
from toscalib.templates.property_item import PropertyItem
from toscalib.templates.substitution_rule import SubstitutionRule
from toscalib.templates.constant import *
from array import array



class SpecImporter(object):
    def __init__(self, ):
        self.name = None
        self.type = None
        self.image = None
        
        self.streams_subscribes = []
        self.streams_publishes = []
        self.service_calls = []
        self.service_provides = []
        
        self.parameters = []
        self.aux_para = {}
        self.policy_para = {}
    
    def _add_parameters(self, para_array, tag):
        for entry in para_array:
            if type(entry) is dict:
                entry['tag'] = tag
                self.parameters.append(entry)
#                if entry.has_key('policy_editable') and entry['policy_editable'] is True:
                if 'policy_editable' in entry and entry['policy_editable'] is True:
#                    if entry.has_key('policy_group'):
                    if 'policy_group'  in entry:
                        policy_group = entry['policy_group']
                    else:
                        policy_group = 'default_group'
#                    if self.policy_para.has_key(policy_group) is False:
                    if policy_group not in self.policy_para:
                        self.policy_para[policy_group] = []
                    self.policy_para[policy_group].append(entry)
                

    def _add_string_para(self, para_name, para_value, tag):
        entry = {}
        entry['name'] = para_name
        entry['value'] = para_value
        entry['type'] = 'string'
        entry['tag'] = tag
        self.parameters.append(entry)                
                
    def _import(self, spec_name, aux_name = None):
        with open(spec_name, 'r') as data_file:
            data = json.load(data_file)
            self._import_spec_str(data)
            
        if aux_name is None:
            return
        
        with open(aux_name) as data_file:
            data = json.load(data_file)
            self._import_aux_str(data)
            
    def _import_spec_str(self, data):

#        if data.has_key('self'):
        if 'self' in data:
            data_sec = data['self']
#            if data_sec.has_key('name'):
            if 'name' in data_sec:
                self.name = data_sec['name']
#            if data_sec.has_key('component_type'):
            if 'component_type' in data_sec:
                self.type = data_sec['component_type']
        
        for key in data.keys():
            if key == 'self':
                continue
            elif key == 'streams':
                data_sec = data[key]
#                if data_sec.has_key('subscribes'):
                if 'subscribes' in data_sec:
                    self.streams_subscribes = data_sec['subscribes']
#                if data_sec.has_key('publishes'):
                if 'publishes' in data_sec:
                    self.streams_publishes = data_sec['publishes']
            elif key == 'services':
                data_sec = data[key]
#                if data_sec.has_key('calls'):
                if 'calls' in data_sec:
                    self.service_calls = data_sec['calls']
#                if data_sec.has_key('provides'):
                if 'provides' in data_sec:
                    self.service_provides = data_sec['provides']
            elif key == 'parameters':
                if self.type == 'docker':
                    self._add_parameters(data[key], 'docker')
                elif self.type == 'cdap':
                    data_sec = data[key]
#                    if data_sec.has_key('app_config'):
                    if 'app_config' in data_sec:
                        self._add_parameters(data_sec['app_config'], 'app_config')
#                    if data_sec.has_key('program_preferences'):
                    if 'program_preferences' in data_sec:
                        prog_pref_sec = data_sec['program_preferences']
                        index = 0
                        for prog_pref_entry in prog_pref_sec:
#                            if prog_pref_entry.has_key('program_type'):
                            if 'program_type' in prog_pref_entry:
                                self._add_string_para('program_type', prog_pref_entry['program_type'], 'program_preferences_'+str(index))
#                            if prog_pref_entry.has_key('program_id'):
                            if 'program_id' in prog_pref_entry:
                                self._add_string_para('program_id', prog_pref_entry['program_id'], 'program_preferences_'+str(index))
#                            if prog_pref_entry.has_key('program_pref'):
                            if 'program_pref' in prog_pref_entry:
                                self._add_parameters(prog_pref_entry['program_pref'], 'program_preferences_'+str(index))
#                    if data_sec.has_key('app_preferences'):
                    if 'app_preferences'  in data_sec:
                        self._add_parameters(data_sec['app_preferences'], 'app_preferences')
            elif key == 'auxilary':
                self.aux_para.update(data[key])
            elif key == 'artifacts':
                for item in data[key]:
#                    if item.has_key('type') and item['type'] == 'jar':
                    if 'type' in item and item['type'] == 'jar':
                        self.image = item['uri']
#                    if item.has_key('type') and item['type'] == 'docker image':
                    if 'type' in item and item['type'] == 'docker image':
                        self.image = item['uri']
                    
    def _import_aux_str(self, data):        
        self.aux_para.update(data)
        
    

class ToscaBuilder(object):
    def __init__(self):
        self.name = None
        self.new_type_name = None
        self.cloudify_type = None
        self.imported_files = []
        self.db = ToscaDB()
        self.spec_import = SpecImporter()
        self.image = None
        self.service_component_type = None
        self.imports = []
        
    def clear_DB(self):
        self.db = ToscaDB()
       
    def import_spec(self, spec_name, aux_name = None):
        self.spec_import._import(spec_name, aux_name)
        self.set_image(self.spec_import.image)
    
    def import_spec_str(self, spec_str):
        self.spec_import._import_spec_str(spec_str)
        self.set_image(self.spec_import.image)
        
            
    def import_schema(self, filename):
        self.db = ToscaDB()
        self.imported_files = []
        self.db = tosca_import._file_import(self.imported_files, filename, self.db)
        
    def import_import(self, filename):
        with open(filename) as data_file:
            try: 
                self.imports = yaml.load(data_file)
            except yaml.YAMLError as exc:
                logging.warning( 'input file can not be loaded as YAML, try JSON')
                try:
                    self.imports = json.load(data_file)
                except:
                    logging.error( 'input file can not be loaded as JSON either')
                    exit(1)
        if type(self.imports) is not list:
            logging.error( 'import file must be a list')
            exit(1)            
        
    def set_image(self, img):
        self.image = img
        
    def set_service_component_type (self, type):
        self.service_component_type = type
        
    
    def _using_dmaap(self):
        for stream in self.spec_import.streams_subscribes:
#            if stream.has_key('type') and stream['type'] in ['message router', 'message_router', 'data router', 'data_router'] :
            if 'type' in stream  and stream['type'] in ['message router', 'message_router', 'data router', 'data_router'] :
                return True
        for stream in self.spec_import.streams_publishes:
#            if stream.has_key('type') and stream['type'] in ['message router', 'message_router', 'data router', 'data_router'] :
            if 'type' in stream and stream['type'] in ['message router', 'message_router', 'data router', 'data_router'] :
                return True
        return False       
    
    def _using_policy(self):
        if len(self.spec_import.policy_para) > 0:
            return True
        else:
            return False     
    
    def create_node_type(self, name = None):
        if self.spec_import.type == "docker":
            parent_type_name = 'tosca.dcae.nodes.dockerApp'
            if self._using_dmaap():
                self.cloudify_type = self.db.NODE_TYPES['dcae.nodes.DockerContainerForComponentsUsingDmaap']
            else:
                self.cloudify_type = self.db.NODE_TYPES['dcae.nodes.DockerContainerForComponents']

        elif self.spec_import.type == 'cdap':
            parent_type_name = 'tosca.dcae.nodes.cdapApp'
            self.cloudify_type = self.db.NODE_TYPES['dcae.nodes.MicroService.cdap']
            
        if name is None:
            self.new_type_name = parent_type_name + '.'+self.spec_import.name
        else:
            self.new_type_name = parent_type_name + '.' + name
            
        new_type = NodeType(self.new_type_name, '')
        new_type.parent_type = parent_type_name;
        new_type.parent = self.db.NODE_TYPES[parent_type_name]
        
#             if new_type.parent is not None:
#                 new_type.properties = copy.deepcopy(new_type.parent.properties)
#                 new_type.attributes = copy.deepcopy(new_type.parent.attributes)
#                 new_type.capabilities = copy.deepcopy(new_type.parent.capabilities)
#                 new_type.requirements = copy.deepcopy(new_type.parent.requ)
#             else:
#                 new_type.properties = {}
#                 new_type.attributes = {}
#                 new_type.capabilities = {}
        
        for para in self.spec_import.parameters:
#             new_prop = PropertyDefinition(para['tag']+'_'+para['name'])
            new_prop = PropertyDefinition(para['name'])
#            if para.has_key('type'):
            if 'type' in para:
                para_key = 'type'
                if para[para_key] == 'integer':
                    new_prop.type = TYP_INT
                elif para[para_key] == 'float':
                    new_prop.type = TYP_FLT
#                elif para[para_key] == 'string' or para.has_key('value') is False:
#                elif para[para_key] == 'string' or 'value'not in para:
                else:
                    new_prop.type = TYP_STR
#                 else:
#                     if type(para['value']) is list:
#                         new_prop.type = TYP_LIST
#                     elif type(para['value']) is dict:
#                         new_prop.type = TYP_MAP
#                     else:
#                         new_prop.type = TYP_STR
                new_prop.type_obj = DataType(new_prop.type)

            new_prop.parsed = True            
            new_prop._create_rawcontent()
            if 'constraints' in para:
                new_prop.raw_content[YMO_PROP_CONSTRAINT] = para['constraints']
                
            new_type.properties[new_prop.name] = new_prop
            
        stream_subscribe_http =     {'type': 'dcae.capabilities.stream.subscribe'}
        stream_dmaap_mr_publish =   {'capability': 'dcae.capabilities.dmmap.topic', 'relationship': 'dcae.relationships.publish_events' }
        stream_dmaap_mr_subscribe = {'capability': 'dcae.capabilities.dmmap.topic', 'relationship': 'dcae.relationships.subscribe_to_events' }
        stream_dmaap_dr_publish =   {'capability': 'dcae.capabilities.dmmap.feed', 'relationship': 'dcae.relationships.publish_files' }
        stream_dmaap_dr_subscribe = {'capability': 'dcae.capabilities.dmmap.feed', 'relationship': 'dcae.relationships.subscribe_to_files' }
        stream_publish_http =       {'capability': 'dcae.capabilities.stream.subscribe', 'relationship': 'dcae.relationships.rework_connected_to' }
        service_provide_content =   {'type': 'dcae.capabilities.service.provide'}
        service_call_content =      {'capability': 'dcae.capabilities.service.provide', 'relationship': 'dcae.relationships.rework_connected_to' }
        policy_req =                {'capability': 'dcae.capabilities.policy', 'relationship': 'cloudify.relationships.depends_on'}
        
        index = 0
        for stream in self.spec_import.streams_subscribes:
#            if stream.has_key('format') is False:
            if 'format' not in stream:
                continue
            if stream['type'] == 'http':
#                 if stream.has_key('config_key'):
#                     new_cap_name = stream['config_key']
#                 else:
#                    new_cap_name = "stream_subscribe_"+str(index)
                new_cap_name = "stream_subscribe_"+str(index)
                new_cap = CapabilityDefinition(new_cap_name, copy.deepcopy(stream_subscribe_http))
                new_cap._parse_content(self.db)
                new_type.capabilities[new_cap.name] = new_cap
                self.cloudify_type.capabilities[new_cap.name] = copy.deepcopy(new_cap)
            elif stream['type'] in ['message router', 'message_router', 'data router', 'data_router'] :
#                 if stream.has_key('config_key'):
#                     new_req_name = stream['config_key']
#                 else:
#                     new_req_name = "stream_subscribe_"+str(index)
                new_req_name = "stream_subscribe_"+str(index)
                tmp_content={}
                if stream['type'] in ['message router', 'message_router'] :
                    tmp_content[new_req_name] = copy.deepcopy(stream_dmaap_mr_subscribe)
                else:
                    tmp_content[new_req_name] = copy.deepcopy(stream_dmaap_dr_subscribe)
                new_req = RequirementDefinition(tmp_content)
                new_req._parse_content(self.db)
                new_type.requirements.append(new_req)
                self.cloudify_type.requirements.append(copy.deepcopy(new_req))
            else:
                continue


#             new_prop = PropertyDefinition(new_cap_name + '_route')
#             new_prop.type = TYP_STR
#             new_prop.type_obj = DataType(new_prop.type)
#             new_type.properties[new_prop.name] = new_prop
            index += 1
        
        index = 0
        for service in self.spec_import.service_provides:
#            if service.has_key('config_key'):
            if 'config_key' in service:
                new_cap_name = service['config_key']
            else:   
                new_cap_name = "service_provide_"+str(index)
            new_cap = CapabilityDefinition(new_cap_name, copy.deepcopy(service_provide_content))
            new_cap._parse_content(self.db)
            new_type.capabilities[new_cap.name] = new_cap
            self.cloudify_type.capabilities[new_cap.name] = copy.deepcopy(new_cap)
            
#             new_prop = PropertyDefinition(new_cap_name + '_service_name')
#             new_prop.type = TYP_STR
#             new_prop.type_obj = DataType(new_prop.type)
#             new_type.properties[new_prop.name] = new_prop
#             new_prop = PropertyDefinition(new_cap_name + '_service_endpoint')
#             new_prop.type = TYP_STR
#             new_prop.type_obj = DataType(new_prop.type)
#             new_type.properties[new_prop.name] = new_prop
#             new_prop = PropertyDefinition(new_cap_name + '_verb')
#             new_prop.type = TYP_STR
#             new_prop.type_obj = DataType(new_prop.type)
#             new_type.properties[new_prop.name] = new_prop
            index += 1
            
        index = 0
        for stream in self.spec_import.streams_publishes:
#            if stream.has_key('format') is False:
            if 'format' not in stream:
                continue
            if stream['type'] == 'http':
#                 if stream.has_key('config_key'):
#                     new_req_name = stream['config_key']
#                 else:
#                     new_req_name = "stream_publish_"+str(index)
                new_req_name = "stream_publish_"+str(index)
                tmp_content={}
                tmp_content[new_req_name] = copy.deepcopy(stream_publish_http)
                new_req = RequirementDefinition(tmp_content)
                new_req._parse_content(self.db)
                new_type.requirements.append(new_req)
                self.cloudify_type.requirements.append(copy.deepcopy(new_req))
            elif stream['type'] in ['message router', 'message_router', 'data router', 'data_router'] :
#                 if stream.has_key('config_key'):
#                     new_req_name = stream['config_key']
#                 else:
#                     new_req_name = "stream_publish_"+str(index)
                new_req_name = "stream_publish_"+str(index)
                tmp_content={}
                if stream['type'] in ['message router', 'message_router'] :
                    tmp_content[new_req_name] = copy.deepcopy(stream_dmaap_mr_publish)
                else:
                    tmp_content[new_req_name] = copy.deepcopy(stream_dmaap_dr_publish)
                new_req = RequirementDefinition(tmp_content)
                new_req._parse_content(self.db)
                new_type.requirements.append(new_req)
                self.cloudify_type.requirements.append(copy.deepcopy(new_req))
            else:
                continue
            
#             new_prop = PropertyDefinition(new_req_name + '_key')
#             new_prop.type = TYP_STR
#             new_prop.type_obj = DataType(new_prop.type)
#             new_type.properties[new_prop.name] = new_prop
            index += 1
            
        index = 0
        for service in self.spec_import.service_calls:
#            if service.has_key('config_key'):
            if 'config_key' in service:
                new_req_name = service['config_key']
            else:   
                new_req_name = "service_call_"+str(index)
            tmp_content={}
            tmp_content[new_req_name] = copy.deepcopy(service_call_content)
            new_req = RequirementDefinition(tmp_content)
            new_req._parse_content(self.db)
            new_type.requirements.append(new_req)
            self.cloudify_type.requirements.append(copy.deepcopy(new_req))
            index += 1
                         
        if self._using_policy() is True:
#             self.create_policy(name)
            for policy_group in self.spec_import.policy_para.keys():
                if policy_group is 'default_group':
                    new_req_name = "policy"
                else:
                    new_req_name = 'policy_' + policy_group
                tmp_content={}
                tmp_content[new_req_name] = copy.deepcopy(policy_req)
                new_req = RequirementDefinition(tmp_content)
                new_req._parse_content(self.db)
                new_type.requirements.append(new_req)
                self.cloudify_type.requirements.append(copy.deepcopy(new_req))

        new_type.parsed = True
        new_type._create_rawcontent()
        self.db.NODE_TYPES[self.new_type_name] = new_type
        self.cloudify_type._create_rawcontent()


    def _create_property(self, entry):
        raw_content = {}
#        if entry.has_key('type'):
        if 'type' in entry:
            raw_content[YMO_PROP_TYPE] = entry['type']
            if entry['type'] == 'number':
                raw_content[YMO_PROP_TYPE] = TYP_INT
        else:
            raw_content[YMO_PROP_TYPE] = TYP_STR
#        if entry.has_key('description') and len(entry['description']) > 0:
        if 'description' in entry and len(entry['description']) > 0:
            raw_content[YMO_PROP_DESCRIPTION] = entry['description']
#         if entry.has_key('value'):
#             raw_content[YMO_PROP_DEFAULT] = entry['value']
#        if entry.has_key('constraints'):
        if 'constraints' in entry:
            raw_content[YMO_PROP_CONSTRAINT] = entry['constraints']
#        if entry.has_key('entry_schema'):
        if 'entry_schema' in entry:
            raw_content[YMO_PROP_ENTRY] = entry['entry_schema']
#        if entry.has_key('policy_schema'):
        if 'policy_schema' in entry:
            raw_content[YMO_PROP_ENTRY] = entry['policy_schema']
            if raw_content[YMO_PROP_TYPE] is TYP_STR:
                raw_content[YMO_PROP_TYPE] = TYP_MAP

        return raw_content

    def _create_data_type(self, name, type, para_array):
        if len(para_array) < 1:
            return None
        
        new_data_type = DataType(name)
        new_data_type.type = type
        new_data_type.properties = {}
        for entry in para_array:
            prop_name = entry['name']
            new_data_type.properties[prop_name] = PropertyDefinition(prop_name)            
            new_data_type.properties[prop_name].raw_content = self._create_property(entry)
        
        new_data_type._create_rawcontent()
        return new_data_type

    def _analyze_data_types(self, para_array, data_types):
        if type(para_array) is not list:
            return
        for entry in para_array:
#            if entry.has_key('entry_schema') is True:
            if 'entry_schema' in entry:
                new_data_name = 'policy.data.' + entry['name']
                ret_para_array = self._analyze_data_types(entry['entry_schema'], data_types)
#                if entry.has_key('type'):
                if 'type' in entry:
                    data_types[new_data_name]=self._create_data_type(new_data_name, entry['type'], ret_para_array)
                else:
                    data_types[new_data_name]=self._create_data_type(new_data_name, TYP_MAP, ret_para_array)
                entry['entry_schema'] = {'type': new_data_name}
#            elif entry.has_key('policy_schema') is True:
            elif 'policy_schema' in entry:
                new_data_name = 'policy.data.' + entry['name']
                ret_para_array = self._analyze_data_types(entry['policy_schema'], data_types)
#                if entry.has_key('type') and entry['type'] is not TYP_STR:
                if 'type' in entry and entry['type'] is not TYP_STR:
                    data_types[new_data_name]=self._create_data_type(new_data_name, entry['type'], ret_para_array)
                else:
                    data_types[new_data_name]=self._create_data_type(new_data_name, TYP_MAP, ret_para_array)
                entry['policy_schema'] = {'type': new_data_name}
            else:
                continue
            
        return para_array

    def create_policy(self):
        parent_type_name = 'policy.nodes.Root'
        name = self.spec_import.name
            
        for policy_group in self.spec_import.policy_para.keys():
            if policy_group is 'default_group':
                new_type_name = 'policy.nodes.'+name
            else:
                new_type_name = 'policy.nodes.'+policy_group
                
            new_type = NodeType(new_type_name, '')
            new_type.parent_type = parent_type_name;
            new_type.parent = self.db.NODE_TYPES[parent_type_name]
            
            self._analyze_data_types(self.spec_import.policy_para[policy_group], self.db.DATA_TYPES)
            
            for entry in self.spec_import.policy_para[policy_group]:
                new_prop = PropertyDefinition(entry['name'])
                new_prop.raw_content = self._create_property(entry)
                new_prop.parsed = True            
                new_type.properties[new_prop.name] = new_prop
    
            new_type.parsed = True
            new_type._create_rawcontent()
            self.db.NODE_TYPES[new_type_name] = new_type

    def create_model(self, name):
        self.template = ToscaTopology(DEFAULT_TEMPLATE_NAME)
        self.template.metadata = {'template_name': name}
        self.template.db = self.db

        node = tosca_operate._create_new_node(self.template, self.new_type_name, name)
#         self._assign_property_value(node, 'image', self.image)
#        self._assign_property_value(node, 'service_component_type', self.spec_import.service_component_type)
        
        topic_index = 0;
        
        for prop_name in ['location_id']:
            fuc_val_list = ['SELF', 'composition', prop_name]
            fuc_val = {}
            fuc_val['get_property'] = fuc_val_list
            self._assign_property_value(node, prop_name, fuc_val)
            
        for para in self.spec_import.parameters:
#            prop_item = node._get_property_item(para['tag']+'_'+para['name'])
            prop_item = node._get_property_item(para['name'])
            def_item = copy.deepcopy(prop_item.definition)
#             input_name = node.name + '_' + def_item.name
#             def_item.name = input_name
#            if para.has_key('value'):
            if 'value' in para:
#                 def_item.default = para['value']
                prop_item._assign(para['value'])
#            if para.has_key('sourced_at_deployment') and para['sourced_at_deployment'] is True:
            if 'sourced_at_deployment' in para and para['sourced_at_deployment'] is True:
                input_name = prop_item.name
                def_item = copy.deepcopy(prop_item.definition)
                def_item.name = input_name
#                if para.has_key('value'):
                if 'value' in para:
                    def_item.default = para['value']
                self.template.aux_inputs[input_name] = PropertyItem(def_item)
                fun_item = {}
                fun_item['get_input'] = input_name
                prop_item._assign(fun_item)
#            if para.has_key('dependency'):
            if 'dependency' in para:
                fun_item = {}
                fun_item['get_property'] = ['SELF', para['dependency']]
                prop_item._assign(fun_item)
            
#             self.template.aux_inputs[input_name] = PropertyItem(def_item)
#             fun_item = {}
#             fun_item['get_input'] = input_name
#             prop_item._assign(fun_item)
        
        if 'connected_broker_dns_name' in node.properties:
            prop_item = node._get_property_item('connected_broker_dns_name')
            if prop_item is not None: 
                input_name = prop_item.name
                def_item = copy.deepcopy(prop_item.definition)
                def_item.name = input_name
                self.template.aux_inputs[input_name] = PropertyItem(def_item)
                fun_item = {}
                fun_item['get_input'] = input_name
                prop_item._assign(fun_item)
            
        index = 0
        for stream in self.spec_import.streams_subscribes:
#            if stream.has_key('format') is False:
            if 'format' in stream is False:
                continue
            if stream['type'] == 'http':
                new_cap_name = "stream_subscribe_"+str(index)
#                if stream.has_key('format'):
                if 'format' in stream:
                    new_cap = node._get_capability_property(new_cap_name, 'format')
                    new_cap._assign(stream['format'])                    
#                if stream.has_key('version'):
                if 'version' in stream:
                    new_cap = node._get_capability_property(new_cap_name, 'version')
                    new_cap._assign(stream['version'])
#                if stream.has_key('route'):
                if 'route' in stream:
                    new_cap = node._get_capability_property(new_cap_name, 'route')
                    new_cap._assign(stream['route'])
#                         new_prop = node._get_property_item(new_cap_name+'_route')
#                         new_prop._assign(stream['route'])
            elif stream['type'] in ['message router', 'message_router', 'data router', 'data_router']:
                new_req_name = "stream_subscribe_"+str(index)
                new_req = node._get_requirement_item_first(new_req_name)
                if stream['type'] in ['message router', 'message_router'] :
                    new_topic_name = 'topic'+ str(topic_index)
                    topic_index += 1
                    new_topic_node = tosca_operate._create_new_node(self.template, 'tosca.dcae.nodes.dmaap.topic', new_topic_name)
                else:
                    new_topic_name = 'feed'+ str(topic_index)
                    topic_index += 1
                    new_topic_node = tosca_operate._create_new_node(self.template, 'tosca.dcae.nodes.dmaap.feed', new_topic_name)
                new_req._assign(new_topic_node)
                for prop_item in iter(new_topic_node.properties.values()):
                    if prop_item.name == 'topic_name':
#                        if stream.has_key('config_key'):
#                            prop_item._assign(stream['config_key']+'-'+str(uuid.uuid4()))
#                            prop_item._assign(stream['config_key'])
#                        else:
                            prop_item._assign('')
                    elif prop_item.name == 'feed_name':
#                        if stream.has_key('config_key'):
#                            prop_item._assign(stream['config_key']+'-'+str(uuid.uuid4()))
#                            prop_item._assign(stream['config_key'])
#                        else:
                            prop_item._assign("")                        
                    elif prop_item.name == 'node_name':
                        prop_item._assign('__GET_NODE_NAME__')
                    elif prop_item.name == 'location':
                        fun_item = {}
                        fun_item['get_property'] = ['SELF', 'composition', 'location_id']
                        prop_item._assign(fun_item)
                    elif prop_item.required == True:
                        input_name = new_topic_name + '_' + prop_item.name
                        def_item = copy.deepcopy(prop_item.definition)
                        def_item.name = input_name
                        self.template.aux_inputs[input_name] = PropertyItem(def_item)
                        fun_item = {}
                        fun_item['get_input'] = input_name
                        prop_item._assign(fun_item)
                if stream['type'] in ['message router', 'message_router'] :
                    for cap_prop_item in iter(new_topic_node._get_capability_item('topic').properties.values()):
                        cap_prop_item._assign({'get_property': ['SELF', cap_prop_item.name]})
                else:
                    for cap_prop_item in iter(new_topic_node._get_capability_item('feed').properties.values()):
                        cap_prop_item._assign({'get_property': ['SELF', cap_prop_item.name]})
                       
            index += 1

        index = 0
        for service in self.spec_import.service_provides:
            new_cap_name = "service_provide_"+str(index)
#            if service.has_key('request'):
            if 'request' in service:
                service_item = service['request']
#                if service_item.has_key('format'):
                if 'format' in service_item:
                    new_cap = node._get_capability_property(new_cap_name, 'request_format')
                    new_cap._assign(service_item['format'])                    
#                if service_item.has_key('version'):
                if 'version' in service_item:
                    new_cap = node._get_capability_property(new_cap_name, 'request_version')
                    new_cap._assign(service_item['version'])
#            if service.has_key('response'):
            if 'response' in service:
                service_item = service['response']
#                if service_item.has_key('format'):
                if 'format' in service_item:
                    new_cap = node._get_capability_property(new_cap_name, 'response_format')
                    new_cap._assign(service_item['format'])                    
#                if service_item.has_key('version'):
                if 'version' in service_item:
                    new_cap = node._get_capability_property(new_cap_name, 'response_version')
                    new_cap._assign(service_item['version'])                
#            if service.has_key('service_name'):
            if 'service_name' in service:
                new_cap = node._get_capability_property(new_cap_name, 'service_name')
                new_cap._assign(service['service_name'])                    
#                     new_prop = node._get_property_item(new_cap_name+'_service_name')
#                     new_prop._assign(service['service_name'])
#            if service.has_key('service_endpoint'):
            if 'service_endpoint' in service:
                new_cap = node._get_capability_property(new_cap_name, 'service_endpoint')
                new_cap._assign(service['service_endpoint'])                    
#                     new_prop = node._get_property_item(new_cap_name+'_service_endpoint')
#                     new_prop._assign(service['service_endpoint'])
#            if service.has_key('verb'):
            if 'verb' in service:
                new_cap = node._get_capability_property(new_cap_name, 'verb')
                new_cap._assign(service['verb'])                    
#                     new_prop = node._get_property_item(new_cap_name+'_verb')
#                     new_prop._assign(service['verb'])
            index += 1

        
        index = 0
        for stream in self.spec_import.streams_publishes:
#            if stream.has_key('format') is False:
            if 'format' not in stream:
                continue
            if stream['type'] == 'http':
                new_req_name = "stream_publish_"+str(index)
                new_req = node._get_requirement_item_first(new_req_name)
                items = []
#                if stream.has_key('format'):
                if 'format' in stream:
                    items.append({'format':[{'equal': stream['format']}]})
#                if stream.has_key('version'):
                if 'version' in stream:
                    items.append({'version':[{'equal': stream['version']}]})
                new_req.filter = {'capabilities': [{'dcae.capabilities.stream.subscribe': {'properties': items}}]}
            elif stream['type'] in ['message router', 'message_router', 'data router', 'data_router']:
                new_req_name = "stream_publish_"+str(index)
                new_req = node._get_requirement_item_first(new_req_name)
                if stream['type'] in ['message router', 'message_router'] :
                    new_topic_name = 'topic'+ str(topic_index)
                    topic_index += 1
                    new_topic_node = tosca_operate._create_new_node(self.template, 'tosca.dcae.nodes.dmaap.topic', new_topic_name)
                else:
                    new_topic_name = 'feed'+ str(topic_index)
                    topic_index += 1
                    new_topic_node = tosca_operate._create_new_node(self.template, 'tosca.dcae.nodes.dmaap.feed', new_topic_name)
                new_req._assign(new_topic_node)
                for prop_item in iter(new_topic_node.properties.values()):
                    if prop_item.name == 'topic_name':
#                        if stream.has_key('config_key'):
#                            prop_item._assign(stream['config_key']+'-'+str(uuid.uuid4()))
#                            prop_item._assign(stream['config_key'])
#                        else:
                            prop_item._assign("")
                    elif prop_item.name == 'feed_name':
#                        if stream.has_key('config_key'):
#                            prop_item._assign(stream['config_key']+'-'+str(uuid.uuid4()))
#                            prop_item._assign(stream['config_key'])
#                        else:
                            prop_item._assign("")                        
                    elif prop_item.name == 'node_name':
                        prop_item._assign('__GET_NODE_NAME__')
                    elif prop_item.name == 'location':
                        fun_item = {}
                        fun_item['get_property'] = ['SELF', 'composition', 'location_id']
                        prop_item._assign(fun_item)
                    else:
                        input_name = new_topic_name + '_' + prop_item.name
                        def_item = copy.deepcopy(prop_item.definition)
                        def_item.name = input_name
                        self.template.aux_inputs[input_name] = PropertyItem(def_item)
                        fun_item = {}
                        fun_item['get_input'] = input_name
                        prop_item._assign(fun_item)
                if stream['type'] in ['message router', 'message_router'] :
                    for cap_prop_item in iter(new_topic_node._get_capability_item('topic').properties.values()):
                        cap_prop_item._assign({'get_property': ['SELF', cap_prop_item.name]})
                else:
                    for cap_prop_item in iter(new_topic_node._get_capability_item('feed').properties.values()):
                        cap_prop_item._assign({'get_property': ['SELF', cap_prop_item.name]})

            index += 1            
        
        if self._using_policy():
            index = 0
            for policy_group in self.spec_import.policy_para.keys():
                if policy_group is 'default_group':
                    req_name = 'policy'
                    policy_type_name = 'policy.nodes.' + self.spec_import.name
                else:
                    req_name = 'policy_'+policy_group
                    policy_type_name = 'policy.nodes.' + policy_group
    
                new_req = node._get_requirement_item_first(req_name)
                policy_node_name = 'policy_' + str(index)
                index += 1
                new_policy_node = tosca_operate._create_new_node(self.template, 'tosca.dcae.nodes.policy', policy_node_name)
                policy_name_item = new_policy_node._get_property_item('policy_name')
                policy_name_item._assign(policy_type_name)
                new_req._assign(new_policy_node)  
    
    
    def create_translate(self, name):
        self.template = ToscaTopology(DEFAULT_TEMPLATE_NAME)
        self.template.metadata = {'template_name': name+"_translate"}
        self.template.db = self.db
        index = 0
        for item in self.imports:
            self.template.extra_imports.append({str(index): item})
            index += 1
        
        if self.new_type_name not in self.db.NODE_TYPES:
            logging.warning( 'error: new node type is not in db: ' + self.new_type_name)
            return
        
        for input_def in iter(self.db.NODE_TYPES[self.new_type_name].properties.values()):
            self.template.inputs[input_def.name] = PropertyItem(input_def)
        
        self.template.sub_type = self.new_type_name
            
        for cap_name in self.db.NODE_TYPES[self.new_type_name].capabilities.keys():
            self.template.sub_rules.append(SubstitutionRule(SUB_CAPABILITY, cap_name, None, [name, cap_name]))
            
        for req_item in self.db.NODE_TYPES[self.new_type_name].requirements:
            if req_item.name == 'host':
                self.template.sub_rules.append(SubstitutionRule(SUB_REQUIREMENT, req_item.name, None, [name, 'host']))
            elif req_item.name == 'composition':
                continue
            else:
                self.template.sub_rules.append(SubstitutionRule(SUB_REQUIREMENT, req_item.name, None, [name, req_item.name]))
                                                            
        if self.cloudify_type is None:
            logging.warning( 'cloudify_type should not be None!')
            return 
        
        node = tosca_operate._create_new_node(self.template, self.cloudify_type.name, name)

        for prop_name in node.properties.keys():
            if prop_name == 'application_config':
                fuc_val = {}
                for entry in self.spec_import.parameters:
                    if entry['tag'] == 'docker':
                        tmp_fun = {}
#                        tmp_fun['get_input'] = entry['tag']+'_' +entry['name']
                        tmp_fun['get_input'] = entry['name']
                        fuc_val[entry['name']] = tmp_fun

                fuc_list = {}
                index = 0
                for stream in self.spec_import.streams_publishes:
                    fuc_unit = {}
                    req_name = "stream_publish_"+str(index)
                    index += 1            
                    if stream['type'] in ['message router', 'message_router']:
                        fuc_unit['aaf_password'] = {'get_property': ['SELF', req_name, 'aaf_password' ]}
                        fuc_unit['aaf_username'] = {'get_property': ['SELF', req_name, 'aaf_username' ]}
                        fuc_unit['dmaap_info'] = {'concat': ['<<', {'get_property': ['SELF', req_name, 'node_name']}, '>>' ]}
                        fuc_unit['type'] = stream['type'].replace(' ', '_')
                    elif stream['type'] in ['data router', 'data_router']:
                        fuc_unit['dmaap_info'] = {'concat': ['<<', {'get_property': ['SELF', req_name, 'node_name']}, '>>' ]}
                        fuc_unit['type'] = stream['type'].replace(' ', '_')
                    else:
                        fuc_unit = {'concat': ['{{', {'get_property': ['SELF', req_name, 'node_name']}, '}}' ]}
                    fuc_list.update({stream['config_key']: fuc_unit})
                fuc_val['streams_publishes'] = fuc_list

                fuc_list = {}
                index = 0
                for stream in self.spec_import.streams_subscribes:
                    fuc_unit = {}
                    req_name = "stream_subscribe_"+str(index)
                    index += 1            
                    if stream['type']  in ['message router', 'message_router']:
                        fuc_unit['aaf_password'] = {'get_property': ['SELF', req_name, 'aaf_password' ]}
                        fuc_unit['aaf_username'] = {'get_property': ['SELF', req_name, 'aaf_username' ]}
                        fuc_unit['dmaap_info'] = {'concat': ['<<', {'get_property': ['SELF', req_name, 'node_name']}, '>>' ]}
                        fuc_unit['type'] = stream['type'].replace(' ', '_')
                    elif stream['type'] in ['data router', 'data_router']:
                        fuc_unit['dmaap_info'] = {'concat': ['<<', {'get_property': ['SELF', req_name, 'node_name']}, '>>' ]}
                        fuc_unit['type'] = stream['type'].replace(' ', '_')
                    else:
                        continue
                    fuc_list.update({stream['config_key']: fuc_unit})
                fuc_val['streams_subscribes'] = fuc_list
                
                fuc_list = {}
                index = 0
                for service in self.spec_import.service_calls:
#                    if service.has_key('config_key'):
                    if 'config_key' in service:
                        req_name = service['config_key']
                    else:
                        req_name = 'service_call_' + str(index)
                    index += 1
#                    if service['type'] == 'http':
                    fuc_unit = {'concat': ['{{', {'get_property': ['SELF', req_name, 'node_name']}, '}}' ]}
#                    if service.has_key('config_key') is False:
                    if 'config_key' not in service:
                        logging.warning( 'service call section must have config_key!')
                        continue
                    fuc_list.update({service['config_key']: fuc_unit})
                fuc_val['services_calls'] = fuc_list

            elif prop_name in ['app_config', 'app_preferences']:
                fuc_val = {}
                for entry in self.spec_import.parameters:
                    if entry['tag'] == prop_name:
                        tmp_fun = {}
#                         tmp_fun['get_input'] = entry['tag']+'_' +entry['name']
                        tmp_fun['get_input'] = entry['name']
                        fuc_val[entry['name']] = tmp_fun
            elif prop_name == 'program_preferences':
                fuc_val = []
                last_tag = None
                for entry in self.spec_import.parameters:
                    if entry['tag'].startswith(prop_name):
                        if entry['tag'] != last_tag:
                            fuc_entry = {}
                            fuc_unit = {}
                            fuc_entry['program_pref'] = fuc_unit
                            last_tag = entry['tag']
                            fuc_val.append(fuc_entry)
                        if entry['name'] in ['program_type', 'program_id']:
                            tmp_fun = {}
#                            tmp_fun['get_input'] = entry['tag']+'_' +entry['name']
                            tmp_fun['get_input'] = entry['name']
                            fuc_entry[entry['name']] = tmp_fun
                        else:
                            tmp_fun = {}
#                            tmp_fun['get_input'] = entry['tag']+'_' +entry['name']
                            tmp_fun['get_input'] = entry['name']
                            fuc_unit[entry['name']] = tmp_fun
            elif prop_name == 'service_endpoints':
                fuc_val = []
                index = 0
                for service in self.spec_import.service_provides:
                    fuc_entry={}
                    cap_prefix = 'service_' + str(index)
#@                    if service.has_key('service_name'):
                    if 'service_name' in service:
                        tmp_fun = {'get_input':cap_prefix + '_service_name'}
                    else:
                        tmp_fun = {}
                    fuc_entry['service_name'] = tmp_fun
#                    if service.has_key('service_endpoint'):
                    if 'service_endpoint' in service:
                        tmp_fun = {'get_input':cap_prefix + '_service_endpoint'}
                    else:
                        tmp_fun = {}
                    fuc_entry['service_endpoint'] = tmp_fun
#                    if service.has_key('verb'):
                    if 'verb' in service:
                        tmp_fun = {'get_input':cap_prefix + '_verb'}
                    else:
                        tmp_fun = {}
                    fuc_entry['endpoint_method'] = tmp_fun
                    fuc_val.append(fuc_entry)
                    index += 1
                    
            elif prop_name == 'docker_config':
                fuc_val = {}
                for key in self.spec_import.aux_para.keys():
                    fuc_val[key] = self.spec_import.aux_para[key]
                    
            elif prop_name == 'connections':
                fuc_val = {}
                fuc_entry = []
                index = 0
                for stream in self.spec_import.streams_publishes:
                    if stream['type'] not in ['message router', 'message_router', 'data router', 'data_router']:
                        continue
                    fuc_unit = {}
                    req_name = "stream_publish_"+str(index)
                    fuc_unit['name'] = {'get_property': ['SELF', req_name, 'node_name' ]}
#                    if stream.has_key('config_key'):
                    if 'config_key' in stream:
                        fuc_unit['config_key'] = stream['config_key']
                    if stream['type'] in ['message router', 'message_router']:
                        fuc_unit['client_role'] = {'get_property': ['SELF', req_name, 'client_role' ]}
                        fuc_unit['aaf_username'] = {'get_property': ['SELF', req_name, 'aaf_username' ]}
                        fuc_unit['aaf_password'] = {'get_property': ['SELF', req_name, 'aaf_password' ]}                        
                    fuc_unit['location'] = {'get_property': ['SELF', req_name, 'location' ]}
                    fuc_unit['type'] = stream['type'].replace(' ', '_')
                    fuc_entry.append(fuc_unit)
                    index += 1
                fuc_val['streams_publishes'] = fuc_entry
                fuc_entry = []
                index = 0
                for stream in self.spec_import.streams_subscribes:
                    if stream['type'] not in ['message router', 'message_router', 'data router', 'data_router']:
                        continue
                    fuc_unit = {}
                    req_name = "stream_subscribe_"+str(index)
                    fuc_unit['name'] = {'get_property': ['SELF', req_name, 'node_name' ]}
#                    if stream.has_key('config_key'):
                    if 'config_key' in stream:
                        fuc_unit['config_key'] = stream['config_key']
                    if stream['type'] in ['message router', 'message_router']:
                        fuc_unit['client_role'] = {'get_property': ['SELF', req_name, 'client_role' ]}
                        fuc_unit['aaf_username'] = {'get_property': ['SELF', req_name, 'aaf_username' ]}
                        fuc_unit['aaf_password'] = {'get_property': ['SELF', req_name, 'aaf_password' ]}                        
                    fuc_unit['location'] = {'get_property': ['SELF', req_name, 'location' ]}
                    fuc_unit['type'] = stream['type'].replace(' ', '_')
                    fuc_entry.append(fuc_unit)
                    index += 1
                fuc_val['streams_subscribes'] = fuc_entry
            
            elif prop_name == 'streams_publishes':
                fuc_val = []
                index = 0
                
                for stream in self.spec_import.streams_publishes:
                    if stream['type'] not in ['message router', 'message_router', 'data router', 'data_router']:
                        continue
                    fuc_unit = {}
                    req_name = "stream_publish_"+str(index)
                    fuc_unit['name'] = {'get_property': ['SELF', req_name, 'node_name' ]}
                    if stream['type'] in ['message router', 'message_router']:
                        fuc_unit['client_role'] = {'get_property': ['SELF', req_name, 'client_role' ]}
                    fuc_unit['location'] = {'get_property': ['SELF', req_name, 'location' ]}
                    fuc_unit['type'] = stream['type'].replace(' ', '_')
                    fuc_val.append(fuc_unit)
                    index += 1

            elif prop_name == 'streams_subscribes':
                fuc_val = []
                index = 0
                
                for stream in self.spec_import.streams_subscribes:
                    if stream['type'] not in ['message router', 'message_router', 'data router', 'data_router']:
                        continue
                    fuc_unit = {}
                    req_name = "stream_subscribe_"+str(index)
                    fuc_unit['name'] = {'get_property': ['SELF', req_name, 'node_name' ]}
                    fuc_unit['location'] = {'get_property': ['SELF', req_name, 'location' ]}
                    if stream['type'] in ['message router', 'message_router']:
                        fuc_unit['client_role'] = {'get_property': ['SELF', req_name, 'client_role' ]}
                    fuc_unit['type'] = stream['type'].replace(' ', '_')
                    fuc_val.append(fuc_unit)
                    index += 1

                
            elif self.spec_import.aux_para is not None and prop_name in self.spec_import.aux_para.keys():
                fuc_val = self.spec_import.aux_para[prop_name]
            elif prop_name == 'service_component_type':
                if self.service_component_type is not None:
                    fuc_val = self.service_component_type
                elif self.spec_import.type == 'docker':
                    fuc_val = self.spec_import.name
                else:
                    fuc_val = 'cdap_app_' + name
            elif prop_name in ['image', 'jar_url']:
                fuc_val = self.image
            else:
                fuc_val = {}
                fuc_val['get_input'] = prop_name
                                
            self._assign_property_value(node, prop_name, fuc_val)
        
        if 'cdap' in self.cloudify_type.name:
            interface_item = node._get_interface_item('cloudify.interfaces.lifecycle')
            op_item = interface_item.operations['create']
            input_item = op_item.inputs['connected_broker_dns_name']
            input_item._assign({'get_input': 'connected_broker_dns_name'})
        
            
    def _assign_property_value(self, node, property_name, value):
#        if node.properties.has_key(property_name) is False:
        if property_name not in node.properties:
            logging.warning( 'No property with name '+ property_name+ ' in the node '+ node.name)
            return False
        return node.properties[property_name]._assign(value)

    def export_policy(self, filename):
        return tosca_export._yaml_export(filename, self.db._prepare_schema())
        
    def export_schema(self, filename):
        return tosca_export._yaml_export(filename, self.db._prepare_schema())
            
    def export_model(self, filename):
        return tosca_export._yaml_export(filename, self.template._prepare_output('main,import_schema'))
    
    def export_translation(self, filename):
        return tosca_export._yaml_export(filename, self.template._prepare_output('main,import_schema,w_sub'))

        
