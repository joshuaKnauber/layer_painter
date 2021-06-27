import bpy


def base_poll(context):
    """ basic poll function for all lp panels """
    return context.active_object and context.active_object.type == "MESH"


def draw_lp_group(layout, group_node, preview=False):
    """ draws the given node group as an lp group, for example a mask """
    col = layout.column()
    col.use_property_split = True
    col.use_property_decorate = False

    not_hidden = True
    for i, inp in enumerate(group_node.inputs):
        interface_inp = group_node.node_tree.inputs[i]
        
        if interface_inp.lp_group.mode == "INPUT":
            if not_hidden:
                layout.prop(inp, "default_value", text=inp.name)
        
        elif interface_inp.lp_group.mode == "LABEL":
            if not_hidden:
                layout.separator(factor=0.5)
                layout.label(text=inp.name)
        
        elif interface_inp.lp_group.mode == "SECTION":
            layout.separator(factor=0.5)
            hide_icon = "DISCLOSURE_TRI_DOWN" if interface_inp.lp_group.expand_section else "DISCLOSURE_TRI_RIGHT"
            layout.prop(interface_inp.lp_group, "expand_section", text=inp.name, icon=hide_icon, emboss=False)
            not_hidden = interface_inp.lp_group.expand_section
            
        elif interface_inp.lp_group.mode == "TEX":
            if not_hidden:
                row = layout.row()
                split = row.split(factor=0.25)
                
                if preview:
                    row.enabled = False
                    split.label(text=inp.name)
                    split.template_ID(bpy.context.scene.lp, "group_preview_image", new="image.new", open="image.open")

                else:
                    pass # TODO