import bpy


class LP_AssetProperties(bpy.types.PropertyGroup):
    
    name: bpy.props.StringProperty(name="Name", description="Name of the asset and node group")
    
    blend_file: bpy.props.StringProperty(name="Blend File Name")
    
    asset_type: bpy.props.EnumProperty(name="Asset Type",
                                       description="Type of the asset",
                                       items=[("MASK","Mask","Mask"),
                                              ("FILTER","Filter","Filter")])

    thumbnail: bpy.props.StringProperty(name="Thumbnail",
                                    description="Thumbnail for this asset",
                                    subtype="FILE_PATH")