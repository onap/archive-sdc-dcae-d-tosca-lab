import unittest
from tests.utils.test_utils import init_template
from toscalib.templates.node import Node


class TestNodeTemplateMethods(unittest.TestCase):

    def test_instantiate_with_type(self):
        template = init_template()
        node = Node(template, 'myNode', template.db.NODE_TYPES.get('nodeTypeName'))
        self.assertEqual(1, len(node.attributes))
        node._instatiateWithType(template.db.NODE_TYPES.get('substituteNodeType'))
        self.assertEqual(0, len(node.attributes))

    def test_parse_pre_defined_content(self):
        template = init_template()
        node = Node(template, 'myNode', template.db.NODE_TYPES.get('nodeTypeName'))
        self.assertIsNone(node.properties.get('propertyName').value)
        prop_sec = {'properties': {'propertyName': 'template_value'}}
        node._parse_pre_defined_content(prop_sec)
        self.assertEqual('template_value', node.properties.get('propertyName').value.value)

    # TODO uncomment after merging ecomp latest code
    # def test_update_get_node_name_property_value(self):
    #     template = init_template()
    #     node = Node(template, 'myNode', template.db.NODE_TYPES.get('nodeTypeName'))
    #     prop_sec = {'properties': {'propertyName': '__GET_NODE_NAME__'}}
    #     node._parse_pre_defined_content(prop_sec)
    #     self.assertEqual('__GET_NODE_NAME__', node.properties.get('propertyName').value.value)
    #     node._update_get_node_name()
    #     self.assertEqual('myNode', node.properties.get('propertyName').value.value)

    # TODO uncomment after merging ecomp latest code
    # def test_update_get_node_name_capability_property_value(self):
    #     template = init_template()
    #     node = Node(template, 'myNode', template.db.NODE_TYPES.get('nodeTypeName'))
    #     prop_sec = {'capabilities': {'capabilityName': {'properties': {'capabilityProperty': '__GET_NODE_NAME__'}}}}
    #     node._parse_pre_defined_content(prop_sec)
    #     self.assertEqual('__GET_NODE_NAME__', node._get_capability_property('capabilityName', 'capabilityProperty').value.value)
    #     node._update_get_node_name()
    #     self.assertEqual('myNode', node._get_capability_property('capabilityName', 'capabilityProperty').value.value)

    def test_update_prefix(self):
        template = init_template()
        node = template.node_dict.get('nodeName')
        prop_sec = {'properties': {'propertyName': {'get_input': 'inputName'}}, 'capabilities': {'capabilityName': {'properties': {'capabilityProperty': {'get_property': ['nodeName', 'propertyName']}}}}}
        node._parse_pre_defined_content(prop_sec)
        node._update_prefix('PREFIX_')
        self.assertEqual('PREFIX_nodeName', node.name)
        self.assertEqual('PREFIX_nodeName', node.id.value.function.extra_data[0])
        self.assertEqual('PREFIX_inputName', node.properties.get('propertyName').value.function.target_property)
        self.assertEqual('PREFIX_nodeName', node._get_capability_property('capabilityName', 'capabilityProperty').value.function.extra_data[0])

    def test_verify_functions(self):
        template = init_template()
        node = template.node_dict.get('nodeName')
        prop_sec = {'properties': {'propertyName': {'get_input': 'inputName'}}, 'capabilities': {'capabilityName': {'properties': {'capabilityProperty': {'get_property': ['nodeName', 'propertyName']}}}}}
        node._parse_pre_defined_content(prop_sec)
        self.assertIsNone(node.properties.get('propertyName').value.function.value_from_item)
        self.assertIsNone(node._get_capability_property('capabilityName', 'capabilityProperty').value.function.value_from_item)
        self.assertIsNone(node._get_capability_property('capabilityName', 'capabilityProperty').value.function.value_from_node)
        node._verify_functions()
        self.assertIsNotNone(node.properties.get('propertyName').value.function.value_from_item)
        self.assertIsNotNone(node._get_capability_property('capabilityName', 'capabilityProperty').value.function.value_from_item)
        self.assertIsNotNone(node._get_capability_property('capabilityName', 'capabilityProperty').value.function.value_from_node)
        self.assertEqual(template.inputs.get('inputName'), node.properties.get('propertyName').value.function.value_from_item)
        self.assertEqual(node.properties.get('propertyName'), node._get_capability_property('capabilityName', 'capabilityProperty').value.function.value_from_item)
        self.assertEqual(node, node._get_capability_property('capabilityName', 'capabilityProperty').value.function.value_from_node)



