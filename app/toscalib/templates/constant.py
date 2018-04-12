#Author: Shu Shi
#emaiL: shushi@research.att.com

YMO_PREFIX=r'.._YAMLORDER_'

TRUE_VALUES = ('True', 'TRUE', 'true', 'yes', 'Yes', 'YES', '1')

TEMPLATE_SECTIONS = (VERSION, METADATA, DESCRIPTION, DSL, 
                     REPO, IMPORT, ARTIFACT_TYPE, DATA_TYPE, CAPABILITY_TYPE,
                     INTERFACE_TYPE, RELATIONSHIP_TYPE, NODE_TYPE, GROUP_TYPE,
                     POLICY_TYPE,  TOPOLOGY) = \
                    ('tosca_definitions_version', 'metadata', 'description', 'dsl_definitions',
                     'repositories', 'imports', 'artifact_types', 'data_types', 'capability_types',
                     'interface_types', 'relationship_types', 'node_types', 'group_types',
                     'policy_types', 'topology_template' )
                    
YAML_ORDER_TEMPLATE_SECTIONS = (YMO_VERSION, YMO_METADATA, YMO_DESCRIPTION, YMO_DSL, 
                     YMO_REPO, YMO_IMPORT, YMO_ARTIFACT_TYPE, YMO_DATA_TYPE, YMO_CAPABILITY_TYPE,
                     YMO_INTERFACE_TYPE, YMO_RELATIONSHIP_TYPE, YMO_NODE_TYPE, YMO_GROUP_TYPE,
                     YMO_POLICY_TYPE,  YMO_TOPOLOGY) = \
                    ('00_YAMLORDER_tosca_definitions_version', '02_YAMLORDER_metadata', '01_YAMLORDER_description', '03_YAMLORDER_dsl_definitions',
                     '04_YAMLORDER_repositories', '05_YAMLORDER_imports', '06_YAMLORDER_artifact_types', '07_YAMLORDER_data_types', '08_YAMLORDER_capability_types',
                     '09_YAMLORDER_interface_types', '10_YAMLORDER_relationship_types', '11_YAMLORDER_node_types', '12_YAMLORDER_group_types',
                     '13_YAMLORDER_policy_types', '14_YAMLORDER_topology_template' )

# Topology template key names
TOPOLOGY_SECTIONS = (TOPO_DESCRIPTION, TOPO_INPUTS, TOPO_NODE_TEMPLATES,
            TOPO_RELATIONSHIP_TEMPLATES, TOPO_OUTPUTS, TOPO_GROUPS,
            TOPO_SUBSTITUION_MAPPINGS) = \
           ('description', 'inputs', 'node_templates',
            'relationship_templates', 'outputs', 'groups',
            'substitution_mappings')
           
YAML_ORDER_TOPOLOGY_SECTIONS = (YMO_TOPO_DESCRIPTION, YMO_TOPO_INPUTS, YMO_TOPO_NODE_TEMPLATES,
            YMO_TOPO_RELATIONSHIP_TEMPLATES, YMO_TOPO_OUTPUTS, YMO_TOPO_GROUPS,
            YMO_TOPO_SUBSTITUION_MAPPINGS) = \
           ('10_YAMLORDER_description', '11_YAMLORDER_inputs', '13_YAMLORDER_node_templates',
            '14_YAMLORDER_relationship_templates', '16_YAMLORDER_outputs', '15_YAMLORDER_groups',
            '12_YAMLORDER_substitution_mappings')

SUBSTITUTION_SECTION = (SUB_NODE_TYPE, SUB_PROPERTY, SUB_ATTRIBUTE, SUB_REQUIREMENT, SUB_CAPABILITY, SUB_CAP_PROPERTY, SUB_CAP_ID, SUB_REQ_ID, SUB_INPUT, SUB_OUTPUT) = \
                ('node_type', 'properties', 'attributes', 'requirements', 'capabilities', 'properties', 'id', 'id', 'INPUT', 'OUTPUT')
                
