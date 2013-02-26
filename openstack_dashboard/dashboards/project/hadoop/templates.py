from random import Random

images = []
rnd = Random(0)

class Template(object):
    def __init__(self, id, node_template_name, node_type, flavor_name):
        self.id = id
        self.name = node_template_name
        self.node_type = node_type
        self.flavor_name = flavor_name

def addImage(node_template_name, node_type, flavor_name):

    images.append(Template(rnd.randint(0, 1000000), node_template_name, node_type, flavor_name))

def getImages():
    return get_hardcode_images()

def remove(id):
    for image in images:
        if image.id == id:
            images.remove(image)
            return 1
    return 0


def get_hardcode_images():
    im0 = Template(0, "jt_nn.large", "JT+NN", "m1.large")
    im1 = Template(1, "jt_nn.xlarge", "JT+NN", "m1.xlarge")
    im2 = Template(2, "jt.large", "JT", "m1.large")
    im3 = Template(3, "nn.large", "NN", "m1.large")
    im4 = Template(4, "tt_dn.medium", "TT+DN", "m1.medium")
    im5 = Template(5, "tt_dn.large", "TT+DN", "m1.large")
    im6 = Template(6, "tt_dn.xlarge", "TT+DN", "m1.xlarge")

    return [im0, im1, im2, im3, im4, im5, im6]