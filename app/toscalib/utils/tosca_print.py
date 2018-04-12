#Author: Shu Shi
#emaiL: shushi@research.att.com


LEVEL_NODE_NAME = 1
LEVEL_NODE_DETAILS = 2
LEVEL_NODE_EVERYTHING = 3

def _print_template(template, level=LEVEL_NODE_DETAILS):
    print_str = ''
    if template is None: 
        return print_str
    print_str += 'Nodes:'+ '\n'
    for node in iter(template.node_dict.values()):
        print_str += _print_node(node, level)
    return print_str
 
def _print_node(node, level):
    print_str = ''
    if node is None:
        return
    print_str +=  ' '+ node.name + '\n'
    print_str +=   '    type: '+ node.type+ '\n'
    if level == LEVEL_NODE_DETAILS:
        if len(node.properties) > 0:
            print_str +=   '    properties:' + '\n'
        for prop in iter(node.properties.values()):
            if prop.filled:
                print_str +=   '     '+ prop.name+ ': '+ str(prop.value._get_value()[0])+ '\n'
            else:
                print_str +=   '     '+ prop.name+ ': null'+ '\n'
        if len(node.requirements)> 0:
            print_str +=   '    requirements:'+ '\n'
        for req in node.requirements:
            if req.filled:
                print_str +=   '     '+ req.name+ ': '+ req.value.name+ '\n'
            else:
                print_str +=   '     '+ req.name+ ': null'+ '\n'
        print_str +=   ''+ '\n'
    return print_str
    

def _print_node_types(db):
    print_str =  'Available node types: '+ '\n'
    for name in db.NODE_TYPES.keys():
        print_str +=   name, '\n'
    return print_str

def _print_templates(db):
    print_str =   'Available templates: '+ '\n'
    for name in db.TEMPLATES.keys():
        print_str +=   name, '\n'
    return print_str

def _print_node_type(node_type):
    print_str =   'Node Type Definition: '+ node_type.name+ '\n'
    print_str +=   node_type.raw_content+ '\n'
    return print_str
