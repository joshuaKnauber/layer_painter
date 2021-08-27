import bpy

from .. import utils
from ..operators import utils_operator


class LP_OT_AddMask(bpy.types.Operator):
    bl_idname = "lp.add_mask"
    bl_label = "Add Mask"
    bl_description = "Adds a mask"
    bl_options = {"REGISTER", "INTERNAL"}
    
    @classmethod
    def poll(cls, context):
        mat = utils.active_material(context)
        return utils_operator.base_poll(context) and mat.lp.selected

    def get_selected_asset(self, context):
        index = int(context.scene.lp.masks)
        if index < len(context.scene.lp.mask_assets):
            return context.scene.lp.mask_assets[index]
        else:
            return context.scene.lp.filter_assets[index - len(context.scene.lp.mask_assets) - 1]

    def execute(self, context):
        if len(context.scene.lp.mask_assets) + len(context.scene.lp.filter_assets) > 0:
            index = int(context.scene.lp.masks)
            if index < len(context.scene.lp.mask_assets):
                utils.active_material(context).lp.selected.add_mask( self.get_selected_asset(context), True )
            else:
                utils.active_material(context).lp.selected.add_mask( self.get_selected_asset(context), False )
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout

        if len(context.scene.lp.mask_assets) + len(context.scene.lp.filter_assets) > 0:
            box = layout.box()
            col = box.column(align=True)
            col.template_icon_view(context.scene.lp, "masks", show_labels=True, scale=7)
            row = col.row()
            row.label(text=self.get_selected_asset(context).name)
        else:
            layout.label(text="No assets. Add a file in the preferences.", icon="ERROR")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=300)


class LP_OT_RemoveMask(bpy.types.Operator):
    bl_idname = "lp.remove_mask"
    bl_label = "Remove Mask"
    bl_description = "Removes this mask"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}
    
    node_name: bpy.props.StringProperty(options={"HIDDEN"})

    @classmethod
    def poll(cls, context):
        mat = utils.active_material(context)
        return utils_operator.base_poll(context) and mat.lp.selected

    def execute(self, context):
        mat = utils.active_material(context)
        mask = mat.lp.selected.node.node_tree.nodes[self.node_name]
        mat.lp.selected.remove_mask(mask)
        return {"FINISHED"}


class LP_OT_MoveMask(bpy.types.Operator):
    bl_idname = "lp.move_mask"
    bl_label = "Move Mask"
    bl_description = "Moves this mask"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}
    
    node_name: bpy.props.StringProperty(options={"HIDDEN"})
    move_up: bpy.props.BoolProperty(options={"HIDDEN"})

    @classmethod
    def poll(cls, context):
        mat = utils.active_material(context)
        return utils_operator.base_poll(context) and mat.lp.selected

    def execute(self, context):
        mat = utils.active_material(context)
        mask = mat.lp.selected.node.node_tree.nodes[self.node_name]
        mat.lp.selected.move_mask(mask, self.move_up)
        return {"FINISHED"}
