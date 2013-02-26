from random import Random

clusters = []

rnd = Random(0)

class Cluster(object):
    def __init__(self, _id, name, node_templates, base_image, status, nodes_count):
        self.id = _id
        self.name = name
        self.node_templates = node_templates
        self.base_image = base_image
        self.nodes_count = nodes_count
        self.status = status

def createCluster(name, node_templates, base_image, nodes_count) :
    cl = Cluster(rnd.randint(0, 1000000), name, node_templates, base_image, "active", nodes_count)
    clusters.append(cl)

def find_cluster(cluster_id):
    for cl in clusters:
        if cl.id == cluster_id:
            return cl

def getClusters():
    return get_hardcode_clusters()

def get_hardcode_clusters():
    cl1 = Cluster(0, "cluster-01", ["jt_nn.xlarge: 1", "tt_dn.medium: 10"], "ubuntu-12.04-x86_64", "active", 11)
    cl2 = Cluster(1, "cluster-02", ["jt.large: 1", "nn.large: 1", "tt_dn.medium: 10"], "ubuntu-12.04-x86_64", "active", 12)
    return [cl1, cl2]
