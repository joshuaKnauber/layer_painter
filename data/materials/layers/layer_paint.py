


def setup_channel_nodes(layer, channel, endpoints):
    """ creates the nodes for the given channel in the form of a paint layer """
    mix = layer.__add_channel_mix(channel)
    layer.__add_channel_opacity(mix)

    tex = __setup_node_value(layer, channel)
    layer.node.node_tree.links.new(tex.outputs[0], mix.inputs[2])


def remove_channel_nodes(layer, channel_uid):
    """ removes the endpoints and channel nodes from the given layer """
    pass


def __setup_node_value(layer, channel):
    """ setup the value node for the paint layer """
    return None