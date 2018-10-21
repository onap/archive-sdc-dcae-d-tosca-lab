#Author: Shu Shi
#emaiL: shushi@research.att.com


from toscalib.templates.node import Node
import copy, logging
#from __builtin__ import False

def _create_new_node(template, type_name, node_name = None):
    db = template.db
#    if db.NODE_TYPES.has_key(type_name) is False:
    if type_name not in db.NODE_TYPES:
        new_name = 'unknown_'+ str(template.node_index)
        template.node_index = template.node_index + 1
        new_node = Node(template, new_name, None)
        logging.debug( 'New node: '+ new_name+ ' added')
        return new_node
    
    if node_name is None:
        new_name = _get_basename(db.NODE_TYPES[type_name].name) + '_' + str(template.node_index)
        template.node_index = template.node_index + 1
    else:
        new_name = node_name
         
    new_node = Node(template, new_name, db.NODE_TYPES[type_name])

    template._add_node(new_node)    
    
    logging.debug( 'New node: '+ new_name+ ' added')
    return new_node
    

def _create_new_template(template, type_name, prefix_name = None):
    db = template.db
    if prefix_name is None:
        prefix = db.TEMPLATES[type_name].name + '_' + str(template.temp_index) + '_'
        template.temp_index = template.temp_index + 1
    elif prefix_name == 'NO_PREFIX':
        prefix = ''
    else:
        prefix = prefix_name
    
    new_temp = copy.deepcopy(db.TEMPLATES[type_name])
    new_temp._update_prefix(prefix)
    new_temp._update_get_node_name()
    new_temp._update_template(template)
    template.inputs.update(new_temp.inputs)
    template.outputs.update(new_temp.outputs)
    template.node_dict.update(new_temp.node_dict)
    return template

def _assign_property_value(node, property_name, value):
#    if node.properties.has_key(property_name) is False:
    if property_name not in node.properties:
        logging.warning( 'No property with name '+ property_name+ ' in the node '+ node.name)
        return False
    return node.properties[property_name]._assign(value)

def _assign_capability_property_value(node, cap_name, prop_name, value):
#    if node.capabilities.has_key(cap_name) is False:
    if cap_name not in node.capabilities:
        logging.warning( 'No capability with name '+ cap_name+ ' in the node '+ node.name)
        return False
    cap_item = node.capabilities[cap_name]
#    if cap_item.properties.has_key(prop_name) is False:
    if prop_name not in cap_item.properties:
        logging.warning( 'No propoerty with name'+ prop_name+ ' in the node '+ node.name+ ' capability '+ cap_name)
        return False
    return cap_item.properties[prop_name]._assign(value)

def _assign_requirement_value(node, requirement_name, value):

    requirement_found = False
    for req in node.requirements:
        if req.name == requirement_name:
            requirement_found = req
            break
    if requirement_found is False:
        logging.warning( 'No requirement with name '+ requirement_name+ ' in the node '+ node.name)
        return False
    if isinstance(value, Node) is False:
        logging.warning( 'Node value should be passed to requirement assignment')
        return False
    else:
        if requirement_found._verify_node(value):
            requirement_found._assign(value)
        else:
            logging.warning( 'Invalid requirement fulfillment for node '+ node.name+ '->'+ requirement_name)
 
    
    return True
 
def _get_basename(name):
    names = name.split(".")
    return names[len(names)-1]       
    