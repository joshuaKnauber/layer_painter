import bpy

from ..operators import utils_operator
from .. import constants, utils


class LP_OT_PbrSetup(bpy.types.Operator):
    bl_idname = "lp.pbr_setup"
    bl_label = "Add PBR channels"
    bl_description = "Adds the basic PBR channels to your material"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    material: bpy.props.StringProperty(name="Material",
                                       description="Name of the material to use",
                                       options={"HIDDEN", "SKIP_SAVE"})

    @classmethod
    def poll(cls, context):
        return utils_operator.base_poll(context)

    def add_missing(self, mat, princ, normal, bump, out):
        if not out:
            out = mat.node_tree.nodes.new(constants.NODES["OUT"])
        if not princ:
            princ = mat.node_tree.nodes.new(constants.NODES["PRINC"])
            princ.location = (out.location[0]-200, out.location[1])
        if not princ.outputs[0].is_linked:
            mat.node_tree.links.new(princ.outputs[0], out.inputs[0])
        if not bump:
            bump = mat.node_tree.nodes.new(constants.NODES["BUMP"])
            bump.location = (princ.location[0], princ.location[1]-630)
        if not bump.outputs[0].is_linked:
            mat.node_tree.links.new(bump.outputs[0], princ.inputs["Normal"])
        if not normal:
            normal = mat.node_tree.nodes.new(constants.NODES["NORMAL"])
            normal.location = (princ.location[0], princ.location[1]-820)
        if not normal.outputs[0].is_linked:
            mat.node_tree.links.new(normal.outputs[0], bump.inputs["Normal"])
        return princ, normal, bump, out

    def get_nodes(self, mat):
        princ, normal, bump, out = None, None, None, None
        for node in mat.node_tree.nodes:
            if node.bl_idname == constants.NODES["PRINC"]:
                princ = node
            elif node.bl_idname == constants.NODES["NORMAL"]:
                normal = node
            elif node.bl_idname == constants.NODES["BUMP"]:
                bump = node
            elif node.bl_idname == constants.NODES["OUT"]:
                out = node
        return self.add_missing(mat, princ, normal, bump, out)

    def execute(self, context):
        mat = bpy.data.materials[self.material]
        princ, normal, bump, out = self.get_nodes(mat)

        color = mat.lp.add_channel(princ.inputs["Base Color"])
        color.default_enable = True
        channel = mat.lp.add_channel(princ.inputs["Roughness"])
        channel = mat.lp.add_channel(princ.inputs["Metallic"])
        channel = mat.lp.add_channel(princ.inputs["Emission"])
        channel = mat.lp.add_channel(bump.inputs["Height"])
        channel.name = "Height"
        channel = mat.lp.add_channel(normal.inputs["Color"])
        channel.name = "Normal"

        utils.redraw()
        return {"FINISHED"}
