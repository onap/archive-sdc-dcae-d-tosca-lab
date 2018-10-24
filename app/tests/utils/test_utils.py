from toscalib.templates.topology import ToscaTopology
from toscalib.templates.database import ToscaDB
from toscalib.types.node import NodeType
from toscalib.types.capability import CapabilityType
from toscalib.tosca_builder import ToscaBuilder
import os

CURR_DIR = os.path.dirname(os.path.abspath(__file__))
meta_model = os.path.join(CURR_DIR, os.pardir, '../data/meta_model/meta_tosca_schema.yaml')
policy_model = os.path.join(CURR_DIR, os.pardir, '../data/meta_model/meta_policy_schema.yaml')


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

def init_sub_template():
    db = ToscaDB()
    sub_capability = CapabilityType('tosca.capabilities.substitute', {'properties': {'capabilityProperty': {'type': 'string'}}})
    sub_capability._parse_content(db)
    db._import_capability_type(sub_capability)
    sub_node = NodeType('substituteNodeType', {'id': 'subNodeId', 'properties': {'propertyName': {'type': 'string'}}, 'capabilities': {'substituteCapability': {'type': 'tosca.capabilities.substitute'}}, 'requirements': [{'substituteRequirement': {'capability': 'tosca.capabilities.substitute'}}]})
    sub_node._parse_content(db)
    db._import_node_type(sub_node)
    template = ToscaTopology('subTemplateName', None, {'inputs': {'propertyName': {'type': 'string'}}, 'node_templates': {'nodeName': {'type': 'substituteNodeType'}}})
    template._parse_content(db)
    return template


def init_tosca_builder_with_schema_and_spec():
    spec = {"self": {
        "version": "1.1.0",
        "name": "test_spec_ss",
        "description": "Collector for receiving VES events through restful interface",
        "component_type": "docker"},
        "streams": {
            "subscribes": [],
            "publishes": [{
                "format": "VES_specification",
                "version": "5.28.4",
                "type": "message router",
                "config_key": "ves_sipsignaling"}]},
        "services": {
            "provides": [{
                "route": "/eventListener/v5",
                "verb": "POST",
                "request": {
                    "format": "VES_specification",
                    "version": "5.28.4"},
                "response": {
                    "format": "ves.coll.response",
                    "version": "1.0.0"}}]},
        "parameters": [{
            "name": "collector.service.port",
            "value": 8080,
            "description": "standard http port"},
            {"name": "collector.service.secure.port",
             "value": 8443,
             "description": "secure port "},
            {"name": "collector.keystore.file.location",
             "value": "/opt/app/dcae-certificate/keystore.jks",
             "description": "fs location of keystore in vm"}],
        "auxilary": {
            "healthcheck": {
                "type": "http",
                "interval": "15s",
                "timeout": "1s",
                "endpoint": "/healthcheck"}}}

    builder = ToscaBuilder()
    builder.import_schema(meta_model)
    builder.import_spec_str(spec)
    return builder


def init_tosca_builder_with_policy_schema_and_spec():
    spec = {"self": {
            "version": "0.1.6",
            "name": "DcaeSamCollector",
            "component_type": "docker"},
            "parameters": [{
                "name": "clliLocationMappingClliFutureUse3",
                "description": "SAM Collector clli=location ID set",
                "value": "",
                "type": "string"},
                {"name": "vnfFaultMonProvisionPolicy",
                 "policy_editable": True,
                 "policy_group": "DcaeSamCollector_vnfFaultMonProvisionPolicy",
                 "type": "string",
                 "policy_schema": [{
                      "name": "vnfTypeSpecificData",
                      "description": "List of objects for vnf type monitorng",
                      "type": "list",
                      "entry_schema": [{
                          "name": "elementType",
                          "value": ""},
                          {"name": "monitoringTasks",
                           "type": "list",
                           "entry_schema": [{
                               "name": "HostGroupSetCommonLinuxSNMP",
                               "type": "boolean",
                               "value": "false"},
                               {"name": "HostGroupSetNagent_Common_Linux",
                                "type": "boolean",
                                "value": "false"}]
                           }
                      ]
                 }]}
            ]}

    builder = ToscaBuilder()
    builder.import_schema(policy_model)
    builder.import_spec_str(spec)
    return builder

def init_tosca_builder_with_hello_world_spec_k8():
    spec = {"self": {"component_type": "docker", "description": "Hello World mS for subscribing the data from local DMaaP, DR or MR, processing them and publishing them as PM files to local DMaaP DR",
            "name": "dcae.collectors.vcc.helloworld.pm", "version": "1.0.1"}, "services": {"calls": [], "provides": []},
            "streams": {"publishes": [], "subscribes": []},
            "parameters": [{"name": "vcc_hello_name", "value": "", "description": "the name entered for specific person","sourced_at_deployment": True, "designer_editable": True, "policy_editable": False},
            {"name": "useDtiConfig", "value": False, "description": "component depends on configuration from dti.", "sourced_at_deployment": "false", "designer_editable": "false", "policy_editable": False, "required": True},
            {"name": "isSelfServeComponent", "value": "false", "description": "Is this used as self serve component.", "sourced_at_deployment": False, "designer_editable": False, "policy_editable": False, "required": "true"}],
            "auxilary": {"healthcheck": {"interval": "60s", "timeout": "20s", "script": "/opt/app/vcc/bin/common/HealthCheck_HelloWorld.sh", "type": "docker"},
            "volumes": [{"container": {"bind": "/opt/app/dcae-certificate"}, "host": {"path": "/opt/app/dcae-certificate"}},
            {"container": {"bind": "/opt/logs/DCAE/dmd/AGENT"}, "host": {"path": "/opt/logs/DCAE/helloworldpm/dmd/AGENT"}},
            {"container": {"bind": "/opt/logs/DCAE/dmd/WATCHER"}, "host": {"path": "/opt/logs/DCAE/helloworldpm/dmd/WATCHER"}},
            {"container": {"bind": "/opt/app/vcc/logs/DCAE"}, "host": {"path": "/opt/logs/DCAE/helloworldpm/vcc-logs"}},
            {"container": {"bind": "/opt/app/vcc/archive/data"}, "host": {"path": "/opt/data/DCAE/helloworldpm/vcc-archive"}}]},
            "artifacts": [{"type": "docker image", "uri": "dockercentral.it.att.com:5100/com.att.dcae.controller/dcae-controller-vcc-helloworld-pm:18.02-001"}]}

    builder = ToscaBuilder()
    builder.import_schema(meta_model)
    builder.import_spec_str(spec)
    return builder
