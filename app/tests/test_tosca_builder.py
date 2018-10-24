import unittest
from tests.utils.test_utils import init_tosca_builder_with_schema_and_spec, \
    init_tosca_builder_with_policy_schema_and_spec, init_tosca_builder_with_hello_world_spec_k8
from toscalib.tosca_workbook import ToscaWorkBook


class TestToscaBuilderMethods(unittest.TestCase):

    def test_create_node_type(self):
        builder = init_tosca_builder_with_schema_and_spec()
        self.assertIsNotNone(builder.spec_import.type)
        self.assertEqual(builder.spec_import.type, 'docker')
        self.assertTrue(builder._using_dmaap())
        self.assertIsNone(builder.cloudify_type)
        self.assertIsNone(builder.new_type_name)
        self.assertNotIn('tosca.dcae.nodes.dockerApp.test_spec_ss', builder.db.NODE_TYPES)
        self.assertNotIn('tosca.dcae.nodes.dockerApp.docker_flag', builder.db.NODE_TYPES)
        builder.create_node_type()
        self.assertIn('tosca.dcae.nodes.dockerApp.test_spec_ss', builder.db.NODE_TYPES)
        self.assertIsNotNone(builder.new_type_name)
        self.assertEqual(builder.new_type_name, 'tosca.dcae.nodes.dockerApp.test_spec_ss')
        self.assertIsNotNone(builder.cloudify_type)
        # TODO uncomment after K8 support integration
       # self.assertEqual(builder.cloudify_type, builder.db.NODE_TYPES['dcae.nodes.ContainerizedServiceComponentUsingDmaap'])
       #  builder.create_node_type('docker_flag', True)
       #  self.assertIn('tosca.dcae.nodes.dockerApp.docker_flag', builder.db.NODE_TYPES)
       #  self.assertEqual(builder.new_type_name, 'tosca.dcae.nodes.dockerApp.docker_flag')
       #  self.assertEqual(builder.cloudify_type, builder.db.NODE_TYPES['dcae.nodes.DockerContainerForComponentsUsingDmaap'])

    def test_create_model(self):
        builder = init_tosca_builder_with_schema_and_spec()
        builder.create_node_type()
        builder.create_model('test_ss')
        self.assertIsNotNone(builder.template)
        self.assertIsNotNone(builder.template.db)
        self.assertEqual(builder.db, builder.template.db)
        self.assertIn('test_ss', builder.template.node_dict)
        self.assertIn('topic0', builder.template.node_dict)

    def test_create_translate(self):
        builder = init_tosca_builder_with_schema_and_spec()
        builder.create_node_type()
        builder.create_translate('test_ss')
        self.assertIsNotNone(builder.template)
        self.assertEqual(len(builder.template.sub_rules), 2)
        self.assertEqual(builder.template.metadata, {'template_name': 'test_ss_translate'})
        self.assertEqual(builder.db, builder.template.db)

    def test_create_policy(self):
        builder = init_tosca_builder_with_policy_schema_and_spec()
        self.assertEqual(len(builder.db.DATA_TYPES), 0)
        self.assertEqual(len(builder.db.NODE_TYPES), 1)
        builder.create_policy()
        self.assertEqual(len(builder.db.DATA_TYPES), 3)
        self.assertEqual(len(builder.db.NODE_TYPES), 2)

    def test_spec_to_model_to_blueprint_create(self):
        #TODO imports section
        #TODO assertions
        builder = init_tosca_builder_with_hello_world_spec_k8()
        name = builder.spec_import.name
        filename = 'WEB'
        builder.create_node_type(name)
        schema = builder.export_schema(filename)
        builder.create_model(name)
        template = builder.export_model(filename)
        builder.create_translate(name)
        translate = builder.export_translation(filename)
        workbook = ToscaWorkBook()
        workbook._import_dir('../data/shared_model/')
        workbook._import_yml_str(schema)
        workbook._import_yml_str(template)
        workbook._import_yml_str(translate)
        workbook._translate_template_yaml_str(template)
        workbook._add_shared_node(
            [{'dcae.capabilities.cdapHost': 'cdap_host'}, {'dcae.capabilities.dockerHost': 'docker_host'},
             {'dcae.capabilities.composition.host': 'composition_virtual'}])
        bp = workbook._export_yaml_web('cloudify,main')
