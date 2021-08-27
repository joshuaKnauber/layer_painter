import bpy

from .. import utils
from ..operators import utils_operator


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
