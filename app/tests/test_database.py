import unittest
from toscalib.templates.database import ToscaDB
from tests.utils.test_utils import init_template


class TestDatabaseMethods(unittest.TestCase):

    def test_prepare_schema(self):
        db = ToscaDB()
        res = db._prepare_schema()
        self.assertEqual(res, {'00_YAMLORDER_tosca_definitions_version': 'tosca_simple_yaml_1_0_0'})
        db = init_template().db
        res = db._prepare_schema()
        self.assertEqual(res, {'00_YAMLORDER_tosca_definitions_version': 'tosca_simple_yaml_1_0_0', '08_YAMLORDER_capability_types': {'tosca.capabilities.dummy': {'properties': {'capabilityProperty': {'type': 'string'}}},
                               'tosca.capabilities.substitute': {'properties': {'capabilityProperty': {'type': 'string'}}}}, '11_YAMLORDER_node_types': {'nodeTypeName': {'attributes': {'attributeName': {'type': 'string'}},
                               'capabilities': {'capabilityName': {'type': 'tosca.capabilities.dummy'}}, 'id': 'nodeId', 'properties': {'propertyName': {'type': 'string'}}, 'requirements': [{'dummyRequirement': {'capability': 'tosca.capabilities.dummy'}}]},
                               'substituteNodeType': {'capabilities': {'substituteCapability': {'type': 'tosca.capabilities.substitute'}}, 'id': 'subNodeId', 'properties': {'inputName': {'type': 'string'}}, 'requirements': [{'substituteRequirement': {'capability': 'tosca.capabilities.substitute'}}]}}})




