from .... import constants
from ....data import utils_groups


def group_setup(node):
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
