from toscalib.templates.constant import *
import logging


class SubstitutionRule (object):
    def __init__(self, type, item_name, prop_name, value):
        self.type = type
        self.item = item_name
        self.property = prop_name
        self.value = value
        
    def _update_pointer(self, src_node, dst_template):
        if type(self.value) is not list and len(self.value) < 1:
            logging.warning( 'Incorrect mapping rule for property '+ self.property+ ': '+ self.value)
            return
        
        if self.type == SUB_PROPERTY:
            if self.value[0] == SUB_INPUT:
#                if hasattr(dst_template, 'inputs') and dst_template.inputs.has_key(self.value[1]):
                if hasattr(dst_template, 'inputs') and self.value[1] in dst_template.inputs:
                    if src_node is not None:
                        src_node.properties[self.property].sub_pointer = dst_template.inputs[self.value[1]]
                        if src_node.properties[self.property].required is True or src_node.properties[self.property].filled is True:
                            dst_template.inputs[self.value[1]].used = True
                elif src_node is not None and src_node.properties[self.property].required is True:
                    logging.warning( 'Incorrect mapping rule for property '+ self.property+ ': no input named '+ self.value[1])
#            elif dst_template.node_dict.has_key(self.value[0]):
            elif self.value[0] in dst_template.node_dict:
                target_node = dst_template.node_dict[self.value[0]]
                target_prop_item = target_node._get_property_item(self.value[1])
                if target_prop_item is not None: 
                    if src_node is not None:
                        src_prop_item = src_node._get_property_item(self.property)
                        if src_prop_item.required is True or src_prop_item.filled is True:
                            target_prop_item.used = True
                        if src_prop_item is not None:
                            src_prop_item.sub_pointer = target_prop_item
                else:
                    logging.warning( 'Incorrect mapping rule for property '+ self.property+ ': no property named '+ self.value[1]+ ' in node '+ self.value[0])
            else:
                logging.warning('Incorrect mapping rule for property '+ self.property+ ': no node named '+ self.value[0])
        
        elif self.type == SUB_ATTRIBUTE:
            if self.value[0] == SUB_OUTPUT:
#                if hasattr(dst_template, 'outputs') and dst_template.outputs.has_key(self.value[1]):
                if hasattr(dst_template, 'outputs') and self.value[1] in dst_template.outputs:
                    if src_node is not None:
                        src_node.attributes[self.property].sub_pointer = dst_template.outputs[self.value[1]]
                else: 
                    logging.warning( 'Incorrect mapping rule for attribute '+ self.property+ ': no output named '+ self.value[1])
        
        elif self.type == SUB_CAPABILITY:
            if self.property is None:
#                if dst_template.node_dict.has_key(self.value[0]):
                if self.value[0] in dst_template.node_dict:
                    target_node = dst_template.node_dict[self.value[0]]
                    target_cap_item = target_node._get_capability_item(self.value[1])
                    if target_cap_item is not None:
                        if src_node is not None:
                            src_cap_item = src_node._get_capability_item(self.item)
                            if src_cap_item is not None:
                                src_cap_item.sub_pointer = target_cap_item
                                for prop_name in src_cap_item.properties.keys():
                                    src_cap_item.properties[prop_name].sub_pointer = target_cap_item.properties[prop_name]
                    else:
                        logging.warning( 'Incorrect mapping rule for capability '+ self.item+ ': no capability named '+ self.value[1]+ ' in node '+ self.value[0])
                else:
                    logging.warning( 'Incorrect mapping rule for capability '+ self.item+ ': no node named '+ self.value[0])
            elif self.property == SUB_CAP_ID:
                if self.value[0] == SUB_OUTPUT:
#                    if hasattr(dst_template, 'outputs') and dst_template.outputs.has_key(self.value[1]):
                    if hasattr(dst_template, 'outputs') and self.value[1] in dst_template.outputs:
                        target_node = dst_template.outputs[self.value[1]]
                        if src_node is not None:
                            src_cap_item = src_node._get_capability_item(self.item)
                            if src_cap_item is not None:
                                src_cap_item.sub_pointer = target_node
#                elif dst_template.node_dict.has_key(self.value[0]):
                elif self.value[0] in dst_template.node_dict:
                    target_node = dst_template.node_dict[self.value[0]]
                    if len(self.value) < 2:
                        target_item = target_node
#                    elif target_node.capabilities.has_key(self.value[1]) and len(self.value) > 1:
                    elif len(self.value) > 1 and self.value[1] in target_node.capabilities :
                        target_item = target_node._get_capability_property(self.value[1], self.value[2])
                    elif self.value[1] in target_node.properties:
                        target_item = target_node._get_property_item(self.value[1])
                    else:
                        target_item = None
                        logging.warning( 'Incorrect mapping rule for capability '+ self.item+ ': no capability/property named '+ self.value[1]+ ' in node '+ self.value[0])

                    if target_item is not None and src_node is not None:
                        src_cap_item = src_node._get_capability_item(self.item)
                        if src_cap_item is not None:
                            src_cap_item.sub_pointer = target_item
            else:
                if self.value[0] == SUB_INPUT:
