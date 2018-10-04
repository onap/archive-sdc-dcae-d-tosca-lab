import unittest
from toscalib.templates.value import _is_function
from tests.utils.test_utils import init_template


class TestCalculateFunctionValueMethods(unittest.TestCase):

    def test_get_input_function_representation(self):
        value = {'get_input': 'inputName'}
        func = _is_function(value)
        self.assertEqual(func.target_property, 'inputName')
        res = func._get_function_representation()
        self.assertEqual(res, value)

    def test_get_self_property_function_representation(self):
        value = {'get_property': ['SELF', 'propertyName']}
        func = _is_function(value)
        self.assertIsNotNone(func.extra_data)
        self.assertIsNone(func.value_from_node)
        res = func._get_function_representation()
        self.assertEqual(res, value)
        template = init_template()
        node = template.node_dict.get('nodeName')
        func._update_function_reference(template, node)
        self.assertIsNotNone(func.value_from_node)
        res = func._get_function_representation()
        self.assertEqual(res, {'get_property': ['nodeName', 'propertyName']})

    def test_get_attribute_function_representation(self):
        value = {'get_attribute': ['SELF', 'attributeName']}
        func = _is_function(value)
        self.assertIsNotNone(func.extra_data)
        self.assertIsNone(func.value_from_node)
        res = func._get_function_representation()
        self.assertEqual(res, value)
        template = init_template()
        node = template.node_dict.get('nodeName')
        func._update_function_reference(template, node)
        self.assertIsNotNone(func.value_from_node)
        res = func._get_function_representation()
        self.assertEqual(res, {'get_attribute': ['nodeName', 'attributeName']})

    def test_get_id_attribute_function_representation(self):
        template = init_template()
        node = template.node_dict.get('nodeName')
        value = {'get_attribute': ['SELF', 'id']}
        func = _is_function(value)
        func._update_function_reference(template, node)
        self.assertIsNotNone(func.value_from_node)
        res = func._get_function_representation()
        self.assertEqual(res, {'get_attribute': ['nodeName', 'id']})
        res = func._get_function_representation('heat')
        self.assertEqual(res, {'get_id': 'nodeName'})

    def test_calculate_concat_function_result(self):
        template = init_template()
        node = template.node_dict.get('nodeName')
        value = {'concat': [{'get_attribute': ['SELF', 'id']}, {'concat': [{'get_property': ['SELF', 'propertyName']}, 'third', '4']}]}
        func = _is_function(value)
        res = func._calculate_function_result()
        self.assertEqual(res, (value, 2))
        func._update_function_reference(template, node)
        res = func._calculate_function_result()
        expected = {'concat': [{'get_attribute': ['nodeName', 'id']}, {'concat': [{'get_property': ['nodeName', 'propertyName']}, 'third', '4']}]}
        self.assertEqual(res, (expected, 2))

    def test_calculate_property_function_result(self):
        template = init_template()
        value = {'get_property': ['node2', 'dummyRequirement', 'propertyName']}
        func = _is_function(value)
        res = func._calculate_function_result()
        self.assertEqual(res, (value, 2))
        func._update_function_reference(template)
        res = func._calculate_function_result()
        expected = ({'get_property': ['nodeName', 'propertyName']}, 2)
        self.assertEqual(res, expected)

