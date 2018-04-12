#Author: Shu Shi
#emaiL: shushi@research.att.com

from toscalib.types.constraints import PropertyConstraints
from toscalib.types.entry_schema import EntrySchema
from toscalib.types.data import DataType, TYP_STR, TYP_ANY, TYP_MAP
from toscalib.templates.constant import *
import logging

class PropertyDefinition(object):
    def __init__(self, name, content = None):
        self.name = name
        self.raw_content = content
        self.parsed = False
        self.type = None
        self.type_obj = None
        
        if content is None:
            self.required = True
            self.type = TYP_ANY
            self.type_obj = DataType(self.type)
            self.default = self.name
            self.parsed = True
        
    def _parse_content(self, db):
        
        if self.parsed is True:
            return
        
        content = self.raw_content
        
        if content is None:
            self.required = True
            self.type = TYP_ANY
            self.type_obj = DataType(self.type)
            self.default = self.name
            self.parsed = True
            return
        
#        if content.has_key(PROP_TYPE):
        if PROP_TYPE in content:
            self.type = content[PROP_TYPE]
            if self.type in DataType._built_in_types():
                self.type_obj = DataType(self.type)
                self.type_obj._parse_content(db)
#            elif db.DATA_TYPES.has_key(self.type) is False:
            elif self.type in db.DATA_TYPES is False:
                logging.warning( 'Data type: '+ self.type+ ' not defined or imported!')
                self.type_obj = None
            else:
                self.type_obj = db.DATA_TYPES[self.type]
                self.type_obj._parse_content(db)

        self.required = True
#        if content.has_key(PROP_REQUIRED):
        if PROP_REQUIRED in content:
            if content[PROP_REQUIRED] not in TRUE_VALUES:
                self.required = False
            
#        if content.has_key(PROP_DEFAULT):
        if PROP_DEFAULT in content:
            self.default = content[PROP_DEFAULT]
        else:
            self.default = None
            
#        if content.has_key(PROP_ENTRY):
        if PROP_ENTRY in content:
            self.type_obj.entry = EntrySchema(content[PROP_ENTRY])
            self.type_obj.entry._parse_content(db)
            
#        if content.has_key(PROP_CONSTRAINT):
        if PROP_CONSTRAINT in content:
            self.constraints = PropertyConstraints(content[PROP_CONSTRAINT])
            self.constraints._parse_content()
        else:
            self.contraints = None
            
        self.parsed = True

    def _create_rawcontent(self):
        self.raw_content = {}
        self.raw_content[YMO_PROP_TYPE] = self.type
        if self.type == TYP_ANY:
            self.raw_content[YMO_PROP_TYPE] = TYP_STR
        if self.default is not None and self.default is not self.name:
            self.raw_content[YMO_PROP_DEFAULT] = self.default
        if self.required is False:
            self.raw_content[YMO_PROP_REQUIRED] = self.required
#add more about constraints        
        
  
  