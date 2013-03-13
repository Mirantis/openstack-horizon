class Cluster(object):
    def __init__(self, _id, name, node_templates, base_image, status, nodes_count):
        self.id = _id
        self.name = name
        self.node_templates = node_templates
        self.base_image = base_image
        self.nodes_count = nodes_count
        self.status = status