YAML_ORDER_SUBSTITUTION_SECTION = (YMO_SUB_NODE_TYPE, YMO_SUB_PROPERTY, YMO_SUB_REQUIREMENT, YMO_SUB_CAPABILITY) = \
                ('00_YAMLORDER_node_type', '01_YAMLORDER_properties', '03_YAMLORDER_requirements', '02_YAMLORDER_capabilities')
                
REQUIREMENT_SECTION = (REQ_NODE, REQ_RELATIONSHIP, REQ_CAPABILITY, REQ_OCCURRENCE, REQ_FILTER) = \
                ('node', 'relationship', 'capability', 'occurrences', 'node_filter') 
                
YAML_ORDER_REQUIREMENOD_ASSIGNMENOD_SECTION = (YMO_REQ_NODE, YMO_REQ_RELATIONSHIP, YMO_REQ_CAPABILITY, YMO_REQ_OCCURRENCE, YMO_REQ_FILTER) = \
                ('01_YAMLORDER_node', '02_YAMLORDER_relationship', '00_YAMLORDER_capability', '04_YAMLORDER_occurrences', '03_YAMLORDER_node_filter') 

NODE_SECTION = (NOD_DERIVED_FROM, NOD_TYPE, NOD_PROPERTIES, NOD_ATTRIBUTES, NOD_REQUIREMENTS,
            NOD_INTERFACES, NOD_CAPABILITIES, NOD_ARTIFACTS, NOD_DESCRIPTION) = \
               ('derived_from', 'type', 'properties', 'attributes', 'requirements',
                'interfaces', 'capabilities', 'artifacts', 'description')
               
YAML_ORDER_NODETYPE_DEFINITION = (YMO_NOD_DERIVED_FROM, YMO_NOD_TYPE, YMO_NOD_PROPERTIES, YMO_NOD_ATTRIBUTES, YMO_NOD_REQUIREMENTS, YMO_NOD_RELATIONSHIPS,
            YMO_NOD_INTERFACES, YMO_NOD_CAPABILITIES, YMO_NOD_ARTIFACTS, YMO_NOD_DESCRIPTION) = \
               ('00_YAMLORDER_derived_from', '00_YAMLORDER_type', '01_YAMLORDER_properties', '03_YAMLORDER_attributes', '05_YAMLORDER_requirements', '05_YAMLORDER_relationships',
                '06_YAMLORDER_interfaces', '04_YAMLORDER_capabilities', '07_YAMLORDER_artifacts', '02_YAMLORDER_description')  

CAPABILITY_SECTION = (CAP_DERIVED_FROM, CAP_TYPE, CAP_PROPERTIES, CAP_ATTRIBUTES, 
                      CAP_VERSION, CAP_DESCEIPTION, CAP_SOURCE ) = \
               ('derived_from', 'type', 'properties', 'attributes', 
                'version', 'description', 'valid_source_type')
               
               
PROPERTY_SECTION = (PROP_TYPE, PROP_REQUIRED, PROP_DEFAULT, PROP_DESCRIPTION, 
                    PROP_STATUS, PROP_ENTRY, PROP_CONSTRAINT) = \
                ('type', 'required', 'default', 'description', 
                 'status', 'entry_schema', 'constraints')
                
YAML_ORDER_PROPERTY_SECTION = (YMO_PROP_TYPE, YMO_PROP_REQUIRED, YMO_PROP_DEFAULT, YMO_PROP_DESCRIPTION, 
                    YMO_PROP_STATUS, YMO_PROP_ENTRY, YMO_PROP_CONSTRAINT) = \
                ('00_YAMLORDER_type', '01_YAMLORDER_required', '03_YAMLORDER_default', '02_YAMLORDER_description', 
                 '04_YAMLORDER_status', '05_YAMLORDER_entry_schema', '06_YAMLORDER_constraints')  


YAML_ORDER_INTERFACE_SECTION = (YMO_INT_TYPE, YMO_INT_INPUTS, YMO_OP_DESCRIPTION, YMO_OP_IMPLEMENTATION, YMO_OP_EXECUTOR, YMO_OP_INPUTS) = \
                ('00_YAMLORDER_type', '01_YAMLORDER_inputs', '02_YAMLORDER_description', 
                 '03_YAMLORDER_implementation', '04_YAMLORDER_executor', '05_YAMLORDER_inputs')                  
