import bpy
from .. import constants


def __add_warning_frame(ntree):
    """adds a warning to the given node tree as not to edit it"""
    frame = ntree.nodes.new(constants.NODES["FRAME"])
    frame.label = "Do not edit this node group! This will break Layer Painter!"
    frame.use_custom_color = True
    frame.color = (1, 0, 0)
    frame.width = 1000
    frame.height = 30


def make_group(ntree, name):
    """creates an empty node group and assigns it to a node"""
    ngroup = bpy.data.node_groups.new(name, "ShaderNodeTree")
    ngroup.use_fake_user = True

    group_inputs = ngroup.nodes.new(constants.NODES["GROUP_IN"])
    group_inputs.location = (-350, 0)
    group_inputs.name = constants.INPUT_NAME

    group_outputs = ngroup.nodes.new(constants.NODES["GROUP_OUT"])
    group_outputs.name = constants.OUTPUT_NAME
    group_outputs.location = (300, 0)

    node = ntree.nodes.new(constants.NODES["GROUP"])
    node.node_tree = ngroup
    node.name = name
    node.label = name

    # __add_warning_frame(ngroup)

    return node, ngroup


def add_input(node, idname, name):
    """adds an input to the given nodes node group
    return node_input, node_group_input_node_output
    """
    if idname in constants.SOCKET_MAP:
        idname = constants.SOCKET_MAP[idname]
    node.node_tree.interface.new_socket(socket_type=idname, name=name, in_out="INPUT")
    return node.inputs[-1], node.node_tree.nodes[constants.INPUT_NAME].outputs[-2]


def add_output(node, idname, name):
    """adds an output to the given nodes node group
    return node_output, node_group_output_node_input
    """
    if idname in constants.SOCKET_MAP:
        idname = constants.SOCKET_MAP[idname]
    node.node_tree.interface.new_socket(socket_type=idname, name=name, in_out="OUTPUT")
    return node.outputs[-1], node.node_tree.nodes[constants.OUTPUT_NAME].inputs[-2]
