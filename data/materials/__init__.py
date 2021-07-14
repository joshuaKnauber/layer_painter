import bpy
from . import channels, layers, material


classes = (
    material.LP_MaterialProperties,
)
reg_classes, unreg_classes = bpy.utils.register_classes_factory(classes)


def register():
    channels.register()
    layers.register()
    reg_classes()
    
    bpy.types.Material.lp = bpy.props.PointerProperty(type=material.LP_MaterialProperties)

    bpy.types.NodeSocketFloat.uid = bpy.props.StringProperty()
    bpy.types.NodeSocketFloatFactor.uid = bpy.props.StringProperty()
    bpy.types.NodeSocketColor.uid = bpy.props.StringProperty()
    bpy.types.NodeSocketVector.uid = bpy.props.StringProperty()

    bpy.types.ShaderNodeTree.uid = bpy.props.StringProperty()


def unregister():
    del bpy.types.Material.lp

    del bpy.types.NodeSocketFloat.uid
    del bpy.types.NodeSocketFloatFactor.uid
    del bpy.types.NodeSocketColor.uid
    del bpy.types.NodeSocketVector.uid

    del bpy.types.ShaderNodeTree.uid
    
    channels.unregister()
    layers.unregister()
    unreg_classes()
