from .... import constants
from ....data import utils_groups


def group_setup(layer, node):
    # add preview output to layer node
    _, out = utils_groups.add_output(node, constants.SOCKETS["COLOR"], constants.PREVIEW_OUT_NAME)
    out.default_value = (1,1,1,1)

    # add layer opacity node to group tree
    opacity = node.node_tree.nodes.new(constants.NODES["MIX"])

    opacity.name = constants.OPAC_NAME
    opacity.label = constants.OPAC_NAME
    opacity.location = (-350, -100)

    opacity.inputs[0].default_value = 1
    opacity.inputs[1].default_value = (0, 0, 0, 1)
    opacity.inputs[2].default_value = (1, 1, 1, 1)

    # add backup layer filter node
    node, ngroup = utils_groups.make_group(node.node_tree, constants.LAYER_FILTER_NAME(layer))
    _, inp = utils_groups.add_input(node, constants.SOCKETS["COLOR"], "Color")
    _, out = utils_groups.add_output(node, constants.SOCKETS["COLOR"], "Color")
    inp.node.name = constants.INPUT_NAME
    out.node.name = constants.OUTPUT_NAME
    ngroup.links.new(out, inp)
    node.label = "Layer Filter Backup"
    node.hide = True