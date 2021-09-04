import bpy

from math import degrees, radians


class LP_OT_RotateBackground(bpy.types.Operator):
    bl_idname = "lp.rotate_background"
    bl_label = "Rotate Background"
    bl_description = "Rotates the background of the view"
    bl_options = {"REGISTER", "INTERNAL"}
    
    @classmethod
    def poll(cls, context):
        return context.mode in ["OBJECT", "PAINT_TEXTURE"]

    def modal(self, context, event):
        # set cursor
        bpy.context.window.cursor_set("MOVE_X")

        # reset cursor finish modal
        if event.type == "RIGHTMOUSE" and event.value == "RELEASE":
            context.window.cursor_set("DEFAULT")
            return {'FINISHED'}
        
        # reset cursor and cancel modal
        elif event.type == "ESC":
            context.window.cursor_set("DEFAULT")
            return {'CANCELLED'}
        
        # calculate rotation value
        factor = 0.25
        value = (event.mouse_x - self.startValue) * factor
        value = self.startRotation + value
        
        # wrap rotation
        if value >= 180:
            value -= 360
        elif value <= -180:
            value += 360

        # set value
        context.area.spaces[0].shading.studiolight_rotate_z = radians(value)
        return {'RUNNING_MODAL'}


    def invoke(self, context, event):
        if context.area and context.area.type == "VIEW_3D":
            # set start properties
            self.startValue = event.mouse_x

            shading = context.area.spaces[0].shading
            self.startRotation = degrees(shading.studiolight_rotate_z)
            
            # run modal
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        return {'FINISHED'}