class KG:
    def __init__(self, origin, signposts=None, metadata=None, linksets=None):
        self.provenance = origin
        self.signposts = signposts
        self.metadata = metadata
        self.linksets = linksets

    def get_kg(self): 
        return {
            'provenance': self.provenance,
            'signposts': self.signposts,
            'linksets': self.linksets,
            'metadata': self.metadata
        }
