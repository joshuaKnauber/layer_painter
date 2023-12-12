from .... import constants
from ....data import utils_groups
from .layer_types import layer_fill, layer_paint


def setup(layer):
    """set up all channels for the given layer"""
    update(layer)


def update(layer):
    """update all channels for the given layer"""
    if not layer.node:
        raise f"Couldn't find layer node for '{layer.name}'. Delete layer to proceed."
    __add_new_channels(layer)
    __remove_orphan_channels(layer)


def disconnect_outputs(layer):
    """disconnects all the layers channel outputs"""
    if not layer.node:
        raise f"Couldn't find layer node for '{layer.name}'. Delete layer to proceed."

    # go through all channels and disconnect
    for channel in layer.mat.lp.channels:
        index = layer.get_channel_output_index(channel.uid)
        if index >= 0:
            for link in layer.node.outputs[index].links:
                layer.mat.node_tree.links.remove(link)


def connect_channel_outputs(layer):
    """connects all channel outputs to the layer above"""
    if not layer.node:
        raise f"Couldn't find layer node for '{layer.name}'. Delete layer to proceed."

    # go through all channels and connect output
    for channel in layer.mat.lp.channels:
        index = layer.get_channel_output_index(channel.uid)
        if index >= 0:
            __connect_layer_output(layer, channel, layer.node.outputs[index])


def __add_new_channels(layer):
    """create all channels in the layer that haven't been added yet"""
    for channel in layer.mat.lp.channels:
        if not layer.has_channel_input(channel.uid):
            # create channel
            inp, out = __create_channel(layer, channel)

            # connect channel to surrounding layers or channel input
            __connect_layer_output(layer, channel, out)
            __connect_layer_input(layer, channel, inp)


def __create_channel(layer, channel):
    """creates the nodes for the given channel in this layer"""
    # add channel in and output to node group
    endpoints = __add_channel_endpoints(layer, channel)

    # set up nodes inside layer depending on layer type
    if layer.layer_type == "FILL":
        layer_fill.setup_channel_nodes(layer, channel, endpoints)
    elif layer.layer_type == "PAINT":
        layer_paint.setup_channel_nodes(layer, channel, endpoints)

    inp_index, out_index = layer.get_channel_endpoint_indices(channel.uid)
    return layer.node.inputs[inp_index], layer.node.outputs[out_index]


def __add_channel_endpoints(layer, channel):
    """adds the in and output for the given channel in this layer"""
    if not channel.inp:
        raise f"Couldn't find input for channel '{channel.name}'. Delete channel to proceed."

    # create node group input for channel
    inp, group_inp = utils_groups.add_input(
        layer.node, channel.inp.bl_rna.identifier, channel.name
    )
    inp.default_value = channel.inp.default_value

    # create node group output for channel
    out, group_out = utils_groups.add_output(
        layer.node, channel.inp.bl_rna.identifier, channel.name
    )
    out.default_value = channel.inp.default_value

    # set uids to match channel uid
    group_inp.uid = channel.uid
    group_out.uid = channel.uid
    return group_inp, group_out


def __connect_layer_output(layer, channel, out):
    """try to connect the given layer output to the correct input"""
    if not channel.inp:
        raise f"Couldn't find input for channel '{channel.name}'. Delete channel to proceed."

    above = layer.mat.lp.layer_above(layer)
    if above and not above.node:
        raise f"Couldn't find layer node for '{above.name}'. Delete layer to proceed."

    # connect channel output to channel input
    if not above:
        layer.mat.node_tree.links.new(out, channel.inp)
    # connect channel output to layer above
    else:
        index = above.get_channel_input_index(channel.uid)
        if index >= 0:
            layer.mat.node_tree.links.new(out, above.node.inputs[index])


def __connect_layer_input(layer, channel, inp):
    """try to connect the given layer input to the correct output"""
    below = layer.mat.lp.layer_below(layer)
    if below and not below.node:
        raise f"Couldn't find layer node for '{below.name}'. Delete layer to proceed."

    # connect channel input to layer below
    if below:
        index = below.get_channel_output_index(channel.uid)
        if index >= 0:
            layer.mat.node_tree.links.new(below.node.outputs[index], inp)


def __remove_orphan_channels(layer):
    """removes all channels that aren't part of the material"""
    channel_uids = layer.mat.lp.channel_uids

    # go through all layer inputs to check if they should still exist
    inputs = [
        *filter(
            lambda i: i.item_type == "SOCKET" and i.in_out == "INPUT",
            layer.node.node_tree.interface.items_tree,
        )
    ]
    for i in range(len(inputs) - 1, -1, -1):
        out = layer.node.node_tree.nodes[constants.INPUT_NAME].outputs[i]
        if hasattr(out, "uid") and not out.uid in channel_uids:
            # set up nodes inside layer depending on layer type
            if layer.layer_type == "FILL":
                layer_fill.remove_channel_nodes(layer, out.uid)
            elif layer.layer_type == "PAINT":
                layer_paint.remove_channel_nodes(layer, out.uid)
