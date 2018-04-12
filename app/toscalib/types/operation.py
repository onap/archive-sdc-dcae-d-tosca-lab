from toscalib.types.property import PropertyDefinition


class OperationDefinition(object):
    def __init__(self, interface_name, name, content = None):
        self.name = name
        self.interface = interface_name
        self.raw_content = content
        self.parsed = False
        self.implementation = None
        self.inputs = {}
        
    def _parse_content(self, db):
        if self.parsed is True:
            return
        
        if self.raw_content is None:
            self.parsed = True
            return
        
        self.parsed = True

        if type(self.raw_content) is not dict:
            return
            
        for key_name in self.raw_content.keys():         
            if key_name == 'implementation':
                self.implementation = self.raw_content[key_name]
            if key_name == 'inputs':
                input_sec = self.raw_content['inputs']
                for input_item in input_sec.keys():
                    self.inputs[input_item] = PropertyDefinition(input_item, input_sec[input_item])
                    self.inputs[input_item]._parse_content(db)
            
        return
    
