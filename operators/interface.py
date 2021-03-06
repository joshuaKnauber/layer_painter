import bpy


class LP_OT_SwitchToNodeEditor(bpy.types.Operator):
    bl_idname = "lp.switch_to_node_editor"
    bl_label = "Switch To Node Editor"
    bl_description = "Switch to the node editor to add custom channels"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}
    
    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        context.area.type = "NODE_EDITOR"
        context.area.ui_type = "ShaderNodeTree"
        return {"FINISHED"}


class LP_OT_SwitchToViewport(bpy.types.Operator):
    bl_idname = "lp.switch_to_viewport"
    bl_label = "Switch To Viewport"
    bl_description = "Switch to the viewport to add custom channels"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}
    
    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        context.area.type = "VIEW_3D"
        return {"FINISHED"}