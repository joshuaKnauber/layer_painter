import bpy


class LP_OT_AddMask(bpy.types.Operator):
    bl_idname = "my_operator.my_class_name"
    bl_label = "My Class Name"
    bl_description = "Description that shows in blender tooltips"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        
        return {"FINISHED"}
