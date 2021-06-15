import bpy
from .. import constants


class LP_FillLayerProperties(bpy.types.PropertyGroup):
        
        
    def setup_value_node(self, layer_ntree, channel, mix):
        """ setup the value node for the fill layer """
        if type(channel.inp.default_value) == float:
            value = layer_ntree.nodes.new( constants.NODES["MIX"] )
            value.inputs[0].default_value = channel.inp.default_value
            value.inputs[1].default_value = (0,0,0,1)
            value.inputs[2].default_value = (1,1,1,1)

        else:
            value = layer_ntree.nodes.new( constants.NODES["RGB"] )
            value.outputs[0].default_value = channel.inp.default_value

        layer_ntree.links.new( value.outputs[0], mix.inputs[2] )