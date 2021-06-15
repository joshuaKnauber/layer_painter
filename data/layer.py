import bpy
from ..utils import make_uid
from . import group_utils
from . import node_utils
from .. import constants
from .fill_layer import LP_FillLayerProperties
from .paint_layer import LP_PaintLayerProperties


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


    fill: bpy.props.PointerProperty(type=LP_FillLayerProperties)

    
    paint: bpy.props.PointerProperty(type=LP_PaintLayerProperties)
        
        
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
    
    
    def get_channel_opacity_socket(self, uid):
        """ returns the opacity nodes socket for the given channel uid """
        return self.get_channel_node(uid).inputs[0].links[0].from_node.inputs[0]
    
    
    def get_channel_value_socket(self, uid):
        """ returns the socket storing the value for the given channel uid """
        if self.layer_type == "FILL":
            channel_mix = self.get_channel_node( uid )
            value_node = channel_mix.inputs[2].links[0].from_node
            
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
        mix.mute = not channel.default_enable
        
        self.layer_ntree.links.new( group_inp, mix.inputs[1] )
        self.layer_ntree.links.new( mix.outputs[0], group_out )
        
        return mix
    
    
    def __add_channel_opacity(self, mix):
        """ adds the node controlling the opacity for the given channel node """
        opacity = self.layer_ntree.nodes.new( constants.NODES["MIX"] )
        
        opacity.inputs[0].default_value = 1
        opacity.inputs[1].default_value = (0,0,0,1)
        opacity.inputs[2].default_value = (1,1,1,1)
        
        self.layer_ntree.links.new( opacity.outputs[0], mix.inputs[0] )
        self.layer_ntree.links.new( self.layer_ntree.nodes[ constants.OPAC_NAME ].outputs[0], opacity.inputs[2] )

        return opacity
        
        
    def __create_fill_channel(self, channel):
        """ creates the nodes for the given channel in the form of a fill layer """
        mix = self.__add_channel_mix(channel)
        self.__add_channel_opacity(mix)

        self.fill.setup_value_node(self.layer_ntree, channel, mix)
        
        return self.node.inputs[-1], self.node.outputs[-1]
        
        
    def __create_paint_channel(self, channel):
        """ creates the nodes for the given channel in the form of a paint layer """
        mix = self.__add_channel_mix(channel)
        opacity = self.__add_channel_opacity(mix)

        self.paint.setup_value_node(self.layer_ntree, channel, mix) # TODO
        
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

        # remove channel opacity node. TODO: when has masks or paint layer looks different
        self.layer_ntree.nodes.remove(mix.inputs[0].links[0].from_node)
        
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