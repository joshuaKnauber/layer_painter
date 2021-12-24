import bpy

from .. import utils
from ..operators import utils_operator, utils_paint
from ..data.materials.layers.layer_types import layer_fill
from ..data import utils_nodes


class LP_OT_ImageProps(bpy.types.Operator):
    bl_idname = "lp.image_props"
    bl_label = "Image Props"
    bl_description = "Draws the property settings for this image"
    bl_options = {"REGISTER", "INTERNAL"}

    node_group: bpy.props.StringProperty(options={"HIDDEN"})
    node_name: bpy.props.StringProperty(options={"HIDDEN"})
    use_mapping: bpy.props.BoolProperty(options={"HIDDEN"})

    def update_texture_mapping(self, context):
        """ update the image mapping """
        ntree = bpy.data.node_groups[self.node_group]
        tex = ntree.nodes[self.node_name]
        mapp = tex.inputs[0].links[0].from_node
        coords = mapp.inputs[0].links[0].from_node

        # update mapping connection
        if self.tex_coords == "UV":
            ntree.links.new(coords.outputs["UV"], mapp.inputs[0])
        elif self.tex_coords == "BOX":
            ntree.links.new(coords.outputs["Object"], mapp.inputs[0])
        elif self.tex_coords == "GENERATED":
            ntree.links.new(coords.outputs["Generated"], mapp.inputs[0])

        # update projection mode
        if self.tex_coords == "BOX":
            tex.projection = "BOX"
        else:
            tex.projection = "FLAT"

    tex_coords: bpy.props.EnumProperty(name="Mapping",
                                        description="Coordinates to use for the texture mapping",
                                        items=[("UV", "Uv", "Uv coordinates"),
                                              ("BOX", "Box", "Box/Object mapping"),
                                              ("GENERATED", "Generated", "Generated coordinates")],
                                        options={"HIDDEN"},
                                        update=update_texture_mapping)

    @classmethod
    def poll(cls, context):
        mat = utils.active_material(context)
        return utils_operator.base_poll(context) and mat.lp.selected

    def execute(self, context):
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        tex = bpy.data.node_groups[self.node_group].nodes[self.node_name]
        tex_image = bpy.data.node_groups[self.node_group].nodes[self.node_name].image
        mapp = tex.inputs[0].links[0].from_node

        row = layout.row()
        row.enabled = False
        row.label(text="Interpolation")

        row = layout.row()
        row.prop(tex, "interpolation", text="")
        row.separator()

        row = layout.row()
        row.enabled = False
        row.label(text="Extension")

        row = layout.row()
        row.prop(tex, "extension", text="")
        row.separator()

        row = layout.row()
        row.enabled = False
        row.label(text="Color Space")

        row = layout.row()
        row.prop(tex_image.colorspace_settings, "name", text="")
        row.separator()

        if self.use_mapping:
            row = layout.row()
            row.enabled = False
            row.label(text="Mapping")

            row = layout.row()
            row.prop(self, "tex_coords", text="")
            if self.tex_coords == "BOX":
                row.prop(tex, "projection_blend", slider=True)

            row = layout.row()
            col = row.column()
            col.prop(mapp.inputs[1], "default_value", text="Location")
            col = row.column()
            col.prop(mapp.inputs[2], "default_value", text="Rotation")
            col = row.column()
            col.prop(mapp.inputs[3], "default_value", text="Scale")

    def invoke(self, context, event):
        tex = bpy.data.node_groups[self.node_group].nodes[self.node_name]
        mapp = tex.inputs[0].links[0].from_node

        if mapp.inputs[0].links[0].from_socket.name == "UV":
            self.tex_coords = "UV"
        elif mapp.inputs[0].links[0].from_socket.name == "Object":
            self.tex_coords = "BOX"
        elif mapp.inputs[0].links[0].from_socket.name == "Generated":
            self.tex_coords = "GENERATED"
        return context.window_manager.invoke_popup(self)
