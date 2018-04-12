#Author: Shu Shi
#emaiL: shushi@research.att.com

from toscalib.templates.constant import *
from toscalib.types.constraints import PropertyConstraints
import logging

class EntrySchema(object):
    def __init__(self, content):
        self.type = None
        self.type_obj = None
        self.constraints = None
        self.raw_content = content
        self.parsed = False
    
    def _parse_content(self, db):
        if self.parsed is True:
            return
        
        if self.raw_content is None:
            logging.warning( 'Construct None entry_schema section')
            self.parsed = True
            return
        
        if type(self.raw_content) is str:
            self.type = self.raw_content
            from toscalib.types.data import DataType
            if self.type in DataType._built_in_types():
                self.type_obj = DataType(self.type)
#            elif db is None or db.DATA_TYPES.has_key(self.type) is False:
            elif db is None or self.type not in db.DATA_TYPES:
                logging.warning( 'Data type: '+ self.type+ ' not defined or imported!')
                self.type_obj = None
            else:
                self.type_obj = db.DATA_TYPES[self.type]
                self.type_obj._parse_content(db)
            self.parsed = True
            return
            
#        if self.raw_content.has_key(PROP_TYPE):
        if PROP_TYPE in self.raw_content:
            self.type = self.raw_content[PROP_TYPE]
            from toscalib.types.data import DataType
            if self.type in DataType._built_in_types():
                self.type_obj = DataType(self.type)
#            elif db is None or db.DATA_TYPES.has_key(self.type) is False:
            elif db is None or self.type not in db.DATA_TYPES:
                logging.warning( 'Data type: '+ self.type+ ' not defined or imported!')
                self.type_obj = None
            else:
                self.type_obj = db.DATA_TYPES[self.type]
                self.type_obj._parse_content(db)
        
#        if self.raw_content.has_key(PROP_CONSTRAINT):
        if PROP_CONSTRAINT in self.raw_content:
            self.constraints = PropertyConstraints(self.raw_content[PROP_CONSTRAINT])
            self.constraints._parse_content()
            
        self.parsed = True
        return
    
    def _format_value (self, value):
        if self.type_obj is not None:
            return self.type_obj._format_value(value)
        else:
            logging.warning( 'Invalid entry_schema type')
            return value
    