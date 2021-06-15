import bpy
from ..utils import make_uid
from . import group_utils
from . import node_utils
from .. import constants


cached_materials = {}
cached_nodes = {}

def clear_caches():
    global cached_materials
    cached_materials = {}
    global cached_nodes
    cached_nodes = {}


class LP_LayerProperties(bpy.types.PropertyGroup):
    
    
    @property
    def mat(self):
        global cached_materials
        if self.mat_uid_ref in cached_materials:
            return cached_materials[ self.mat_uid_ref ]
        
        for material in bpy.data.materials:
            if material.lp.uid == self.mat_uid_ref:
                cached_materials[ self.mat_uid_ref ] = material
                return material
            
            
    @property
    def node(self):
        global cached_nodes
        if self.uid in cached_nodes:
            if cached_nodes[ self.uid ].name in self.mat.name:
                return cached_nodes[ self.uid ]
        
        for node in self.mat.node_tree.nodes:
            if hasattr(node, "node_tree") and node.node_tree.uid == self.uid:
                cached_nodes[ self.uid ] = node
                return node
            
        return None
            
    @property
    def layer_ntree(self):
        if self.node:
            return self.node.node_tree
        return None
            
            
    mat_uid_ref: bpy.props.StringProperty()
    
    
    uid: bpy.props.StringProperty(name="UID",
                                        description="UID of this layer. Empty if it hasn't been used by LP yet",
                                        default="")
    
    
    layer_type: bpy.props.EnumProperty(name="Layer Type",
                                        description="The type of this layer",
                                        items=[("FILL","Fill","Fill Layer"),
                                            ("PAINT","Paint","Paint Layer")])
        
        
    def init(self, ngroup, layer_type, mat_uid):
        """ call immediately after adding the layer to set it up """
        self.uid = make_uid()
        ngroup.uid = self.uid
        
        self.mat_uid_ref = mat_uid
        
        self.layer_type = layer_type

        self.__add_layer_opacity()
        self.setup_channels()
        
        
    def get_layer_opacity_socket(self):
        """ returns this layers opacity nodes socket """
        return self.node.node_tree.nodes[ constants.OPAC_NAME ].inputs[0]
        
        
    def get_channel_node(self, uid):
        """ returns the channel node in this layer for the given channel uid """
        return self.node.node_tree.nodes[ uid ]
    
    
    def get_channel_tex_alpha_socket(self, uid):
        """ returns the texture alpha nodes socket for the given channel uid """
        return self.get_channel_node(uid).inputs[0].links[0].from_node.inputs[0]
    
    
    def get_channel_opacity_socket(self, uid):
        """ returns the opacity nodes socket for the given channel uid """
        return self.get_channel_tex_alpha_socket(uid).node.inputs[2].links[0].from_node.inputs[0]
    
    
    def get_channel_value_node(self, uid):
        """ returns the node storing the value for the given channel uid """
        if self.layer_type == "FILL":
            channel_mix = self.get_channel_node( uid )
            return channel_mix.inputs[2].links[0].from_node
            
        elif self.layer_type == "PAINT":
            return None #TODO?
        
        
    def __get_channel_texture_nodes(self, uid):
        """ returns the texture nodes for the given channel. Only use if you know this channel uses TEX data """
        tex = self.get_channel_value_node( uid )
        mapp = tex.inputs[0].links[0].from_node
        coords = mapp.inputs[0].links[0].from_node
        return tex, mapp, coords
    
    
    def get_channel_value_socket(self, uid):
        """ returns the socket storing the value for the given channel uid """
        value_node = self.get_channel_value_node( uid )
        
        if self.layer_type == "FILL":
            if value_node.bl_idname == constants.NODES["RGB"]:
                return value_node.outputs[0]
            
            elif value_node.bl_idname == constants.NODES["MIX"]:
                return value_node.inputs[0]
            
        elif self.layer_type == "PAINT":
            return None #TODO?
        
        
    def __add_layer_opacity(self):
        """ adds the node handling this layers opacity """
        opacity = self.layer_ntree.nodes.new( constants.NODES["MIX"] )
        
        opacity.name = constants.OPAC_NAME
        opacity.label = constants.OPAC_NAME
        opacity.location = (-350, -100)
        
        opacity.inputs[0].default_value = 1
        opacity.inputs[1].default_value = (0,0,0,1)
        opacity.inputs[2].default_value = (1,1,1,1)
        
        
    def __add_channel_endpoints(self, channel):
        """ adds the in and output for the given channel in this layer """
        inp, group_inp = group_utils.add_input(self.node, channel.inp.bl_rna.identifier, channel.name)
        inp.default_value = channel.inp.default_value
        _, group_out = group_utils.add_output(self.node, channel.inp.bl_rna.identifier, channel.name)
        return group_inp, group_out
        
        
    def __add_channel_mix(self, channel):
        """ adds the mix node representing the starting point for the given channel in this layer """
        group_inp, group_out = self.__add_channel_endpoints( channel )

        mix = self.layer_ntree.nodes.new( constants.NODES["MIX"] )
        mix.name = channel.uid
        mix.label = channel.uid
        mix.mute = not channel.default_enable
        
        self.layer_ntree.links.new( group_inp, mix.inputs[1] )
        self.layer_ntree.links.new( mix.outputs[0], group_out )
        
        return mix
    
    
    def __add_channel_opacity(self, mix):
        """ adds the node controlling the opacity for the given channel node """
        opacity = self.layer_ntree.nodes.new( constants.NODES["MIX"] )
        opacity.label = "Channel Opacity"
        
        opacity.inputs[0].default_value = 1
        opacity.inputs[1].default_value = (0,0,0,1)
        opacity.inputs[2].default_value = (1,1,1,1)

        tex_alpha = self.layer_ntree.nodes.new( constants.NODES["MIX"] )
        tex_alpha.label = "Texture Alpha"
        
        tex_alpha.inputs[0].default_value = 1
        tex_alpha.inputs[1].default_value = (0,0,0,1)
        tex_alpha.inputs[2].default_value = (1,1,1,1)
        
        self.layer_ntree.links.new( opacity.outputs[0], tex_alpha.inputs[2] )
        self.layer_ntree.links.new( tex_alpha.outputs[0], mix.inputs[0] )
        self.layer_ntree.links.new( self.layer_ntree.nodes[ constants.OPAC_NAME ].outputs[0], opacity.inputs[2] )

        return opacity
    
    
    def setup_fill_value_node(self, channel):
        """ setup the value node for the fill layer """
        if type(channel.inp.default_value) == float:
            value = self.layer_ntree.nodes.new( constants.NODES["MIX"] )
            value.inputs[0].default_value = channel.inp.default_value
            value.inputs[1].default_value = (0,0,0,1)
            value.inputs[2].default_value = (1,1,1,1)

        else:
            value = self.layer_ntree.nodes.new( constants.NODES["RGB"] )
            value.outputs[0].default_value = channel.inp.default_value

        return value
        
        
    def __create_fill_channel(self, channel):
        """ creates the nodes for the given channel in the form of a fill layer """
        mix = self.__add_channel_mix(channel)
        self.__add_channel_opacity(mix)

        value_node = self.setup_fill_value_node(channel)
        self.layer_ntree.links.new( value_node.outputs[0], mix.inputs[2] )
        
        return self.node.inputs[-1], self.node.outputs[-1]
    
    
    def setup_paint_value_node(self): # TODO
        """ setup the value node for the paint layer """
        tex = self.layer_ntree.nodes.new( constants.NODES["TEX"] )
        return tex
        
        
    def __create_paint_channel(self, channel):
        """ creates the nodes for the given channel in the form of a paint layer """
        mix = self.__add_channel_mix(channel)
        opacity = self.__add_channel_opacity(mix)

        tex = self.setup_paint_value_node() # TODO
        self.layer_ntree.links.new( tex.outputs[0], mix.inputs[2] )
        
        return self.node.inputs[-1], self.node.outputs[-1]
    
    
    def __create_channel(self, channel):
        """ creates the nodes for the given channel in this layer """
        if self.layer_type == "FILL":
            return self.__create_fill_channel(channel)
        
        elif self.layer_type == "PAINT":
            return self.__create_paint_channel(channel)
        
        
    def __connect_layer_output(self, channel, out):
        """ try to connect the given layer output to the correct input """
        above = self.mat.lp.layer_above(self)
        
        if not above:
            self.mat.node_tree.links.new( out, channel.inp )
            
        else:
            index = above.get_channel_endpoint_index( channel.uid )
            if index >= 0:
                self.mat.node_tree.links.new( out, above.node.inputs[index] )
        
        
    def __connect_layer_input(self, channel, inp):
        """ try to connect the given layer input to the correct output """
        below = self.mat.lp.layer_below(self)
        
        if below:
            index = below.get_channel_endpoint_index( channel.uid )
            if index >= 0:
                self.mat.node_tree.links.new( below.node.outputs[index], inp )
        
    
    def __create_untracked_channels(self):
        """ create all channels in the layer that haven't been added yet """
        for channel in self.mat.lp.channels:
            if not channel.uid in self.layer_ntree.nodes:

                inp, out = self.__create_channel(channel)
                self.__connect_layer_output( channel, out )
                self.__connect_layer_input( channel, inp )
                
                
    def disconnect_outputs(self):
        """ disconnects all the layers channel outputs """
        for channel in self.mat.lp.channels:
            index = self.get_channel_endpoint_index( channel.uid )
            for link in self.node.outputs[ index ].links:
                self.mat.node_tree.links.remove( link )
                
                
    def connect_channel_outputs(self):
        """ connects all channel outputs to the layer above """
        for channel in self.mat.lp.channels:
            index = self.get_channel_endpoint_index( channel.uid )
            self.__connect_layer_output( channel, self.node.outputs[index] )
            
            
    def __remove_channel(self, mix, socket_index):
        """ removes the nodes for the given channel mix node and socket """
        # remove channel value nodes
        node_utils.remove_connected_left(self.layer_ntree, mix.inputs[2].links[0].from_node)

        # remove channel opacity nodes
        tex_alpha = mix.inputs[0].links[0].from_node
        self.layer_ntree.nodes.remove(tex_alpha.inputs[2].links[0].from_node)
        self.layer_ntree.nodes.remove(tex_alpha)
        
        # remove channel endpoints
        self.layer_ntree.inputs.remove(self.layer_ntree.inputs[ socket_index ])
        self.layer_ntree.outputs.remove(self.layer_ntree.outputs[ socket_index ])
        
        self.layer_ntree.nodes.remove(mix)
        
        
    def __remove_orphan_channels(self, channel_uids):
        """ removes all channels that aren't in the given list of uids """
        for i in range( len(self.layer_ntree.inputs)-1, -1, -1 ):
            mix = self.layer_ntree.nodes[ constants.INPUT_NAME ].outputs[i].links[0].to_node
            if not mix.name in channel_uids:
                self.__remove_channel(mix, i)
                
                
    def get_channel_endpoint_index(self, uid):
        """ returns the channel endpoint indices for the given channel uid """
        for i in range( len(self.layer_ntree.inputs) ):
            if self.layer_ntree.nodes[ constants.INPUT_NAME ].outputs[i].links[0].to_node.name == uid:
                return i
        return -1

                
    def __update_channel_socket_names(self, changed_channel):
        """ finds the channel endpoints for the given channel and updates their name """
        index = self.get_channel_endpoint_index( changed_channel.uid )
        self.layer_ntree.inputs[ index ].name = changed_channel.name
        self.layer_ntree.outputs[ index ].name = changed_channel.name
                
        
    def setup_channels(self, changed_channel=None):
        """ setup the channels for a given one or all material channels """
        if changed_channel:
            self.__update_channel_socket_names( changed_channel )
        else:
            self.__create_untracked_channels()
            self.__remove_orphan_channels( self.mat.lp.channel_uids )
            
                
    def move_up(self):
        """ moves this channels nodes up one spot """
        below = self.mat.lp.layer_below( self, 2 )
        above = self.mat.lp.layer_below( self, 1 )

        if above:
            above.disconnect_outputs()
        
        self.disconnect_outputs()
        self.connect_channel_outputs()

        if below:
            below.disconnect_outputs()

        if above:
            above.connect_channel_outputs()
        
        if below:
            below.connect_channel_outputs()
        
        
    def move_down(self):
        """ moves this channels nodes down one spot """
        below = self.mat.lp.layer_above( self, 1 )
        bottom = self.mat.lp.layer_below( self, 1 )

        below.disconnect_outputs()

        self.disconnect_outputs()
        
        below.connect_channel_outputs()
        
        if bottom:
            bottom.disconnect_outputs()
        
        self.connect_channel_outputs()
        
        if bottom:
            bottom.connect_channel_outputs()
            
            
    def __texture_setup(self):
        """ sets up texture nodes and returns the texture node """
        tex = self.layer_ntree.nodes.new( constants.NODES["TEX"] )
        mapp = self.layer_ntree.nodes.new( constants.NODES["MAPPING"] )
        coord = self.layer_ntree.nodes.new( constants.NODES["COORDS"] )
        
        self.layer_ntree.links.new( coord.outputs["UV"], mapp.inputs[0] )
        self.layer_ntree.links.new( mapp.outputs[0], tex.inputs[0] )
        return tex
            
            
    def get_channel_data_type(self, channel_uid):
        """ returns the type of data that this channel is set to for this layer
        return in ("COL", "TEX")
        """
        node = self.get_channel_value_node( channel_uid )

        if node.bl_idname in [ constants.NODES["RGB"], constants.NODES["MIX"] ]:
            return "COL"
        
        elif node.bl_idname == constants.NODES["TEX"]:
            return "TEX"
        
    
    def cycle_channel_data_type(self, channel_uid):
        """ cycles the type of data this channel is set to in ("COL", "TEX") """
        data_type = self.get_channel_data_type( channel_uid )
        node = self.get_channel_value_node( channel_uid )
        connect_socket = node.outputs[0].links[0].to_socket

        node_utils.remove_connected_left( self.layer_ntree, node )

        if data_type == "COL":
            tex = self.__texture_setup()
            self.layer_ntree.links.new( tex.outputs[0], connect_socket )
            self.layer_ntree.links.new( tex.outputs[1], self.get_channel_tex_alpha_socket(channel_uid) )
            self.update_texture_mapping()
        
        elif data_type == "TEX":
            value_node = self.setup_fill_value_node( self.mat.lp.channel_by_uid(channel_uid) )
            self.layer_ntree.links.new( value_node.outputs[0], connect_socket )


    def update_texture_mapping(self, context=None):
        """ updates the texture mapping for this layers images """
        for channel in self.mat.lp.channels:
            if self.get_channel_data_type( channel.uid ) == "TEX":
                tex, mapp, coords = self.__get_channel_texture_nodes( channel.uid )
                
                if self.tex_coords == "BOX":
                    tex.projection = "BOX"
                    tex.projection_blend = self.tex_blend
                else:
                    tex.projection = "FLAT"
                    
                mapp.inputs[1].default_value = self.tex_location
                mapp.inputs[2].default_value = self.tex_rotation
                mapp.inputs[3].default_value = self.tex_scale
                
                if self.tex_coords == "UV":
                    self.layer_ntree.links.new( coords.outputs["UV"], mapp.inputs[0] )
                elif self.tex_coords == "BOX":
                    self.layer_ntree.links.new( coords.outputs["Object"], mapp.inputs[0] )
                elif self.tex_coords == "GENERATED":
                    self.layer_ntree.links.new( coords.outputs["Generated"], mapp.inputs[0] )
    
    
    tex_coords: bpy.props.EnumProperty(name="Mapping",
                                        description="Coordinates to use for the texture mapping",
                                        items=[("UV","Uv","Uv coordinates"),
                                               ("BOX","Box","Box/Object mapping"),
                                               ("GENERATED","Generated","Generated coordinates")],
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