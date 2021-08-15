from ..... import constants
from .....data import utils_nodes


def setup_channel_nodes(layer, channel, endpoints):
    """ creates the nodes for the given channel in the form of a fill layer """
    if not layer.node: raise f"Couldn't find layer node for '{layer.name}'. Delete layer to proceed."
    if not channel.inp: raise f"Couldn't find input for channel '{channel.name}'. Delete channel to proceed."
    
    # add channel mix and opacity
    mix = __add_channel_mix(layer, channel, endpoints)
    _, _ = __add_channel_opacity(layer, mix)

    # add channel value node
    value_node = __setup_node_value(layer, channel)
    layer.node.node_tree.links.new(value_node.outputs[0], mix.inputs[2])


def remove_channel_nodes(layer, channel_uid):
    """ removes the endpoints and channel nodes from the given layer """
    # remove channel nodes
    __remove_layer_channel_nodes(layer, channel_uid)

    # remove channel endpoints
    inp_index, out_index = layer.get_channel_endpoint_indices(channel_uid)
    layer.node.node_tree.inputs.remove(layer.node.node_tree.inputs[inp_index])
    layer.node.node_tree.outputs.remove(layer.node.node_tree.outputs[out_index])


def get_channel_mix_node(layer, channel_uid):
    """ returns the mix node for the given layer and channel """
    if not layer.node: raise f"Couldn't find layer node for '{layer.name}'. Delete layer to proceed."
    return layer.node.node_tree.nodes[channel_uid]


def get_channel_tex_alpha_socket(layer, channel_uid):
    """ returns the texture alpha nodes socket for the given channel uid """
    if not layer.node: raise f"Couldn't find layer node for '{layer.name}'. Delete layer to proceed."
    return get_channel_mix_node(layer, channel_uid).inputs[0].links[0].from_node.inputs[0]


def get_channel_opacity_socket(layer, channel_uid):
    """ returns the opacity nodes socket for the given channel uid """
    if not layer.node: raise f"Couldn't find layer node for '{layer.name}'. Delete layer to proceed."
    return get_channel_tex_alpha_socket(layer, channel_uid).node.inputs[2].links[0].from_node.inputs[0]


def get_channel_value_node(layer, channel_uid):
    """ returns the node storing the value for the given channel uid """
    if not layer.node: raise f"Couldn't find layer node for '{layer.name}'. Delete layer to proceed."
    return get_channel_mix_node(layer, channel_uid).inputs[2].links[0].from_node


def get_channel_texture_nodes(layer, channel_uid):
    """ returns the texture nodes for the given channel. Returns None, None, None if the channel data type is not TEX """
    if get_channel_data_type(layer, channel_uid) == "TEX":
        tex = get_channel_value_node(layer, channel_uid)
        mapp = tex.inputs[0].links[0].from_node
        coords = mapp.inputs[0].links[0].from_node
        return tex, mapp, coords
    else:
        return None, None, None


def get_channel_data_type(layer, channel_uid):
    """ returns the type of data that this channel is set to for this layer
        return in ("COL", "TEX")
    """
    node = get_channel_value_node(layer, channel_uid)

    # return data type depending on the value node idname
    if node.bl_idname in [constants.NODES["RGB"], constants.NODES["MIX"]]:
        return "COL"
    elif node.bl_idname == constants.NODES["TEX"]:
        return "TEX"


def cycle_channel_data_type(layer, channel_uid):
    """ cycles the type of data this channel is set to in ("COL", "TEX") """
    if not layer.node: raise f"Couldn't find layer node for '{layer.name}'. Delete layer to proceed."
    
    data_type = get_channel_data_type(layer, channel_uid)
    node = get_channel_value_node(layer, channel_uid)
    channel = layer.mat.lp.channel_by_uid(channel_uid)

    # remove current setup
    connect_socket = node.outputs[0].links[0].to_socket
    utils_nodes.remove_connected_left(layer.node.node_tree, node)

    # cycle to TEX
    if data_type == "COL":
        tex = __setup_node_texture(layer, channel)
        layer.node.node_tree.links.new(tex.outputs[0], connect_socket)
        layer.node.node_tree.links.new(tex.outputs[1], get_channel_tex_alpha_socket(layer, channel_uid))
        layer.update_texture_mapping()

    # cycle to COL
    elif data_type == "TEX":
        value_node = __setup_node_value(layer, layer.mat.lp.channel_by_uid(channel_uid))
        layer.node.node_tree.links.new(value_node.outputs[0], connect_socket)


