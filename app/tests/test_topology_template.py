import unittest
from toscalib.templates.topology import ToscaTopology
from tests.utils.test_utils import init_template


class TestTopologyTemplateMethods(unittest.TestCase):

    def test_update_mapping_template_pointer(self):
        template = init_template()
        sub_sec = {'node_type': 'substituteNodeType', 'capabilities': {'substituteCapability': ['nodeName', 'capabilityName']}}
        sub_type = template.db.NODE_TYPES.get('substituteNodeType')
        self.assertIsNone(sub_type.mapping_template)
        template._parse_substitution(template.db, sub_sec)
        self.assertIsNotNone(sub_type.mapping_template)
        self.assertEqual(sub_type.mapping_template, template)

    def test_parse_substitution(self):
        template = init_template()
        sub_sec = {'node_type': 'substituteNodeType', 'requirements': {'substituteRequirement': ['node2', 'dummyRequirement']}, 'capabilities': {'substituteCapability': ['nodeName', 'capabilityName']}}
        self.assertIsNone(template.sub_type)
        self.assertEqual(len(template.sub_rules), 0)
        template._parse_substitution(template.db, sub_sec)
        self.assertEqual(template.sub_type, 'substituteNodeType')
        self.assertEqual(len(template.sub_rules), 3)

    def test_prepare_output(self):
        template = ToscaTopology('topoName')
        res = template._prepare_output()
        self.assertEqual(res, {'00_YAMLORDER_tosca_definitions_version': 'tosca_simple_yaml_1_0_0', '14_YAMLORDER_topology_template': {}})
        template = init_template()
        res = template._prepare_output()
        self.assertEqual(res, {'00_YAMLORDER_tosca_definitions_version': 'tosca_simple_yaml_1_0_0', '14_YAMLORDER_topology_template': {'11_YAMLORDER_inputs': {'inputName': {'00_YAMLORDER_type': 'string'}},
                               '13_YAMLORDER_node_templates': {'node2': {'00_YAMLORDER_type': 'nodeTypeName', '01_YAMLORDER_properties': {'propertyName': None},'05_YAMLORDER_requirements': [{'dummyRequirement': 'nodeName'}]},
                               'nodeName': {'00_YAMLORDER_type': 'nodeTypeName', '01_YAMLORDER_properties': {'propertyName': None}}}}})

