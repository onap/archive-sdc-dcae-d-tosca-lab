'''
Created on Apr 8, 2016

@author: Shu Shi
'''
#!/usr/bin/env python
import web
import json, os, sys
import base64
from toscalib.tosca_workbook import ToscaWorkBook
from toscalib.tosca_builder import ToscaBuilder
from toscalib.templates.database import ToscaDB
from version import __version__


# class fe_get_itembyid:
#     def GET(self):
#         item_id = web.input()
#         print( 'get_itembyid is called with input: ' + str(item_id))
#         web.header('Content-Type', 'application/json')
#         web.header('Access-Control-Allow-Origin', '*')
#         web.header('Access-Control-Allow-Headers', 'Origin, Content-Type, X-Auth-Token')
#         return json.dumps({})
#     
# class fe_get_template:
#     def GET(self):
#         temp_id = web.input()
#         print( 'get_template is called with input: ' + str(temp_id))
#         web.header('Content-Type', 'application/json')
#         web.header('Access-Control-Allow-Origin', '*')
#         web.header('Access-Control-Allow-Headers', 'Origin, Content-Type, X-Auth-Token')
#         return json.dumps({})    
#     
# class fe_get_type:
#     def GET(self):
#         type_name = web.input()
#         print( 'get_type is called with input: ' + str(type_name))
#         web.header('Content-Type', 'application/json')
#         web.header('Access-Control-Allow-Origin', '*')
#         web.header('Access-Control-Allow-Headers', 'Origin, Content-Type, X-Auth-Token')
#         return json.dumps({})    
#     
# class fe_get_compositioncreate:
#     def GET(self):
#         webinput = web.input(cid='unknown_cid')
#         print( 'get_compositioncreate is called with input: ' + str(webinput))
#         cid = webinput.cid
#         
#         workbook_db = ToscaDB()
#         
#         if cid not in workbook_db:
#             workbook_db[cid] = ToscaWorkBook() 
# 
#         ret_json = workbook_db[cid].toJson()
#         ret_json['cid'] = cid
#         
#         web.header('Content-Type', 'application/json')
#         web.header('Access-Control-Allow-Origin', '*')
#         web.header('Access-Control-Allow-Headers', 'Origin, Content-Type, X-Auth-Token')
#         
#         print( 'get_compositioncreate returns:' + ret_json)
#         return json.dumps(ret_json)    
# 
# class fe_get_ice:
#     def GET(self):
#         input_list = web.input()
#         print( 'get_ice is called with input: ' + str(input_list))
#         web.header('Content-Type', 'application/json')
#         web.header('Access-Control-Allow-Origin', '*')
#         web.header('Access-Control-Allow-Headers', 'Origin, Content-Type, X-Auth-Token')
#         return json.dumps({})        
#     
# class fe_post_compimg:
#     def OPTIONS(self):
#         web.header('Access-Control-Allow-Origin', '*')
#         web.header('Access-Control-Allow-Headers', 'Origin, Content-Type, X-Auth-Token')
#         return ''
#     def POST(self):
#         cid = web.input()
#         print( 'post_compimg is called with input: ' + str(cid))
#         try:
#             in_data = json.loads(web.data())
#         except ValueError as e:
#             in_data = web.data()
#         print( 'post_compimg input json data: ' + str(in_data))
#         web.header('Content-Type', 'application/json')
#         web.header('Access-Control-Allow-Origin', '*')
#         web.header('Access-Control-Allow-Headers', 'Origin, Content-Type, X-Auth-Token')
#         return json.dumps({})        
#     
# class fe_post_composition_commit:
#     def OPTIONS(self):
#         web.header('Access-Control-Allow-Origin', '*')
#         web.header('Access-Control-Allow-Headers', 'Origin, Content-Type, X-Auth-Token')
#         return ''
#     def POST(self):
#         cid = web.input()
#         print( 'post_composition_commit is called with input: ' + str(cid))
#         try:
#             in_data = json.loads(web.data())
#         except ValueError as e:
#             in_data = web.data()
#         print( 'post_composition_commit input json data: ' + str(in_data))
#         web.header('Content-Type', 'application/json')
#         web.header('Access-Control-Allow-Origin', '*')
#         web.header('Access-Control-Allow-Headers', 'Origin, Content-Type, X-Auth-Token')
#         return json.dumps({})   
#     
# class fe_post_composition_set_nodepolicies:
#     def OPTIONS(self):
#         web.header('Access-Control-Allow-Origin', '*')
#         web.header('Access-Control-Allow-Headers', 'Origin, Content-Type, X-Auth-Token')
#         return ''
#     def POST(self):
#         cid = web.input()
#         print( 'post_composition_set_nodepolicies is called with input: ' + str(cid))
#         try:
#             in_data = json.loads(web.data())
#         except ValueError as e:
#             in_data = web.data()
#         print( 'post_composition_set_nodepolicies input json data: ' + str(in_data))
#         web.header('Content-Type', 'application/json')
#         web.header('Access-Control-Allow-Origin', '*')
#         web.header('Access-Control-Allow-Headers', 'Origin, Content-Type, X-Auth-Token')
#         return json.dumps({})   
#     
# class fe_post_composition_add_node:
#     def OPTIONS(self):
#         web.header('Access-Control-Allow-Origin', '*')
#         web.header('Access-Control-Allow-Headers', 'Origin, Content-Type, X-Auth-Token')
#         return ''
#     def POST(self):
#         webinput = web.input(cid='unknown_cid')
#         print( 'post_composition_add_node is called with input: ' + str(webinput))
#         cid = webinput.cid
#         try:
#             in_data = json.loads(web.data())
#         except ValueError as e:
#             in_data = web.data()
#         print( 'post_composition_add_node input json data: ' + str(in_data))
#         
#         workbook_db = ToscaDB()
#         if cid not in workbook_db:
#             workbook_db[cid] = ToscaWorkBook() 
# 
#         if 'type' in in_data:
#             if 'name' in in_data['type']:
#                 print( 'add node type: ' + in_data['type']['name'])
#                 new_node = workbook_db[cid]._use(in_data['type']['name'])
#                 new_node.fe_json = in_data
#                 if 'nid' in in_data:
#                     new_node.fe_nid = in_data['nid']
#             else:
#                 print( 'in_data has type but no name')
#         else:
#             print( 'in_data has no type')
#             
#         
#         web.header('Content-Type', 'application/json')
#         web.header('Access-Control-Allow-Origin', '*')
#         web.header('Access-Control-Allow-Headers', 'Origin, Content-Type, X-Auth-Token')
#         
#         return json.dumps(in_data)   
# 
# class fe_post_composition_update_nodes:
#     def OPTIONS(self):
#         web.header('Access-Control-Allow-Origin', '*')
#         web.header('Access-Control-Allow-Headers', 'Origin, Content-Type, X-Auth-Token')
#         return ''
#     def POST(self):
#         webinput = web.input(cid='unknown_cid')
#         print( 'post_composition_update_nodes is called with input: ' + str(webinput))
#         cid = webinput.cid
#         try:
#             in_data = json.loads(web.data())
#         except ValueError as e:
#             in_data = web.data()
#         print( 'post_composition_update_nodes input json data: ' + str(in_data))
#          
#         workbook_db = ToscaDB()
#        
#         if cid not in workbook_db:
#             workbook_db[cid] = ToscaWorkBook() 
# 
#         for in_item in in_data:
#             if 'nid' in in_item :
#                 for node in workbook_db[cid].template.node_dict.itervalues():
#                     if node.fe_nid == in_data['nid']:
#                         node.fe_json.update(in_item)
#                         break
#             else:
#                 print( 'one item has no nid')
# 
#         web.header('Content-Type', 'application/json')
#         web.header('Access-Control-Allow-Origin', '*')
#         web.header('Access-Control-Allow-Headers', 'Origin, Content-Type, X-Auth-Token')
#         return json.dumps({})   
# 
# class fe_post_composition_delete_node:
#     def OPTIONS(self):
#         web.header('Access-Control-Allow-Origin', '*')
#         web.header('Access-Control-Allow-Headers', 'Origin, Content-Type, X-Auth-Token')
#         return ''
#     def POST(self):
#         cid = web.input()
#         print( 'post_composition_delete_nodes is called with input: ' + str(cid))
#         try:
#             in_data = json.loads(web.data())
#         except ValueError as e:
#             in_data = web.data()
#         print( 'post_composition_delete_nodes input json data: ' + str(in_data))
#         web.header('Content-Type', 'application/json')
#         web.header('Access-Control-Allow-Origin', '*')
#         web.header('Access-Control-Allow-Headers', 'Origin, Content-Type, X-Auth-Token')
#         return json.dumps({})   
# 
# class fe_post_composition_add_relation:
#     def OPTIONS(self):
#         web.header('Access-Control-Allow-Origin', '*')
#         web.header('Access-Control-Allow-Headers', 'Origin, Content-Type, X-Auth-Token')
#         return ''
#     def POST(self):
#         cid = web.input()
#         print( 'post_composition_add_relation is called with input: ' + str(cid))
#         try:
#             in_data = json.loads(web.data())
#         except ValueError as e:
#             in_data = web.data()
#         print( 'post_composition_add_relation input json data: ' + str(in_data))
#         web.header('Content-Type', 'application/json')
#         web.header('Access-Control-Allow-Origin', '*')
#         web.header('Access-Control-Allow-Headers', 'Origin, Content-Type, X-Auth-Token')
#         return json.dumps({})   
# 
# class fe_post_composition_delete_relation:
#     def OPTIONS(self):
#         web.header('Access-Control-Allow-Origin', '*')
#         web.header('Access-Control-Allow-Headers', 'Origin, Content-Type, X-Auth-Token')
#         return ''
#     def POST(self):
#         cid = web.input()
#         print( 'post_composition_delete_relation is called with input: ' + str(cid))
#         in_data = json.loads(web.data())
#         print( 'post_composition_delete_relation input json data: ' + str(in_data))
#         web.header('Content-Type', 'application/json')
#         web.header('Access-Control-Allow-Origin', '*')
#         web.header('Access-Control-Allow-Headers', 'Origin, Content-Type, X-Auth-Token')
#         return json.dumps({})   
#     
# class fe_post_composition_add_inputs:
#     def OPTIONS(self):
#         web.header('Access-Control-Allow-Origin', '*')
#         web.header('Access-Control-Allow-Headers', 'Origin, Content-Type, X-Auth-Token')
#         return ''
#     def POST(self):
#         cid = web.input()
#         print( 'post_composition_add_inputs is called with input: ' + str(cid))
#         try:
#             in_data = json.loads(web.data())
#         except ValueError as e:
#             in_data = web.data()
#         print( 'post_composition_add_inputs input json data: ' + str(in_data))
#         web.header('Content-Type', 'application/json')
#         web.header('Access-Control-Allow-Origin', '*')
#         web.header('Access-Control-Allow-Headers', 'Origin, Content-Type, X-Auth-Token')
#         return json.dumps({})  
#     
# class fe_post_composition_add_outputs:
#     def OPTIONS(self):
#         web.header('Access-Control-Allow-Origin', '*')
#         web.header('Access-Control-Allow-Headers', 'Origin, Content-Type, X-Auth-Token')
#         return ''
#     def POST(self):
#         cid = web.input()
#         print( 'post_composition_add_outputs is called with input: ' + str(cid))
#         try:
#             in_data = json.loads(web.data())
#         except ValueError as e:
#             in_data = web.data()
#         print( 'post_composition_add_outputs input json data: ' + str(in_data))
#         web.header('Content-Type', 'application/json')
#         web.header('Access-Control-Allow-Origin', '*')
#         web.header('Access-Control-Allow-Headers', 'Origin, Content-Type, X-Auth-Token')
#         return json.dumps({})  
#     
# class fe_post_composition_set_node_properties:
#     def OPTIONS(self):
#         web.header('Access-Control-Allow-Origin', '*')
#         web.header('Access-Control-Allow-Headers', 'Origin, Content-Type, X-Auth-Token')
#         return ''
#     def POST(self):
#         cid = web.input()
#         print( 'post_composition_set_node_properties is called with input: ' + str(cid))
#         try:
#             in_data = json.loads(web.data())
#         except ValueError as e:
#             in_data = web.data()
#         print( 'post_composition_set_node_properties input json data: ' + str(in_data))
#         web.header('Content-Type', 'application/json')
#         web.header('Access-Control-Allow-Origin', '*')
#         web.header('Access-Control-Allow-Headers', 'Origin, Content-Type, X-Auth-Token')
#         return json.dumps({})  
#     
# class upload:
#     def POST(self, dir):
# #        data = json.loads(web.data())
# #        pyDict = {'one':1,'two':2}
# #        web.header('Content-Type', 'application/json')
# #        return json.dumps(pyDict)
#         return 'OK'
#     
# class import_file:
#     def GET(self):
#         user_data = web.input(dir='')
#         file_dir = user_data.dir
#         if 'name' not in user_data:
#             return 'Error: input has no file name'
#         file_name = user_data.name
#         workbook = ToscaWorkBook()
#         workbook._import( file_dir +'/'+ file_name)
#         return 'OK'
#     
# class use:
#     def GET(self):
#         user_data = web.input()
#         if 'type' not in user_data or 'name' not in user_data:
#             return 'Error: input has no type or name'
#         use_type = user_data['type']
#         name = user_data['name']
#         
#         workbook = ToscaWorkBook()
# 
#         workbook._use(name)
#         return 'OK'
#     
# class assign:
#     def GET(self):
#         user_data = web.input()
#         if 'src_node') is False or user_data.has_key('value') is False:
#             return 'Error: input has no src_node or value'
#         src = user_data.src_node
#         dst_val = user_data.value
#         
#         sub2 = None
#         if user_data.has_key('property'):
#             sub = user_data.property
#         elif user_data.has_key('capability'):
#             sub = user_data.capability
#             if user_data.has_key('capability_property') is False:
#                 return "Error: input has capability but no capability_property"
#             else:
#                 sub2 = user_data.capability_property
#         elif user_data.has_key('requirement'):
#             sub = user_data.requirement
#         
#         workbook = ToscaWorkBook()
# 
#         if sub2 is None:
#             workbook._assign(src, sub, dst_val)
#         else:
#             workbook._assign(src, sub, sub2, dst_val)
# 
#         return 'OK'
#     
# class clear:
#     def GET(self):
#         workbook = ToscaWorkBook()
# 
#         workbook._reset()
#         return 'OK'
# 
# class show:
#     def GET(self):
#         user_data = web.input(level='details')
#         workbook = ToscaWorkBook()
# 
#         if user_data.level == 'details':         
#             return workbook._show_details()
#         else:
#             return workbook._show_abstract()
#     
# class export:
#     def GET(self):
#         user_data = web.input(type='tosca', translation='off')
#         workbook = ToscaWorkBook()
# 
#         if user_data.translation == 'on':
#             if user_data.has_key('translation_lib'):
#                 tran_lib = user_data.translation_lib
#                 workbook._load_translation_db(tran_lib)
# 
#         if user_data.type == 'tosca':
#             return workbook._export_yaml_web()
#         elif user_data.type == 'heat':
#             return 
#         else:
#             return 'Error in export type: only tosca or heat are supported'
        
