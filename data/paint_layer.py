import bpy
from .. import constants


class LP_PaintLayerProperties(bpy.types.PropertyGroup):
        
    
    def setup_value_node(self, layer_ntree, channel, mix):
        """ setup the value node for the paint layer """
        value = layer_ntree.nodes.new( constants.NODES["TEX"] )
        layer_ntree.links.new( value.outputs[0], mix.inputs[2] )