import bpy


class LP_AssetProperties(bpy.types.PropertyGroup):

    def update_group_status(self, context):
        """ updates the node this group belongs to to reflect its status """
        for node in context.space_data.node_tree.nodes:
            if hasattr(node, "node_tree") and node.node_tree == self.id_data:

                if self.is_mask:
                    node.use_custom_color = True
                    node.color = (0.5, 1, 0.7)
                else:
                    node.use_custom_color = False

    is_mask: bpy.props.BoolProperty(name="LP Mask",
                                    description="Makes this group into a layer painter mask",
                                    default=False,
                                    update=update_group_status)

    thumbnail: bpy.props.PointerProperty(
        type=bpy.types.Image, name="Thumbnail")


class LP_AssetSocketProperties(bpy.types.PropertyGroup):

    mode: bpy.props.EnumProperty(name="Mode",
                                 description="Mode of this input",
                                 items=[("INPUT", "Input", "Use this input as the value", "NODE", 0),
                                        ("TEX", "Texture",
                                         "Use texture input", "FILE_IMAGE", 1),
                                        ("LABEL", "Label",
                                         "Make this input a label", "SMALL_CAPS", 2),
                                        ("SECTION", "Section", "Use this input as a section divider", "ALIGN_TOP", 3)])

    expand_section: bpy.props.BoolProperty(name="Expand",
                                           description="Expand section",
                                           default=False)
