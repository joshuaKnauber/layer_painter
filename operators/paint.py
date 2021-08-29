import bpy

from .. import utils
from ..operators import utils_operator, utils_paint
from ..data.materials.layers.layer_types import layer_fill


class LP_OT_PaintChannel(bpy.types.Operator):
    bl_idname = "lp.paint_channel"
    bl_label = "Paint"
    bl_description = "Start painting on this channel"
    bl_options = {"REGISTER", "INTERNAL"}

    channel: bpy.props.StringProperty(options={"HIDDEN"})

    resolution: bpy.props.IntProperty(options={"HIDDEN"},
                                        default=2048,
                                        min=2,
                                        name="Resolution",
                                        description="Resolution of the created image")
    color: bpy.props.FloatVectorProperty(options={"HIDDEN"},
                                        default=(1,1,1,0),
                                        size=4,
                                        min=0,
                                        max=1,
                                        subtype="COLOR",
                                        name="Color",
                                        description="Fill color for the created image")

    @classmethod
    def poll(cls, context):
        mat = utils.active_material(context)
        return utils_operator.base_poll(context) and mat.lp.selected

    def execute(self, context):
        layer = utils.active_material(context).lp.selected
        tex, _, _ = layer_fill.get_channel_texture_nodes(layer, self.channel)
        if not tex.image:
            img = utils_paint.create_image("image", self.resolution, self.color)
            tex.image = img
        else:
            img = tex.image
        utils_paint.save_unsave_images()
        utils_paint.paint_image(img)
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.prop(self, "resolution")
        layout.prop(self, "color")

    def invoke(self, context, event):
        layer = utils.active_material(context).lp.selected
        if layer.layer_type == "FILL":
            layer_fill.set_channel_data_type(layer, self.channel, "TEX")
            tex, _, _ = layer_fill.get_channel_texture_nodes(layer, self.channel)
            if tex.image:
                return self.execute(context)
        return context.window_manager.invoke_props_dialog(self, width=300)


class LP_OT_StopPainting(bpy.types.Operator):
    bl_idname = "lp.stop_painting"
    bl_label = "Finish"
    bl_description = "Finish painting the current image"
    bl_options = {"REGISTER", "INTERNAL"}

    @classmethod
    def poll(cls, context):
        mat = utils.active_material(context)
        return utils_operator.base_poll(context) and mat.lp.selected

    def execute(self, context):
        bpy.ops.object.mode_set(mode='OBJECT')
        utils_paint.save_unsave_images()
        return {"FINISHED"}
