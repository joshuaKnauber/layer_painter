import bpy
from .. import constants


class LP_AddonPreferences(bpy.types.AddonPreferences):
    
    bl_idname = constants.MODULE
    
    pref_nav: bpy.props.EnumProperty(name="Navigation",
                                     items=[("SETTINGS","Settings","Settings","PREFERENCES",0),
                                            ("ASSETS","Assets","Assets","ASSET_MANAGER",1)])
    
    def draw_assets(self, context, layout):
        row = layout.row()
        row.scale_y = 1.5
        row.operator("lp.add_asset_file", icon="ADD")
        layout.separator()
        
        layout.label(text="Masks")
        for mask in context.scene.lp.masks:
            layout.label(text=mask.name)

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