class translate_template:
    def POST(self):
        try:
            in_data = json.loads(web.data().decode('utf-8'))
        except ValueError as e:
            in_data = web.data()
        print( 'translate_template input json data: ' + str(in_data))
        
        workbook = ToscaWorkBook()
        workbook._import_dir('./data/shared_model/')
#        workbook._load_translation_db('./data/shared_model/')
        
        if 'models' in in_data:
            in_model = in_data['models']
            if type(in_model) != list:
                print( 'models in the input should be a list type')
            for model_entry in in_model:
                for key in ['schema', 'template', 'translate']:
                    if key in model_entry:
                        workbook._import_yml_str(base64.b64decode(model_entry[key]))
        
        if 'template' in in_data:
            in_temp = in_data['template']
            workbook._translate_template_yaml_str(base64.b64decode(in_temp))
            workbook._add_shared_node([{'dcae.capabilities.cdapHost':'cdap_host'}, {'dcae.capabilities.dockerHost': 'docker_host'}, {'dcae.capabilities.composition.host': 'composition_virtual'}])
                        
        ret = workbook._export_yaml_web('cloudify,main')
        print(ret)
        return ret
    
class model_create:
    def POST(self):
        try:
            in_data = json.loads(web.data().decode('utf-8'))
        except ValueError as e:
            in_data = web.data()
        print( 'model_create input json data: ' + str(in_data))
        
        ret = {}
        if 'spec' in in_data:
            spec_str = in_data['spec']
            model_prefix = './data/tosca_model'
            meta_model = './data/meta_model/meta_tosca_schema.yaml'
            
            builder = ToscaBuilder()
        
            builder.import_schema(meta_model)
            builder.import_spec_str(spec_str)
            name = builder.spec_import.name
            builder.create_node_type()

            filename = model_prefix + '/'+ name + '/schema.yaml'
            dirname = os.path.dirname(filename)           
            try:
                os.stat(dirname)
            except:
                os.mkdir(dirname)      
                        
            schema_str = builder.export_schema(model_prefix+'/' + name + '/schema.yaml')
            builder.import_schema(model_prefix+'/' + name + '/schema.yaml')
            builder.create_model(name)
            template_str = builder.export_model(model_prefix+'/' + name + '/template.yaml')
            builder.create_translate(name)
            translate_str = builder.export_translation(model_prefix+'/' + name + '/translate.yaml')
        
            ret['schema'] = (base64.encodestring(bytes(schema_str, 'utf-8'))).decode('utf-8')
            ret['template'] = base64.encodestring(bytes(template_str, 'utf-8')).decode('utf-8')
            ret['translate'] = base64.encodestring(bytes(translate_str, 'utf-8')).decode('utf-8')
        
        return json.dumps(ret)


