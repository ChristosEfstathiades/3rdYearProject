from rdflib import Graph
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
    
    def get_joint_kg(self, graphs):
        joint_signposts = Graph()
        provenances = []
        for graph in graphs:
            provenances.append(graph.provenance)
            joint_signposts += graph.signposts
            for linkset in graph.linksets:
                joint_signposts += graph.linksets[linkset].signposts
        return {
            'provenances': provenances,
            'signposts': joint_signposts
        }
