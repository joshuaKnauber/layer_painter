import bpy


class LP_MaskProperties(bpy.types.PropertyGroup):

    name: bpy.props.StringProperty(name="Name",
                                   description="Name of the asset group")

    blend_name: bpy.props.StringProperty(name="Blend Name",
                                    description="Name of the blend file this asset comes from")
    
    path_name: bpy.props.StringProperty(name="Asset Path Name")