#                    if hasattr(dst_template, 'inputs') and dst_template.inputs.has_key(self.value[1]):
                    if hasattr(dst_template, 'inputs') and self.value[1] in dst_template.inputs:
                        if src_node is not None:
                            src_cap_prop_item = src_node._get_capability_property(self.item, self.property)
                            src_cap_prop_item.sub_pointer = dst_template.inputs[self.value[1]]
                            if src_cap_prop_item.required is True or src_cap_prop_item.filled is True:
                                dst_template.inputs[self.value[1]].used = True
                    else:
                        logging.warning( 'Incorrect mapping rule for capability '+ self.item+ ': no input named '+ self.value[1])
#                elif dst_template.node_dict.has_key(self.value[0]):
                elif self.value[0] in dst_template.node_dict:
                    target_node = dst_template.node_dict[self.value[0]]

#                    if target_node.capabilities.has_key(self.value[1]):
                    if self.value[1] in target_node.capabilities:
                        target_cap_property = target_node._get_capability_property(self.value[1], self.value[2])
                        if target_cap_property is not None:
                            if src_node is not None:
                                src_cap_prop_item = src_node._get_capability_property(self.item, self.property)
                                if src_cap_prop_item is not None:
                                    src_cap_prop_item.sub_pointer = target_cap_property
                        else:
                            logging.warning( 'Incorrect mapping rule for capability '+ self.item+ ': no property named '+ self.value[2]+ ' in capability '+ self.value[0]+ '->'+ self.value[1])
#                    elif target_node.properties.has_key(self.value[1]):
                    elif self.value[1] in target_node.properties:
                        target_prop_item = target_node._get_property_item(self.value[1])
                        if src_node is not None:
                            src_cap_prop_item = src_node._get_capability_property(self.item, self.property)
                            if src_cap_prop_item is not None:
                                src_cap_prop_item.sub_pointer = target_prop_item
                    else:
                        logging.warning( 'Incorrect mapping rule for capability '+ self.item+ ': no capability/property named '+ self.value[1]+ ' in node '+ self.value[0])
                else:
                    logging.warning( 'Incorrect mapping rule for capability '+ self.item+ ': no node named '+ self.value[0])
        
        elif self.type == SUB_REQUIREMENT:
            if self.property is None:
#                if dst_template.node_dict.has_key(self.value[0]):
                if self.value[0] in dst_template.node_dict:
                    target_node = dst_template.node_dict[self.value[0]]
                    target_req_item = target_node._get_requirement_item_first(self.value[1])
                    if target_req_item is not None:
                        if src_node is not None:
                            src_req_item = src_node._get_requirement_item_first(self.item)
                            if src_req_item is not None:
                                src_req_item.sub_pointer = target_req_item
                    else:
                        logging.warning( 'Incorrect mapping rule for requirement '+ self.item+ ': no requirement named '+ self.value[1]+ ' in node '+ self.value[0])
                else:
                    logging.warning( 'Incorrect mapping rule for requirement '+ self.item+ ': no node named '+ self.value[0])
            elif self.property == SUB_REQ_ID:
                if self.value[0] == SUB_INPUT:
#                    if hasattr(dst_template, 'inputs') and dst_template.inputs.has_key(self.value[1]):
                    if hasattr(dst_template, 'inputs') and self.value[1] in dst_template.inputs:
                        if src_node is not None:
                            src_req_item = src_node._get_requirement_item_first(self.item)
                            if src_req_item is not None:
                                src_req_item.sub_pointer = dst_template.inputs[self.value[1]]
                                dst_template.inputs[self.value[1]].used = True
                    else:
                        logging.warning( 'Incorrect mapping rule for property '+ self.property+ ': no input named '+ self.value[1])

#                elif dst_template.node_dict.has_key(self.value[0]):
                elif self.value[0] in dst_template.node_dict:
                    target_node = dst_template.node_dict[self.value[0]]
                    target_prop_item = target_node._get_property_item(self.value[1])
                    if target_prop_item is not None:
                        if src_node is not None:
                            src_req_item = src_node._get_requirement_item_first(self.item)
                            if src_req_item is not None:
                                src_req_item.sub_pointer = target_prop_item
                    else:
                        logging.warning( 'Incorrect mapping rule for requirement '+ self.item+ ': no property named '+ self.value[1]+ ' in node '+ self.value[0])
                else:
                    logging.warning( 'Incorrect mapping rule for requirement '+ self.item+ ': no node named '+ self.value[0])
            else:
                logging.warning( 'Incorrect mapping rule for requirement '+ self.item+ ': wrong property name '+ self.property)
                
        else:
            logging.warning('Incorrect mapping rule type: '+ self.type)
                
        
