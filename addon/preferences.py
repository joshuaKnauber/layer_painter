import bpy
from .. import constants


class LP_AddonPreferences(bpy.types.AddonPreferences):

    bl_idname = constants.MODULE

    pref_nav: bpy.props.EnumProperty(name="Navigation",
                                     items=[("SETTINGS", "Settings", "Settings", "PREFERENCES", 0),
                                            ("ASSETS", "Assets", "Assets", "ASSET_MANAGER", 1)])

    def draw_assets(self, context, layout):
        row = layout.row()

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.scale_y = 1.2
        row.prop(self, "pref_nav", expand=True)
        layout.separator()

        if self.pref_nav == "SETTINGS":
            pass

        elif self.pref_nav == "ASSETS":
            self.draw_assets(context, layout)
