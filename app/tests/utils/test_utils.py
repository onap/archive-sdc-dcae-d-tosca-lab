from toscalib.templates.topology import ToscaTopology
from toscalib.templates.database import ToscaDB
from toscalib.types.node import NodeType
from toscalib.types.capability import CapabilityType


def init_template():
    db = ToscaDB()
    capability_type = CapabilityType('tosca.capabilities.dummy', {'properties': {'capabilityProperty': {'type': 'string'}}})
    sub_capability = CapabilityType('tosca.capabilities.substitute', {'properties': {'capabilityProperty': {'type': 'string'}}})
    capability_type._parse_content(db)
    sub_capability._parse_content(db)
    db._import_capability_type(capability_type)
    db._import_capability_type(sub_capability)
    node_type = NodeType('nodeTypeName', {'id': 'nodeId', 'attributes': {'attributeName': {'type': 'string'}}, 'properties': {'propertyName': {'type': 'string'}}, 'capabilities': {'capabilityName': {'type': 'tosca.capabilities.dummy'}}, 'requirements': [{'dummyRequirement': {'capability': 'tosca.capabilities.dummy'}}]})
    sub_node = NodeType('substituteNodeType', {'id': 'subNodeId', 'properties': {'inputName': {'type': 'string'}}, 'capabilities': {'substituteCapability': {'type': 'tosca.capabilities.substitute'}}, 'requirements': [{'substituteRequirement': {'capability': 'tosca.capabilities.substitute'}}]})
    node_type._parse_content(db)
    sub_node._parse_content(db)
    db._import_node_type(node_type)
    db._import_node_type(sub_node)
    template = ToscaTopology('templateName', None, {'inputs': {'inputName': {'type': 'string'}}, 'node_templates': {'nodeName': {'type': 'nodeTypeName'}, 'node2': {'type': 'nodeTypeName', 'requirements': [{'dummyRequirement': 'nodeName'}]}}})
    template._parse_content(db)
    return template

