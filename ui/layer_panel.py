import bpy
from . import interface_utils
from .. import utils


class LP_UL_Layers(bpy.types.UIList):
    
    def draw_faulty_layer(self, layout, mat, layer):
        layout.alert = True
        
        layout.label(text="Faulty layer found!", icon="ERROR")
        op = layout.operator("lp.remove_layer", text="", icon="TRASH", emboss=False)
        op.overwrite_uid = layer.uid
        op.material = mat.name
    
    def draw_layer(self, layout, layer):        
        hide_icon = "HIDE_ON" if layer.node.mute else "HIDE_OFF"
        layout.prop(layer.node, "mute", text="", invert_checkbox=True, icon=hide_icon, emboss=False)

        split = layout.split(factor=0.7)
        split.prop(layer.node, "label", text="", emboss=False)
        split.prop(layer.get_layer_opacity_socket(), "default_value", text="", slider=True, emboss=False)
    
    def draw_item(self, context, layout, data, layer, icon, active_data, active_propname):
        row = layout.row(align=True)
        mat = context.active_object.active_material
        
        if layer.node:
            self.draw_layer( row, layer )
        else:
            self.draw_faulty_layer( row, mat, layer )


class LP_PT_LayerPanel(bpy.types.Panel):
    bl_idname = "LP_PT_LayerPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Layer Painter"
    bl_label = ""
    bl_order = 1
    
    @classmethod
    def poll(cls, context):
        return interface_utils.base_poll(context) and utils.get_active_material(context) != None

    def draw_header(self, context):
        self.layout.label(text=f"{context.active_object.active_material.name} Layers")
        
    def draw_controls(self, layout, mat):
        box = layout.box()
        row = box.row()
        row.enabled = (not mat.lp.has_faulty_layers) and (not mat.lp.has_faulty_channels)
        
        sub_row = row.row(align=False)
        sub_row.operator("lp.add_fill_layer", text="", icon="FILE_NEW", emboss=False).material = mat.name
        # sub_row.operator("lp.add_paint_layer", text="", icon="BRUSH_DATA", emboss=False).material = mat.name

        sub_row = row.row(align=False)
        sub_row.alignment = "CENTER"
        sub_row.operator("lp.move_layer_up", text="", icon="TRIA_UP", emboss=False).material = mat.name
        sub_row.operator("lp.move_layer_down", text="", icon="TRIA_DOWN", emboss=False).material = mat.name

        sub_row = row.row(align=False)
        sub_row.alignment = "RIGHT"
        sub_row.operator("lp.remove_layer", text="", icon="TRASH", emboss=False).material = mat.name

    def draw(self, context):
        mat = utils.get_active_material(context)
        layout = self.layout
        col = layout.column(align=True)
        
        self.draw_controls(col, mat)
        
        if not mat.lp.has_faulty_channels:
            row = col.row(align=True)
            row.scale_y = 1.25
            row.template_list("LP_UL_Layers", "material_layers",
                                mat.lp, "layers",
                                mat.lp, "selected",rows=3,sort_reverse=True)
                
            if len(mat.lp.layers) == 0:
                col.label(text="No layers added", icon="INFO")

        else:
            box = col.box()
            box.alert = True
            box.label(text="Faulty channels found!", icon="ERROR")
            box.operator("lp.switch_to_node_editor", icon="WINDOW", text="Edit channels")