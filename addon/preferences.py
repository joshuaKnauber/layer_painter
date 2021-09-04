import bpy
import os

from .. import keymaps, constants


class LP_AddonPreferences(bpy.types.AddonPreferences):

    bl_idname = __name__.partition('.')[0]

    # navigation enum for the addon preferences
    pref_nav: bpy.props.EnumProperty(name="Navigation",
                                     items=[("SETTINGS", "Settings", "Settings", "PREFERENCES", 0),
                                            ("ASSETS", "Assets", "Assets", "ASSET_MANAGER", 1)])

    def draw_asset_group(self, layout, asset_type, items, uid):
        col = layout.column(align=True)
        row = col.row()
        row.enabled = False
        row.label(text=asset_type.title()+":")
        
        if len(items) == 0:
            col.label(text="-")
        
        # draw all assets from the given list
        for item in items:
            _box = col.box()
            row = _box.row()
            split = row.split(factor=0.6)
            row = split.row()
            row.scale_y = 0.9
            row.label(text=item["name"])

            row = split.row()
            op = row.operator("lp.load_thumbnail", text=os.path.basename(item['thumbnail']) if item["thumbnail"] else "(No Thumbnail)", emboss=False, icon="FILE_IMAGE")
            op.uid = uid
            op.name = item["name"]
            op.asset_type = asset_type

            op = row.operator("lp.remove_asset", text="", emboss=False, icon="PANEL_CLOSE")
            op.uid = uid
            op.name = item["name"]
            op.asset_type = asset_type

    def draw_assets(self, context, layout):
        # import file button
        row = layout.row(align=True)
        row.scale_y = 1.2
        row.operator("lp.load_file", icon="IMPORT")
        row.operator("lp.reload_assets", icon="FILE_REFRESH", text="")
        
        # draw all loaded assets
        for asset_file in context.scene.lp.asset_files:
            box = layout.box()
            row = box.row()
            row.label(text=asset_file["file_name"])
            op = row.operator("lp.load_thumbnails", text="", emboss=False, icon="RENDERLAYERS")
            op.uid = asset_file["uid"]
            op = row.operator("lp.remove_asset_file", text="", emboss=False, icon="TRASH")
            op.uid = asset_file["uid"]

            self.draw_asset_group(box, "masks", asset_file["masks"], asset_file["uid"])
            self.draw_asset_group(box, "filters", asset_file["filters"], asset_file["uid"])

    def draw_keymaps(self, layout):
        row = layout.row()
        row.prop(keymaps.get_shortcut(constants.ROTATE_KEY), "active", full_event=True, text="", toggle=False)
        row.label(text="Rotate HDRI")
        row = layout.row()
        row.enabled = keymaps.get_shortcut(constants.ROTATE_KEY).active
        row.prop(keymaps.get_shortcut(constants.ROTATE_KEY), "type", full_event=True, text="")

    def draw(self, context):
        layout = self.layout

        # drawing the preferences navigation
        row = layout.row()
        row.scale_y = 1.2
        row.prop(self, "pref_nav", expand=True)
        layout.separator()

        # drawing the addon settings
        if self.pref_nav == "SETTINGS":
            self.draw_keymaps(layout)

        # drawing the asset settings
        elif self.pref_nav == "ASSETS":
            self.draw_assets(context, layout)
