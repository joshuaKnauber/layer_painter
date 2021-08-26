import bpy

from .... import utils, constants
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


    ### masks
    def add_mask(self, mask_data):
        """ gets the mask data properties and adds this mask to the top of the stack """
        print(mask_data.name)


    ### filters
    def add_filter(self, filter_data):
        """ gets the filter data properties and adds this filter to the top of the stack """
        print(filter_data.name)