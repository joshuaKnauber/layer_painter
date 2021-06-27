import bpy
from . import material, layer, channel, group, mask


classes = (
    channel.LP_ChannelProperties,
    layer.LP_LayerProperties,
    material.LP_MaterialProperties,
    group.LP_AssetSocketProperties,
    group.LP_AssetProperties,
    mask.LP_MaskProperties,
)
reg_classes, unreg_classes = bpy.utils.register_classes_factory(classes)


def register():
    reg_classes()

    bpy.types.Material.lp = bpy.props.PointerProperty(
        type=material.LP_MaterialProperties)

    bpy.types.NodeSocketFloat.uid = bpy.props.StringProperty()
    bpy.types.NodeSocketFloatFactor.uid = bpy.props.StringProperty()
    bpy.types.NodeSocketColor.uid = bpy.props.StringProperty()

    bpy.types.NodeSocketInterfaceFloat.lp_group = bpy.props.PointerProperty(
        type=group.LP_AssetSocketProperties)
    bpy.types.NodeSocketInterfaceFloatFactor.lp_group = bpy.props.PointerProperty(
        type=group.LP_AssetSocketProperties)
    bpy.types.NodeSocketInterfaceColor.lp_group = bpy.props.PointerProperty(
        type=group.LP_AssetSocketProperties)

    bpy.types.ShaderNodeTree.uid = bpy.props.StringProperty()
    bpy.types.ShaderNodeTree.lp_group = bpy.props.PointerProperty(
        type=group.LP_AssetProperties)


def unregister():
    del bpy.types.Material.lp

    del bpy.types.NodeSocketFloat.uid
    del bpy.types.NodeSocketFloatFactor.uid
    del bpy.types.NodeSocketColor.uid

    del bpy.types.NodeSocketInterfaceFloat.lp_group
    del bpy.types.NodeSocketInterfaceFloatFactor.lp_group
    del bpy.types.NodeSocketInterfaceColor.lp_group

    del bpy.types.ShaderNodeTree.uid
    del bpy.types.ShaderNodeTree.lp_group

    unreg_classes()
