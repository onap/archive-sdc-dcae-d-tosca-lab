import unittest
from toscalib.types.property import PropertyDefinition
from toscalib.templates.database import ToscaDB


class TestEntrySchemaMethods(unittest.TestCase):

    def test_parse_content(self):
        content = {'type': 'list', 'entry_schema': {'type': 'integer'}}
        prop_def = PropertyDefinition('propName', content)
        self.assertFalse(prop_def.parsed)
        self.assertIsNone(prop_def.type)
        self.assertIsNone(prop_def.type_obj)
        prop_def._parse_content(ToscaDB)
        self.assertTrue(prop_def.parsed)
        self.assertEqual(prop_def.type, 'list')
        self.assertTrue(prop_def.type_obj.built_in)
        self.assertEqual(prop_def.type_obj.name, 'list')
        self.assertTrue(prop_def.type_obj.parsed)
        self.assertEqual(prop_def.type_obj.type, 'list')
        self.assertEqual(prop_def.type_obj.entry.type, 'integer')
        self.assertTrue(prop_def.type_obj.entry.parsed)
        self.assertTrue(prop_def.type_obj.entry.type_obj.built_in)
        self.assertEqual(prop_def.type_obj.entry.type_obj.name, 'integer')
        self.assertEqual(prop_def.type_obj.entry.type_obj.type, 'integer')
