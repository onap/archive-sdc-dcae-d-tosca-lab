import unittest
from toscalib.templates.value import _is_function
from tests.utils.test_utils import init_template


class TestValueMethods(unittest.TestCase):

    def test_value_is_get_input_function(self):
        value = {'get_input': 'some_input_param'}
        res = _is_function(value)
        self.assertEqual(res.target_property, 'some_input_param')
        self.assertEqual(res.type, 'get_input')

    def test_value_is_simple_string(self):
        value = 'not_a_function'
        res = _is_function(value)
        self.assertIsNone(res)

    def test_value_is_not_valid_function(self):
        value = {'function': 'unknown'}
        res = _is_function(value)
        self.assertIsNone(res)

    def test_value_too_many_functions(self):
        value = {'get_input': 'some_input_param', 'get_property': 'some_value'}
        res = _is_function(value)
        self.assertIsNone(res)

    def test_value_is_concat_function(self):
        value = {'concat': ['first', 'second']}
        res = _is_function(value)
        self.assertEqual(res.type, 'concat')
        self.assertEqual(res.extra_data[0].raw_value, 'first')
        self.assertEqual(res.extra_data[0].type, 'string')
        self.assertEqual(res.extra_data[0].value, 'first')
        self.assertEqual(res.extra_data[1].raw_value, 'second')
        self.assertEqual(res.extra_data[1].type, 'string')
        self.assertEqual(res.extra_data[1].value, 'second')

    def test_invalid_function_values_not_list(self):
        value = {'concat': {'first': 'one', 'second': 'two'}}
        res = _is_function(value)
        self.assertIsNone(res)

    def test_value_is_valid_function(self):
        value = {'get_property': ['first', 'second']}
        res = _is_function(value)
        self.assertEqual(res.type, 'get_property')
        self.assertListEqual(res.extra_data, value['get_property'])

    def test_update_get_input_value_prefix(self):
        value = {'get_input': 'some_input_param'}
        res = _is_function(value)
        self.assertEqual(res.target_property, 'some_input_param')
        res._update_prefix('PREFIX_')
        self.assertEqual(res.target_property, 'PREFIX_some_input_param')

    def test_update_get_property_value_no_prefix(self):
        value = {'get_property': ['NO_PREFIX', 'some_property']}
        res = _is_function(value)
        self.assertEqual(res.extra_data[0], 'NO_PREFIX')
        res._update_prefix('PREFIX_')
        self.assertEqual(res.extra_data[0], 'PREFIX')

    def test_update_concat_get_input_value_prefix(self):
        value = {'concat': [{'get_input': 'some_input_param'}, 'second']}
        res = _is_function(value)
        self.assertEqual(res.extra_data[0].function.target_property, 'some_input_param')
        self.assertEqual(res.extra_data[1].value, 'second')
        res._update_prefix('PREFIX_')
        self.assertEqual(res.extra_data[0].function.target_property, 'PREFIX_some_input_param')
        self.assertEqual(res.extra_data[1].value, 'second')

    def test_update_get_input_function_reference(self):
        template = init_template()
        value = {'get_input': 'inputName'}
        res = _is_function(value)
        self.assertIsNone(res.value_from_item)
        res._update_function_reference(template)
        self.assertEqual(res.value_from_item, template.inputs.get('inputName'))

    # TODO uncomment after merging latest ecomp code
    # def test_update_get_input_function_reference_auto_generate_input(self):
    #     template = init_template()
    #     node = template.node_dict.get('nodeName')
    #     value = {'get_input': 'propertyName'}
    #     res = _is_function(value)
    #     self.assertIsNone(res.value_from_item)
    #     self.assertIsNone(template.inputs.get('nodeName_propertyName'))
    #     self.assertEqual(res.target_property, 'propertyName')
    #     res._update_function_reference(template, node, node.properties.get('propertyName'))
    #     self.assertIsNotNone(res.value_from_item)
    #     self.assertEqual(res.value_from_item, template.inputs.get('nodeName_propertyName'))

    def test_update_get_property_function_reference_node_not_found(self):
        value = {'get_property': ['node_name', 'property_name']}
        res = _is_function(value)
        self.assertIsNone(res.value_from_item)
        res._update_function_reference(init_template())
        self.assertIsNone(res.value_from_item)

    def test_update_get_property_function_reference_self_property(self):
        template = init_template()
        node = template.node_dict.get('nodeName')
        value = {'get_property': ['SELF', 'propertyName']}
        res = _is_function(value)
        self.assertIsNone(res.value_from_node)
        self.assertIsNone(res.value_from_item)
        res._update_function_reference(template, node)
        self.assertEqual(res.value_from_node, node)
        self.assertEqual(res.value_from_item, node.properties.get('propertyName'))

    def test_update_get_property_function_reference_other_node_property(self):
        template = init_template()
        node = template.node_dict.get('nodeName')
        value = {'get_property': ['nodeName', 'propertyName']}
        res = _is_function(value)
        self.assertIsNone(res.value_from_node)
        self.assertIsNone(res.value_from_item)
        res._update_function_reference(template)
        self.assertIsNotNone(res.value_from_node)
        self.assertIsNotNone(res.value_from_item)
        self.assertEqual(res.value_from_node, node)
        self.assertEqual(res.value_from_item, node._get_property_item('propertyName'))

    def test_update_get_property_function_reference_capability_property(self):
        template = init_template()
        value = {'get_property': ['nodeName', 'capabilityName', 'capabilityProperty']}
        res = _is_function(value)
        self.assertIsNone(res.value_from_node)
        self.assertIsNone(res.value_from_item)
        res._update_function_reference(template)
        self.assertIsNotNone(res.value_from_node)
        self.assertIsNotNone(res.value_from_item)
        node = template.node_dict.get('nodeName')
        self.assertEqual(res.value_from_node, node)
        self.assertEqual(res.value_from_item, node._get_capability_property('capabilityName', 'capabilityProperty'))

    def test_update_get_property_function_reference_requirement_capability_property(self):
        template = init_template()
        value = {'get_property': ['node2', 'dummyRequirement', 'capabilityProperty']}
        res = _is_function(value)
        self.assertIsNone(res.value_from_node)
        self.assertIsNone(res.value_from_item)
        res._update_function_reference(template)
        self.assertIsNotNone(res.value_from_node)
        self.assertIsNotNone(res.value_from_item)
        node = template.node_dict.get('nodeName')
        self.assertEqual(res.value_from_node, node)
        self.assertEqual(res.value_from_item, node._get_capability_property('capabilityName', 'capabilityProperty'))

    def test_update_get_property_function_reference_requirement_target_property(self):
        template = init_template()
        value = {'get_property': ['node2', 'dummyRequirement', 'propertyName']}
        res = _is_function(value)
        self.assertIsNone(res.value_from_node)
        self.assertIsNone(res.value_from_item)
        res._update_function_reference(template)
        self.assertIsNotNone(res.value_from_node)
        self.assertIsNotNone(res.value_from_item)
        node = template.node_dict.get('nodeName')
        self.assertEqual(res.value_from_node, node)
        self.assertEqual(res.value_from_item, node._get_property_item('propertyName'))

    def test_update_get_attribute_function_reference_invalid_params(self):
        value = {'get_attribute': ['no_such_node', 'some_attribute']}
        res = _is_function(value)
        res._update_function_reference(init_template())
        self.assertIsNone(res.value_from_node)
        self.assertIsNone(res.value_from_item)

    def test_update_get_attribute_function_self_attribute(self):
        template = init_template()
        node = template.node_dict.get('nodeName')
        value = {'get_attribute': ['SELF', 'attributeName']}
        res = _is_function(value)
        self.assertIsNone(res.value_from_node)
        self.assertIsNone(res.value_from_item)
        res._update_function_reference(template, node)
        self.assertEqual(res.value_from_node, node)
        self.assertEqual(res.value_from_item, node.attributes.get('attributeName'))

    def test_update_get_attribute_function_node_id_attribute(self):
        template = init_template()
        node = template.node_dict.get('nodeName')
        value = {'get_attribute': ['SELF', 'id']}
        res = _is_function(value)
        self.assertIsNone(res.value_from_node)
        self.assertIsNone(res.value_from_item)
        res._update_function_reference(template, node)
        self.assertEqual(res.value_from_node, node)
        self.assertEqual(res.value_from_item, node.id)

    def test_update_get_attribute_function_other_node_id_attribute(self):
        template = init_template()
        node = template.node_dict.get('nodeName')
        value = {'get_attribute': ['nodeName', 'id']}
        res = _is_function(value)
        self.assertIsNone(res.value_from_node)
        self.assertIsNone(res.value_from_item)
        res._update_function_reference(template)
        self.assertEqual(res.value_from_node, node)
        self.assertEqual(res.value_from_item, node.id)

    def test_update_get_attribute_function_requirement_target_attribute(self):
        template = init_template()
        node = template.node_dict.get('nodeName')
        value = {'get_attribute': ['node2', 'dummyRequirement', 'attributeName']}
        res = _is_function(value)
        self.assertIsNone(res.value_from_node)
        self.assertIsNone(res.value_from_item)
        res._update_function_reference(template)
        self.assertEqual(res.value_from_node, node)
        self.assertEqual(res.value_from_item, node.attributes.get('attributeName'))

    def test_update_concat_function_reference(self):
        template = init_template()
        node = template.node_dict.get('nodeName')
        value = {'concat': [{'get_attribute': ['nodeName', 'id']}, 'second']}
        res = _is_function(value)
        self.assertIsNone(res.extra_data[0].function.value_from_node)
        res._update_function_reference(template)
        self.assertIsNotNone(res.extra_data[0].function.value_from_node)
        self.assertIsNotNone(res.extra_data[0].function.value_from_item)
        self.assertEqual(res.extra_data[0].function.value_from_node, node)
        self.assertEqual(res.extra_data[0].function.value_from_item, node.id)

