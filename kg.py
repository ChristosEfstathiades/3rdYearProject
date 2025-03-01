class KG:
    def __init__(self, origin, signposts=None, metadata=None, linksets=None):
        self.provenance = origin
        self.signposts = signposts
        self.metadata = metadata
        self.linksets = linksets

    # def set_metadata(self, links, metadata):
    #     for index in range(len(links)):
    #         self.metadata[links[index]] = metadata[index]

    # def set_linksets(self, link, signposts):
    #     self.linksets[link]['signposts'] = signposts

    def get_kg(self): 
        return {
            'provenance': self.provenance,
            'signposts': self.signposts,
            'linksets': self.linksets,
            'metadata': self.metadata
        }
