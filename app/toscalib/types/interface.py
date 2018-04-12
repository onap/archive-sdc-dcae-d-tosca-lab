from toscalib.types.property import PropertyDefinition
from toscalib.types.operation import OperationDefinition


class InterfaceDefinition(object):
    def __init__(self, name, content = None):
        self.name = name
        self.raw_content = content
        self.parsed = False
        self.operations = {}
        self.type = None
        self.inputs = {}
        
    def _parse_content(self, db):
        if self.parsed is True:
            return
        
        if self.raw_content is None:
            self.parsed = True
            return

        for key_name in self.raw_content.keys():         
            if key_name == 'type':
                self.type = self.raw_content[key_name]
                continue
            if key_name == 'inputs':
                input_sec = self.raw_content['inputs']
                for input_item in input_sec.keys():
                    self.inputs[input_item] = PropertyDefinition(input_item, input_sec[input_item])
                    self.inputs[input_item]._parse_content(db)
                continue
            self.operations[key_name] = OperationDefinition(self.name, key_name, self.raw_content[key_name])
            self.operations[key_name]._parse_content(db)
            
        self.parsed = True
        return
    
