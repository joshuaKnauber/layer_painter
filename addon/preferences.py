import bpy
from layer_painter import constants


class LP_AddonPreferences(bpy.types.AddonPreferences):

    bl_idname = constants.MODULE

    # navigation enum for the addon preferences
    pref_nav: bpy.props.EnumProperty(name="Navigation",
                                     items=[("SETTINGS", "Settings", "Settings", "PREFERENCES", 0),
                                            ("ASSETS", "Assets", "Assets", "ASSET_MANAGER", 1)])

    def draw_assets(self, context, layout):
        row = layout.row()

    def draw(self, context):
        layout = self.layout

        # drawing the preferences navigation
        row = layout.row()
        row.scale_y = 1.2
        row.prop(self, "pref_nav", expand=True)
        layout.separator()

        # drawing the addon settings
        if self.pref_nav == "SETTINGS":
            pass

        # drawing the asset settings
        elif self.pref_nav == "ASSETS":
            self.draw_assets(context, layout)
