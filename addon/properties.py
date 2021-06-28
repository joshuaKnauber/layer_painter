import bpy


class LP_AddonProperties(bpy.types.PropertyGroup):

    layer_nav: bpy.props.EnumProperty(name="Navigation",
                                      description="Choose which tab to show",
                                      items=[("LAYER", "Layer", "Layer settings"),
                                             ("MASKS", "Masks", "Mask settings"),
                                             ("FILTERS", "Filters", "Filter settings")])

    expand_mapping: bpy.props.BoolProperty(name="Expand",
                                           description="Show the mapping settings of the layer",
                                           default=True)

    # Used to show in the group drawing preview as a placeholder
    group_preview_image: bpy.props.PointerProperty(type=bpy.types.Image)
