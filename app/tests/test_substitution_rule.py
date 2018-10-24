import unittest
from tests.utils.test_utils import *


class TestSubstitutionRuleMethods(unittest.TestCase):

    def test_update_pointer(self):
        template = init_template()
        sub_template = init_sub_template()
        src_node = sub_template.node_dict.get('nodeName')
        target_node = template.node_dict.get('node2')
        sub_sec = {'node_type': 'nodeTypeName',
                      'requirements': {'substituteRequirement': ['node2', 'dummyRequirement']},
                     'capabilities': {'substituteCapability': ['node2', 'capabilityName']}}
        sub_template._parse_substitution(template.db, sub_sec)
        rules = sub_template.sub_rules
        self.assertIsNone(src_node.properties[rules[0].property].sub_pointer)
        self.assertIsNone(src_node.capabilities[rules[1].item].sub_pointer)
        self.assertIsNone(src_node.capabilities[rules[1].item].properties['capabilityProperty'].sub_pointer)
        self.assertIsNone(src_node.requirements[0].sub_pointer)
        rules[0]._update_pointer(src_node, sub_template)
        self.assertIsNotNone(src_node.properties[rules[0].property].sub_pointer)
        self.assertEqual(src_node.properties[rules[0].property].sub_pointer, sub_template.inputs[rules[0].property])
        rules[1]._update_pointer(src_node, template)
        self.assertIsNotNone(src_node.capabilities[rules[1].item].sub_pointer)
        self.assertIsNotNone(src_node.capabilities[rules[1].item].properties['capabilityProperty'].sub_pointer)
        self.assertEqual(src_node.capabilities[rules[1].item].sub_pointer, target_node.capabilities[rules[1].value[1]])
        self.assertEqual(src_node.capabilities[rules[1].item].properties['capabilityProperty'].sub_pointer, target_node.capabilities[rules[1].value[1]].properties['capabilityProperty'])
        rules[2]._update_pointer(src_node, template)
        self.assertIsNotNone(src_node.requirements[0].sub_pointer)
        self.assertEqual(src_node.requirements[0].sub_pointer, target_node.requirements[0])
