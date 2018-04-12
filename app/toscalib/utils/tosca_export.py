#Author: Shu Shi
#emaiL: shushi@research.att.com


import yaml
import re
from toscalib.templates.constant import *

def _yaml_export(filename, content):    
    out_str = yaml.safe_dump(content,  default_flow_style=False, width=float("inf"))
    out_str = re.sub(YMO_PREFIX, '', out_str)
    if filename == 'WEB':
        return out_str
    with open(filename, 'w') as outfile:
        outfile.write(out_str)
    return out_str

def _heat_export(filename, content):
    heat_ver = YMO_PREFIX + 'heat_template_version'
    heat_content = content[YMO_TOPOLOGY]
    if heat_content is None:
        heat_content = {}
    heat_content[heat_ver] = '2013-05-23'
#    if heat_content.has_key(YMO_TOPO_OUTPUTS):
    if YMO_TOPO_OUTPUTS in heat_content:
        heat_content.pop(YMO_TOPO_OUTPUTS)
        
    out_str = yaml.dump(heat_content,  default_flow_style=False)
    out_str = re.sub(YMO_TOPO_INPUTS, YMO_PREFIX+'parameters', out_str)
    out_str = re.sub(YMO_TOPO_NODE_TEMPLATES, YMO_PREFIX+'resources', out_str)
    
    out_str = re.sub('get_input', 'get_param', out_str)
    out_str = re.sub('get_attribute', 'get_attr', out_str)
    out_str = re.sub('get_id', 'get_resource', out_str)
    out_str = re.sub('get_property', 'get_attr', out_str)
    out_str = re.sub('type: integer', 'type: number', out_str)
        
    out_str = re.sub(YMO_PREFIX, '', out_str)
    with open(filename, 'w') as outfile:
        outfile.write(out_str)
