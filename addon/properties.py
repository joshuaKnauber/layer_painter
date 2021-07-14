import bpy


class LP_AddonProperties(bpy.types.PropertyGroup):

    # navigation enum for the layer settings
    layer_nav: bpy.props.EnumProperty(name="Navigation",
                                      description="Choose which tab to show",
                                      items=[("LAYER", "Layer", "Layer settings"),
                                             ("MASKS", "Masks", "Mask settings"),
                                             ("FILTERS", "Filters", "Filter settings")])

    # expand toggle for the mapping settings
    expand_mapping: bpy.props.BoolProperty(name="Expand",
                                           description="Show the mapping settings of the layer",
                                           default=True)