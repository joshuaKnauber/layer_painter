import bpy
import os

from .... import utils, constants
from ....assets import utils_import
from ... import utils_groups
from . import layer_setup, layer_channels
from .layer_types import layer_fill


# holds cached materials and layer nodes for faster repeated access
cached_materials = {}
cached_nodes = {}


def clear_caches():
    """ clears the cached materials and layer nodes """
    global cached_materials
    cached_materials = {}
    global cached_nodes
    cached_nodes = {}


class LP_LayerProperties(bpy.types.PropertyGroup):

    @property
    def __material_by_ref(self):
        """ returns the material matching the layers uid reference to it """
        for material in bpy.data.materials:
            if material.lp.uid == self.mat_uid_ref:
                cached_materials[self.mat_uid_ref] = material
                return material

    @property
    def mat(self):
        """ returns the material this layer belongs to from cache or uid reference """
        global cached_materials
        if self.mat_uid_ref in cached_materials:
            try:
                if cached_materials[self.mat_uid_ref].name:
                    return cached_materials[self.mat_uid_ref]
            except:
                return self.__material_by_ref

        return self.__material_by_ref

    @property
    def node(self):
        """ returns the node this channels belongs to from cache or uid or returns None if it doesn't exist """
        global cached_nodes
        if self.uid in cached_nodes:
            if cached_nodes[self.uid].name in self.mat.name:
                return cached_nodes[self.uid]

        for node in self.mat.node_tree.nodes:
            if hasattr(node, "node_tree") and node.node_tree.uid == self.uid:
                cached_nodes[self.uid] = node
                return node

        return None


    #reference to the uid of the material this layer is in
    mat_uid_ref: bpy.props.StringProperty()

    # uid reference to this layer which matches the uid of the layer node group
    uid: bpy.props.StringProperty(name="UID",
                                  description="UID of this layer. Empty if it hasn't been used by LP yet",
                                  default="")

    # type of this layer which defines the inner structure of the layer
    layer_type: bpy.props.EnumProperty(name="Layer Type",
                                       description="The type of this layer",
                                       items=[("FILL", "Fill", "Fill Layer"),
                                              ("PAINT", "Paint", "Paint Layer")])


    def init(self, ngroup, layer_type, mat_uid):
        """ called immediately after adding the layer to set it up """
        self.uid = utils.make_uid()
        ngroup.uid = self.uid

        self.layer_type = layer_type

        self.mat_uid_ref = mat_uid

        layer_setup.group_setup(self.node)
        layer_channels.setup(self)
        
    
    ### get values
    def has_channel_input(self, channel_uid):
        """ returns if this layer has an input for the given channel uid """
        if not self.node: raise f"Couldn't find layer node for '{self.name}'. Delete the layer to proceed."
        for out in enumerate(self.node.node_tree.nodes[constants.INPUT_NAME].outputs):
            if hasattr(out, "uid") and out.uid == channel_uid:
                return True
        return False

    def get_channel_input_index(self, channel_uid):
        """ returns the index of the channel input with the given uid """
        if not self.node: raise f"Couldn't find layer node for '{self.name}'. Delete the layer to proceed."
        for i, out in enumerate(self.node.node_tree.nodes[constants.INPUT_NAME].outputs):
            if hasattr(out, "uid") and out.uid == channel_uid:
                return i
        return -1

    def get_channel_output_index(self, channel_uid):
        """ returns the index of the channel output with the given uid """
        if not self.node: raise f"Couldn't find layer node for '{self.name}'. Delete the layer to proceed."
        for i, inp in enumerate(self.node.node_tree.nodes[constants.OUTPUT_NAME].inputs):
            if hasattr(inp, "uid") and inp.uid == channel_uid:
                return i
        return -1

    def get_channel_endpoint_indices(self, channel_uid):
        """ returns the indices for the channel in and output for the given uid """
        return self.get_channel_input_index(channel_uid), self.get_channel_output_index(channel_uid)
    
    
    ### get sockets and nodes
    def get_layer_opacity_socket(self):
        """ returns this layers opacity node socket """
        if not self.node: raise f"Couldn't find layer node for '{self.name}'. Delete the layer to proceed."
        return self.node.node_tree.nodes[constants.OPAC_NAME].inputs[0]

    def get_mask_input(self, channel):
        """ returns the input for the given channel uid or 'LAYER' """
        if not self.node: raise f"Couldn't find layer node for '{self.name}'. Delete the layer to proceed."
        if channel == "LAYER":
            return self.node.node_tree.nodes[constants.OPAC_NAME].inputs[2]
        else:
            if self.layer_type == "FILL":
                return layer_fill.get_channel_mask_socket(self, channel)
            elif self.layer_type == "PAINT":
                pass # TODO for paint layer

    def __get_socket_mask_nodes(self, input):
        """ returns all masks connected to a given linked socket """
        nodes = []
        mask = input.links[0].from_node
        while mask.inputs[0].is_linked:
            nodes.append(mask)
            mask = mask.inputs[0].links[0].from_node
        nodes.append(mask)
        return nodes

    def __get_layer_mask_nodes(self):
        """ returns a list of nodes for the layers mask nodes """
        nodes = []
        socket = self.node.node_tree.nodes[constants.OPAC_NAME].inputs[2]
        if socket.is_linked:
            nodes = self.__get_socket_mask_nodes(socket)
        return nodes

    def __get_channel_mask_nodes(self, channel_uid):
        """ returns a list of nodes for the channels mask nodes """
        nodes = []
        if self.layer_type == "FILL":
            socket = layer_fill.get_channel_mask_socket(self, channel_uid)
            if socket.is_linked:
                nodes = self.__get_socket_mask_nodes(socket)
        elif self.layer_type == "PAINT":
            pass # TODO for paint layer
        return nodes

    def get_mask_nodes(self, channel):
        """ returns a list of nodes which match the masks added to the given channel uid or 'LAYER' """
        if not self.node: raise f"Couldn't find layer node for '{self.name}'. Delete the layer to proceed."
        # TODO (noted by Joshua) cache these in some form. Called a lot in the mask ui right now. Should be fairly fast but could be optimized
        if channel == "LAYER":
            return self.__get_layer_mask_nodes()
        else:
            return self.__get_channel_mask_nodes(channel)

    def get_filter_nodes(self, channel):
        """ returns a list of nodes which match the filters added to the given channel uid or 'LAYER' """
        if not self.node: raise f"Couldn't find layer node for '{self.name}'. Delete the layer to proceed."
        return []
    
    
    ### update appearance
    def __update_channel_socket_names(self, changed_channel):
        """ finds the channel endpoints for the given channel and updates their name """
        inp_index, out_index = self.get_channel_endpoint_indices(changed_channel.uid)
        self.node.node_tree.inputs[inp_index].name = changed_channel.name
        self.node.node_tree.outputs[out_index].name = changed_channel.name
        
    def update_channel_appearance(self, changed_channel):
        """ updates the appearance on the layer node for the given channel """
        if not self.node: raise f"Couldn't find layer node for '{self.name}'. Delete the layer to proceed."
        self.__update_channel_socket_names(changed_channel)


    # node utility
    def texture_setup(self):
        """ sets up texture nodes and returns the texture node """
        tex = self.node.node_tree.nodes.new(constants.NODES["TEX"])
        mapp = self.node.node_tree.nodes.new(constants.NODES["MAPPING"])
        coord = self.node.node_tree.nodes.new(constants.NODES["COORDS"])

        self.node.node_tree.links.new(coord.outputs["UV"], mapp.inputs[0])
        self.node.node_tree.links.new(mapp.outputs[0], tex.inputs[0])
        return tex
        
        
    ### move layer
    def move_up(self):
        """ moves this channels nodes up one spot """
        below = self.mat.lp.layer_below(self, 2)
        if below and not below.node: raise f"Couldn't find layer node for '{below.name}'. Delete the layer to proceed."

        above = self.mat.lp.layer_below(self, 1)
        if above and not above.node: raise f"Couldn't find layer node for '{above.name}'. Delete the layer to proceed."

        if above:
            layer_channels.disconnect_outputs(above)

        layer_channels.disconnect_outputs(self)
        layer_channels.connect_channel_outputs(self)

        if below:
            layer_channels.disconnect_outputs(below)

        if above:
            layer_channels.connect_channel_outputs(above)

        if below:
            layer_channels.connect_channel_outputs(below)

    def move_down(self):
        """ moves this channels nodes down one spot """
        below = self.mat.lp.layer_above(self, 1)
        if below and not below.node: raise f"Couldn't find layer node for '{below.name}'. Delete the layer to proceed."

        bottom = self.mat.lp.layer_below(self, 1)
        if bottom and not bottom.node: raise f"Couldn't find layer node for '{bottom.name}'. Delete the layer to proceed."

        layer_channels.disconnect_outputs(below)
        layer_channels.disconnect_outputs(self)
        layer_channels.connect_channel_outputs(below)

        if bottom:
            layer_channels.disconnect_outputs(bottom)

        layer_channels.connect_channel_outputs(self)

        if bottom:
            layer_channels.connect_channel_outputs(bottom)


    ### texture mapping - FILL LAYERS ONLY!!!
    def update_texture_mapping(self, context=None):
        """ updates the texture mapping for this layers images """
        # run through all channels and their nodes
        for channel in self.mat.lp.channels:
            tex, mapp, coords = layer_fill.get_channel_texture_nodes(self, channel.uid)
            if tex:
                
                # update projection and blend
                if self.tex_coords == "BOX":
                    tex.projection = "BOX"
                    tex.projection_blend = self.tex_blend
                else:
                    tex.projection = "FLAT"

                # update loc rot scale
                mapp.inputs[1].default_value = self.tex_location
                mapp.inputs[2].default_value = self.tex_rotation
                mapp.inputs[3].default_value = self.tex_scale

                # update mapping
                if self.tex_coords == "UV":
                    self.node.node_tree.links.new(coords.outputs["UV"], mapp.inputs[0])
                elif self.tex_coords == "BOX":
                    self.node.node_tree.links.new(coords.outputs["Object"], mapp.inputs[0])
                elif self.tex_coords == "GENERATED":
                    self.node.node_tree.links.new(coords.outputs["Generated"], mapp.inputs[0])

    tex_coords: bpy.props.EnumProperty(name="Mapping",
                                       description="Coordinates to use for the texture mapping",
                                       items=[("UV", "Uv", "Uv coordinates"),
                                              ("BOX", "Box", "Box/Object mapping"),
                                              ("GENERATED", "Generated", "Generated coordinates")],
                                       update=update_texture_mapping)

    tex_location: bpy.props.FloatVectorProperty(name="Location",
                                                description="The location of the texture mapping",
                                                default=(0, 0, 0),
                                                unit="LENGTH",
                                                update=update_texture_mapping)

    tex_rotation: bpy.props.FloatVectorProperty(name="Rotation",
                                                description="The rotation of the texture mapping",
                                                default=(0, 0, 0),
                                                unit="ROTATION",
                                                update=update_texture_mapping)

    tex_scale: bpy.props.FloatVectorProperty(name="Scale",
                                             description="The scale of the texture mapping",
                                             default=(1, 1, 1),
                                             update=update_texture_mapping)

    tex_blend: bpy.props.FloatProperty(name="Blend",
                                       description="Blend factor for the object mapping",
                                       default=0,
                                       min=0, max=1,
                                       update=update_texture_mapping)


    ### assets
    def __add_asset_group_node(self, asset_data):
        node = self.node.node_tree.nodes.new(constants.NODES["GROUP"])
        node.node_tree = utils_import.get_hidden_group_copy(os.path.join(constants.ASSET_LOC, asset_data.blend_file), asset_data.name)
        node.label = asset_data.name
        return node

    def __remove_asset_node(self, node):
        """ removes the given asset node from the tree as well as its group """
        group = node.node_tree
        
        from_socket = None
        if node.inputs[0].is_linked:
            from_socket = node.inputs[0].links[0].from_socket
        to_socket = node.outputs[0].links[0].to_socket

        self.node.node_tree.nodes.remove(node)
        if group.users == 0:
            bpy.data.node_groups.remove(group)

        if from_socket and to_socket:
            self.node.node_tree.links.new(from_socket, to_socket)

    def __move_asset_node_up(self, node):
        """ moves the given asset node up (make sure that not top asset before this!!!) """
        above = node.outputs[0].links[0].to_node
        to_socket = above.outputs[0].links[0].to_socket

        self.node.node_tree.links.remove(above.outputs[0].links[0])
        self.node.node_tree.links.remove(node.outputs[0].links[0])

        from_socket = None
        if node.inputs[0].is_linked:
            from_socket = node.inputs[0].links[0].from_socket
            self.node.node_tree.links.remove(from_socket.links[0])

        self.node.node_tree.links.new(node.outputs[0], to_socket)
        self.node.node_tree.links.new(above.outputs[0], node.inputs[0])
        if from_socket:
            self.node.node_tree.links.new(from_socket, above.inputs[0])

    def __move_asset_node_down(self, node):
        """ moves the given asset node down (make sure that not bottom asset before this!!!) """
        below = node.inputs[0].links[0].from_node
        to_socket = node.outputs[0].links[0].to_socket

        self.node.node_tree.links.remove(node.outputs[0].links[0])
        self.node.node_tree.links.remove(node.inputs[0].links[0])

        from_socket = None
        if below.inputs[0].is_linked:
            from_socket = below.inputs[0].links[0].from_socket
            self.node.node_tree.links.remove(below.inputs[0].links[0])

        self.node.node_tree.links.new(below.outputs[0], to_socket)
        self.node.node_tree.links.new(node.outputs[0], below.inputs[0])
        if from_socket:
            self.node.node_tree.links.new(from_socket, node.inputs[0])

    def __move_asset_node(self, node, move_up):
        """ moves the given asset node up or down """
        if not self.node: raise f"Couldn't find layer node for '{self.name}'. Delete the layer to proceed."
        if move_up:
            self.__move_asset_node_up(node)
        else:
            self.__move_asset_node_down(node)

    ### masks
    def add_mask(self, mask_data, has_blend):
        """ gets the mask data properties and adds this mask to the top of the stack """
        if not self.node: raise f"Couldn't find layer node for '{self.name}'. Delete the layer to proceed."

        # add mask node
        node = self.__add_asset_group_node(mask_data)
        to_socket = self.get_mask_input(utils.active_material(bpy.context).lp.channel)

        # add blend mode to mask
        if has_blend:
            self.__add_blend_mode_to_mask(node)

        # link mask node
        if to_socket.is_linked:
            self.node.node_tree.links.new(to_socket.links[0].from_socket, node.inputs[0])
        self.node.node_tree.links.new(node.outputs[0], to_socket)

    def remove_mask(self, mask_node):
        """ removes the given mask node and its group """
        if not self.node: raise f"Couldn't find layer node for '{self.name}'. Delete the layer to proceed."
        self.__remove_asset_node(mask_node)
        self.get_layer_opacity_socket().default_value = self.get_layer_opacity_socket().default_value # trigger viewport update to reflect removed mask

    def move_mask(self, mask_node, move_up):
        """ moves the given mask group up or down """
        if not self.node: raise f"Couldn't find layer node for '{self.name}'. Delete the layer to proceed."
        self.__move_asset_node(mask_node, move_up)

    def is_group_top_mask(self, mask_group, channel):
        """ returns if the given group is the top mask or not """
        if not self.node: raise f"Couldn't find layer node for '{self.name}'. Delete the layer to proceed."
        return mask_group == self.get_mask_nodes(channel)[0]

    def is_group_bottom_mask(self, mask_group, channel):
        """ returns if the given group is the top mask or not """
        if not self.node: raise f"Couldn't find layer node for '{self.name}'. Delete the layer to proceed."
        return mask_group == self.get_mask_nodes(channel)[-1]

    def __link_mask_blend_node(self, ntree, mix, group_in, group_out):
        from_socket = group_out.inputs[0].links[0].from_socket
        ntree.links.remove(group_out.inputs[0].links[0])

        ntree.links.new(group_in.outputs[0], mix.inputs[1])
        ntree.links.new(from_socket, mix.inputs[2])
        ntree.links.new(mix.outputs[0], group_out.inputs[0])


    def __add_blend_mode_to_mask(self, mask_node):
        """ adds a mix node as well as previous mask input to the mask node and node group """
        if not self.node: raise f"Couldn't find layer node for '{self.name}'. Delete the layer to proceed."
        mask_node.node_tree.inputs.new(constants.SOCKETS["FLOAT_FACTOR"], "Mask In")
        mask_node.node_tree.inputs.move(len(mask_node.node_tree.inputs)-1, 0)
        mask_node.inputs[0].default_value = 1
        
        # add mix node
        mix = mask_node.node_tree.nodes.new(constants.NODES["MIX"])
        mix.name = constants.MIX_MASK
        mix.label = constants.MIX_MASK
        mix.inputs[0].default_value = 1
        mix.blend_type = "MULTIPLY"

        # find group in and out nodes
        group_in = None
        group_out = None
        for node in mask_node.node_tree.nodes:
            if node.bl_idname == constants.NODES["GROUP_IN"]:
                group_in = node
            elif node.bl_idname == constants.NODES["GROUP_OUT"]:
                group_out = node

        # link mix node
        if group_in and group_out:
            self.__link_mask_blend_node(mask_node.node_tree, mix, group_in, group_out)


    ### filters
    def add_filter(self, filter_data):
        """ gets the filter data properties and adds this filter to the top of the stack """
        if not self.node: raise f"Couldn't find layer node for '{self.name}'. Delete the layer to proceed."
        print(filter_data.name)

    def remove_filter(self, filter_node):
        """ removes the given filter node and its group """
        if not self.node: raise f"Couldn't find layer node for '{self.name}'. Delete the layer to proceed."
        self.__remove_asset_node(filter_node)

    def move_filter(self, filter_node, move_up):
        """ moves the given filter group up or down """
        if not self.node: raise f"Couldn't find layer node for '{self.name}'. Delete the layer to proceed."
        self.__move_asset_node(filter_node, move_up)
