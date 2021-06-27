import bpy
from . import interface_utils
from .. import utils


class LP_PT_LayerSettingsPanel(bpy.types.Panel):
    bl_idname = "LP_PT_LayerSettingsPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Layer Painter"
    bl_label = ""
    bl_order = 2
    
    @classmethod
    def poll(cls, context):
        mat = utils.get_active_material(context)
        if interface_utils.base_poll(context) and mat != None:
            if mat.lp.active != None:
                return (not mat.lp.has_faulty_layers) and (not mat.lp.has_faulty_channels)
        return False

    def draw_header(self, context):
        self.layout.label(text=f"{context.active_object.active_material.lp.active.node.label} Settings")


    def draw(self, context):
        layout = self.layout
        mat = utils.get_active_material(context)
        layer = mat.lp.active
        
        # NO CHANNELS
        if len(mat.lp.channels) == 0:
            row = layout.row()
            row.scale_y = 1.5
            row.operator("lp.pbr_setup", icon="ADD").material = mat.name
            layout.operator("lp.switch_to_node_editor", icon="WINDOW", text="Edit custom channels")
        
        # LAYER SETTINGS
        else:
            row = layout.row()
            row.scale_y = 1.2
            row.prop(context.scene.lp, "layer_nav", expand=True)
            layout.separator(factor=1)
            
            # LAYER SETTINGS
            if context.scene.lp.layer_nav == "LAYER":

                # LAYER MAPPING
                self.draw_mapping(layout, context, layer)
                layout.separator(factor=1)
                
                for channel in mat.lp.channels:
                    channel_mix = layer.get_channel_node( channel.uid )
                    self.draw_channel(layout, mat, layer, channel, channel_mix)

            # MASK SETTINGS
            elif context.scene.lp.layer_nav == "MASKS":
                self.draw_masks(layout, mat, layer)
            
            # FILTER SETTINGS
            elif context.scene.lp.layer_nav == "FILTERS":
                layout.label(text="Placeholder")
                
                
    def draw_mapping(self, layout, context, layer):
        box = layout.box()
        row = box.row()
        expand_icon = "TRIA_DOWN" if context.scene.lp.expand_mapping else "TRIA_RIGHT"
        row.prop(context.scene.lp, "expand_mapping", text="", emboss=False, icon=expand_icon)
        
        row.prop(layer, "tex_coords", text="")

        if context.scene.lp.expand_mapping:
            if layer.tex_coords == "BOX":
                row.prop(layer, "tex_blend", slider=True)

            row = box.row()
            
            col = row.column()
            col.prop(layer, "tex_location")
            col = row.column()
            col.prop(layer, "tex_rotation")
            col = row.column()
            col.prop(layer, "tex_scale")


    def draw_channel(self, layout, mat, layer, channel, channel_mix):
        box = layout.box()
        row = box.row(align=True)
        
        hide_icon = "CHECKBOX_DEHLT" if channel_mix.mute else "CHECKBOX_HLT"
        row.prop(channel_mix, "mute", text="", invert_checkbox=True, icon=hide_icon, emboss=False)
        
        split = row.split(factor=0.45)
        split.label(text=channel.name)
        
        if not channel_mix.mute:
            row = split.row()
            row.prop(channel_mix, "blend_type", text="", emboss=False)
            row.prop(layer.get_channel_opacity_socket( channel.uid ), "default_value", text="", slider=True)

            row = box.row(align=True)
            
            data_type = mat.lp.get_channel_data_type(layer, channel.uid)

            data_icon = "SHADING_RENDERED" if data_type == "COL" else "SHADING_TEXTURE"
            op = row.operator("lp.cycle_channel_data", text="", icon=data_icon)
            op.material = mat.name
            op.layer_uid = layer.uid
            op.channel_uid = channel.uid
            
            if data_type == "COL":
                row.prop(layer.get_channel_value_socket( channel.uid ), "default_value", text="", slider=True)

            elif data_type == "TEX":
                row.template_ID(layer.get_channel_value_node( channel.uid ), "image", new="image.new", open="image.open")
                
                
    def draw_masks(self, layout, mat, layer):
        pass