import bpy

from layer_painter.ui import utils_ui


class LP_PT_MaterialPanel(bpy.types.Panel):
    bl_idname = "LP_PT_MaterialPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Layer Painter"
    bl_label = ""
    bl_order = 0
    
    @classmethod
    def poll(cls, context):
        return utils_ui.base_poll(context)

    def draw_header(self, context):
        self.layout.label(text=f"{context.active_object.name} Materials")

    def draw(self, context):
        layout = self.layout
        ob = context.active_object

        # material slots on active object
        row = layout.row()
        row.template_list("MATERIAL_UL_matslots", "", ob, "material_slots", ob, "active_material_index", rows=3)
        
        # add and remove material
        col = row.column(align=True)
        col.operator("object.material_slot_add", icon='ADD', text="")
        col.operator("object.material_slot_remove", icon='REMOVE', text="")
        
        # select active material
        layout.template_ID(ob, "active_material", new="material.new")