#Author: Shu Shi
#emaiL: shushi@research.att.com


class RelationshipType:
    def __init__(self, name, content):
        if name is None or content is None:
            return None
        self.name = name
        self.raw_content = content
        
    def _parse_content(self, db):
        pass