# Story 318043 - The TOSCA Lab server should expose API for healthcheck with response:
# {
#   "healthCheckComponent": "TOSCA_LAB",
#   "healthCheckStatus": "<UP / DOWN>",
#   "version": "<component version>",
#   "description": "<OK or error description>"
# }
class health_check:
    def GET(self):
        ret = dict()
        ret['healthCheckComponent'] = "TOSCA_LAB"
        ret['healthCheckStatus'] = "UP"
        ret['version'] = __version__
        ret['description'] = "OK"
        print ('TOSCA_LAB got healthcheck request and returns' + str(ret))
        return json.dumps(ret)
        
            
class MyApplication(web.application):
    def run(self, port=8080, *middleware):
        func = self.wsgifunc(*middleware)
        return web.httpserver.runsimple(func, ('0.0.0.0', port))

urls = (
    '/upload/(.*)', 'upload',
    '/import', 'import_file',   #/import?dir=xxx&name=xxx
    '/use', 'use',              #/use?type=xxx&name=xxx
    '/assign', 'assign',        #/assign?src_node=xxx&[property|capability|requrement]=xxx&[capability_property=xxx]&value]xxx
    '/clear', 'clear',          #/clear
    '/show', 'show',            #/show?[level=abstract/details]
    '/export', 'export',         #/export?[type=tosca/heat]&[translation=[on|off]]&[translation_lib=xxx]
    '/itembyid', 'fe_get_itembyid',
    '/template', 'fe_get_template',
    '/type', 'fe_get_type',
    '/compositioncreate', 'fe_get_compositioncreate',
    '/ice.html', 'fe_get_ice',
    '/compimg', 'fe_post_compimg',
    '/composition.commit', 'fe_post_composition_commit',
    '/composition.setnodepolicies', 'fe_post_composition_set_nodepolicies',
    '/composition.addnode', 'fe_post_composition_add_node',
    '/composition.updatenodes', 'fe_post_composition_update_nodes',
    '/composition.deletenode', 'fe_post_composition_delete_node',
    '/composition.addrelation', 'fe_post_composition_add_relation',
    '/composition.deleterelation', 'fe_post_composition_delete_relation',
    '/composition.addinputs', 'fe_post_composition_add_inputs',
    '/composition.addoutputs', 'fe_post_composition_add_outputs',
    '/composition.setnodeproperties', 'fe_post_composition_set_node_properties',
    '/translate', 'translate_template',
    '/model_create', 'model_create',
    '/healthcheck', 'health_check')

application = web.application(urls, globals(), autoreload=False).wsgifunc()


if __name__ == "__main__":
    app = MyApplication(urls, globals())
    if len(sys.argv) > 1:
        app.run(int(sys.argv[1]))
    else:
        app.run()