def __add_channel_mix(layer, channel, endpoints):
    """ adds the mix node representing the starting point for the given channel in this layer """
    # add mix node
    mix = layer.node.node_tree.nodes.new(constants.NODES["MIX"])
    mix.name = channel.uid
    mix.label = channel.uid
    mix.mute = not channel.default_enable

    # link mix node
    group_inp, group_out = endpoints
    layer.node.node_tree.links.new(group_inp, mix.inputs[1])
    layer.node.node_tree.links.new(mix.outputs[0], group_out)

    return mix


def __add_channel_opacity(layer, mix):
    """ adds the node controlling the opacity for the given channel node """
    # add mask node
    mask = layer.node.node_tree.nodes.new(constants.NODES["MIX"])
    mask.label = "Channel Mask"
    mask.inputs[0].default_value = 1
    mask.inputs[1].default_value = (0, 0, 0, 1)
    mask.inputs[2].default_value = (1, 1, 1, 1)

    # add opacity node
    opacity = layer.node.node_tree.nodes.new(constants.NODES["MIX"])
    opacity.label = "Channel Opacity"
    opacity.inputs[0].default_value = 1
    opacity.inputs[1].default_value = (0, 0, 0, 1)
    opacity.inputs[2].default_value = (1, 1, 1, 1)

    # add node for mixing texture alpha with opacity
    tex_alpha = layer.node.node_tree.nodes.new(constants.NODES["MIX"])
    tex_alpha.label = "Texture Alpha"
    tex_alpha.inputs[0].default_value = 1
    tex_alpha.inputs[1].default_value = (0, 0, 0, 1)
    tex_alpha.inputs[2].default_value = (1, 1, 1, 1)

    # link opacity nodes
    layer.node.node_tree.links.new(opacity.outputs[0], mask.inputs[0])
    layer.node.node_tree.links.new(mask.outputs[0], tex_alpha.inputs[2])
    layer.node.node_tree.links.new(tex_alpha.outputs[0], mix.inputs[0])
    layer.node.node_tree.links.new(layer.node.node_tree.nodes[constants.OPAC_NAME].outputs[0], opacity.inputs[2])

    return opacity, tex_alpha


def __setup_node_value(layer, channel):
    """ setup the value node for the fill layer """
    # set up value node for value channels
    if type(channel.inp.default_value) == float:
        value = layer.node.node_tree.nodes.new(constants.NODES["MIX"])
        value.inputs[0].default_value = channel.inp.default_value
        value.inputs[1].default_value = (0, 0, 0, 1)
        value.inputs[2].default_value = (1, 1, 1, 1)

    # set up value node for color channels
    else:
        value = layer.node.node_tree.nodes.new(constants.NODES["RGB"])
        value.outputs[0].default_value = channel.inp.default_value
    
    #name value node
    value.label = "Channel Value"

    return value


def __setup_node_texture(layer, channel):
    """ set up the channel to use a texture instead of the value """
    tex = layer.texture_setup()
    return tex


def __remove_layer_channel_nodes(layer, channel_uid):
    """ remove all nodes belonging to the layers channel """
    mix = get_channel_mix_node(layer, channel_uid)
    opac = get_channel_opacity_socket(layer, channel_uid).node
    tex_alpha = get_channel_tex_alpha_socket(layer, channel_uid).node
    value = get_channel_value_node(layer, channel_uid)
    
    layer.node.node_tree.nodes.remove(mix)
    layer.node.node_tree.nodes.remove(opac)
    layer.node.node_tree.nodes.remove(tex_alpha)
    utils_nodes.remove_connected_left(layer.node.node_tree, value)
