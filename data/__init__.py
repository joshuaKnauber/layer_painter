import bpy
from . import material, layer, channel


classes = (
    channel.LP_ChannelProperties,
    layer.LP_LayerProperties,
    material.LP_MaterialProperties,
)
reg_classes, unreg_classes = bpy.utils.register_classes_factory(classes)


def register():
    reg_classes()
    
    bpy.types.NodeSocketFloat.uid = bpy.props.StringProperty()
    bpy.types.NodeSocketFloatFactor.uid = bpy.props.StringProperty()
    bpy.types.NodeSocketColor.uid = bpy.props.StringProperty()
    bpy.types.Material.lp = bpy.props.PointerProperty(type=material.LP_MaterialProperties)
    bpy.types.ShaderNodeTree.uid = bpy.props.StringProperty()


def unregister():
    del bpy.types.NodeSocketFloat.uid
    del bpy.types.NodeSocketFloatFactor.uid
    del bpy.types.NodeSocketColor.uid
    del bpy.types.ShaderNodeTree.uid
    del bpy.types.Material.lp
    
    unreg_classes()