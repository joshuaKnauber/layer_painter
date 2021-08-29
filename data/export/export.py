import bpy


class LP_BakeProperties(bpy.types.PropertyGroup):

    resolution: bpy.props.IntProperty(name="Resolution",
                                    description="Resolution of the baked images",
                                    default=2048,
                                    min=2)

    base_color: bpy.props.FloatVectorProperty(name="Base Color",
                                    description="Background color to fill the baked images with",
                                    size=4,
                                    subtype="COLOR",
                                    default=(0,0,0,1))

    directory: bpy.props.StringProperty(name="Save Path",
                                    description="Path to save the baked images to",
                                    subtype="DIR_PATH",
                                    default="//")