import bpy
from .. import constants


class LP_AddonPreferences(bpy.types.AddonPreferences):
    
    bl_idname = constants.MODULE

    def draw(self,context):
        layout = self.layout