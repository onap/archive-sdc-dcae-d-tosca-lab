#Author: Shu Shi
#emaiL: shushi@research.att.com


from toscalib.templates.constant import *
import logging

class RequirementDefinition(object):
    def __init__(self, content):
        self.name =  None
        self.parsed = False
        self.raw_content = content
        self.req_type = None
        self.req_capability = None
        self.relationship = None
        self.occurrence = [1,1]
        
    def _parse_content(self, db):
        if self.parsed is True:
            return
        
        content = self.raw_content
    
        if content is None:
            logging.warning( 'Construct None requirement section')
            self.parsed = True
            return
        if len(content.keys()) != 1:
            logging.warning( 'Requirement section does not have exact one element: ' + len(content.keys()))
            return
        self.name = list(content.keys())[0]
        requirement_def = content[self.name]
        if type(requirement_def) is not dict:
            logging.warning( 'Cannot parse requirement definition: '+ self.name)
            return
        
#        if requirement_def.has_key(REQ_NODE):
        if REQ_NODE in requirement_def:
            self.req_type = requirement_def[REQ_NODE]
        else:
            self.req_type = None
#        if requirement_def.has_key(REQ_CAPABILITY):
        if REQ_CAPABILITY in requirement_def:
            self.req_capability = requirement_def[REQ_CAPABILITY]
        else:
            self.req_capability = None
#        if requirement_def.has_key(REQ_RELATIONSHIP):
        if REQ_RELATIONSHIP in requirement_def:
            self.relationship = requirement_def[REQ_RELATIONSHIP]
        else:
            self.relationship = None
#        if requirement_def.has_key(REQ_OCCURRENCE):
        if REQ_OCCURRENCE in requirement_def:
            self.occurrence = requirement_def[REQ_OCCURRENCE]
            if type(self.occurrence) is not list:
                logging.warning( 'Requirement occurrence expects a list of two numbers but provided with: '+ self.occurrence)
        
        self.parsed = True
        
        
            
            
            