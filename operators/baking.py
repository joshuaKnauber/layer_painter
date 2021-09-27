import bpy

import os

from .import utils_paint
from .. import utils, constants


IS_BAKING = False
TIMER = None

def is_baking():
    global IS_BAKING
    return IS_BAKING


class LP_OT_BakeSetupChannel(bpy.types.Operator):
    bl_idname = "lp.bake_setup_channel"
    bl_label = "Bake Setup"
    bl_options = {'INTERNAL'}

    channel: bpy.props.StringProperty()

    def add_bake_setup(self, ntree):
        out = ntree.nodes.new(constants.NODES["OUT"])
        out.name = constants.EXPORT_OUT_NAME

        # set material output to active
        for node in ntree.nodes:
            if node.bl_idname == constants.NODES["OUT"]:
                node.is_active_output = False
        out.is_active_output = True

        # add emission and connect to output
        emit = ntree.nodes.new(constants.NODES["EMIT"])
        emit.inputs[0].default_value = (1, 0, 0.6, 1)
        emit.name = constants.EXPORT_EMIT_NAME
        ntree.links.new(emit.outputs[0], out.inputs[0])

        return emit

    def setup_texture(self, context, ntree, is_data):
        # set up image in material
        tex = ntree.nodes.new(constants.NODES["TEX"])
        tex.name = constants.BAKE_IMG_NODE
        tex.image = utils_paint.create_image(constants.BAKE_IMG_NAME, context.scene.lp.export.resolution, context.scene.lp.export.base_color, is_data)
        ntree.nodes.active = tex

    def execute(self, context):
        mat = utils.active_material(context)
        channel = mat.lp.channel_by_uid(self.channel)

        # set up bake nodes
        emit = self.add_bake_setup(mat.node_tree)

        # set up texture
        self.setup_texture(context, mat.node_tree, is_data=channel.is_data)

        # set color
        if channel.inp.bl_idname == constants.SOCKETS["COLOR"]:
            emit.inputs[0].default_value = channel.inp.default_value
        else:
            v = channel.inp.default_value
            emit.inputs[0].default_value = (v, v, v, v)

        # connect output
        if channel.inp.is_linked:
            mat.node_tree.links.new(channel.inp.links[0].from_socket, emit.inputs[0])
        return {'FINISHED'}



class LP_OT_BakeCleanupChannel(bpy.types.Operator):
    bl_idname = "lp.bake_cleanup_channel"
    bl_label = "Bake Clean Up"
    bl_options = {'INTERNAL'}

    channel: bpy.props.StringProperty()

    def remove_bake_setup(self, ntree):
        if constants.EXPORT_OUT_NAME in ntree.nodes:
            ntree.nodes.remove(ntree.nodes[constants.EXPORT_OUT_NAME])
        if constants.EXPORT_EMIT_NAME in ntree.nodes:
            ntree.nodes.remove(ntree.nodes[constants.EXPORT_EMIT_NAME])

    def remove_texture(self, ntree):
        # remove bake image node
        if constants.BAKE_IMG_NODE in ntree.nodes:
            ntree.nodes.remove(ntree.nodes[constants.BAKE_IMG_NODE])

        # remove bake image
        if constants.BAKE_IMG_NAME in bpy.data.images:
            bpy.data.images.remove(bpy.data.images[constants.BAKE_IMG_NAME])

    def execute(self, context):
        mat = utils.active_material(context)
        channel = mat.lp.channel_by_uid(self.channel)
        channel.completed_bake = True

        # remove baking setup
        self.remove_bake_setup(mat.node_tree)

        # save image
        img = bpy.data.images[constants.BAKE_IMG_NAME]
        path = bpy.path.abspath(context.scene.lp.export.directory)
        if os.path.exists(path):
            img.save_render(os.path.join(path, f"{mat.name}_{channel.name}.{context.scene.render.image_settings.file_format.lower()}"))

        # remove texture
        self.remove_texture(mat.node_tree)

        utils.redraw()
        return {'FINISHED'}



class LP_OT_BakeFinish(bpy.types.Operator):
    bl_idname = "lp.bake_finish"
    bl_label = "Bake Finish"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        global IS_BAKING
        IS_BAKING = False
        
        global TIMER
        if TIMER:
            bpy.context.window_manager.event_timer_remove(TIMER)
            TIMER = None

        # update viewport
        mat = utils.active_material(context)
        mat.lp.selected_index = mat.lp.selected_index
        return {'FINISHED'}



class LP_OT_BakeMacro(bpy.types.Macro):
    bl_idname = "lp.bake_macro"
    bl_label = "Bake Macro"
    bl_options = {'INTERNAL'}



def get_macro():
    """ cleans the macro and returns it for defining """
    # unregister macro for clean
    if hasattr(bpy.types, "LP_OT_bake_macro"):
        bpy.utils.unregister_class(bpy.types.LP_OT_bake_macro)

    # register macro
    bpy.utils.register_class(LP_OT_BakeMacro)
    return LP_OT_BakeMacro



class LP_OT_BakeChannelsModal(bpy.types.Operator):
    bl_idname = "lp.bake_modal"
    bl_label = "Bake Modal"
    bl_description= "Bakes the selected channels for the selected objects"


    def modal(self, context, event):
        global IS_BAKING
        if not IS_BAKING:
            # reset settings
            context.scene.render.engine = self.prev_engine
            context.scene.cycles.samples = self.prev_samples
            context.scene.view_settings.view_transform = self.prev_view_transform
            return {'FINISHED'}
        return {'PASS_THROUGH'}


    def invoke(self, context, event):
        global IS_BAKING
        IS_BAKING = True

        # save previous settings
        self.prev_engine = context.scene.render.engine
        context.scene.render.engine = "CYCLES"

        self.prev_samples = context.scene.cycles.samples
        context.scene.cycles.samples = 2

        self.prev_view_transform = context.scene.view_settings.view_transform
        context.scene.view_settings.view_transform = 'Standard'

        # set bake settings
        context.scene.render.bake.use_clear = False

        macro = get_macro()

        # set up all bake channels
        for channel in utils.active_material(context).lp.channels:
            channel.completed_bake = False
            if channel.bake:

                setup = macro.define('LP_OT_bake_setup_channel')
                setup.properties.channel = channel.uid

                bake = macro.define('OBJECT_OT_bake')
                bake.properties.type = "EMIT"

                clean = macro.define('LP_OT_bake_cleanup_channel')
                clean.properties.channel = channel.uid

        macro.define('LP_OT_bake_finish')

        global TIMER
        TIMER = bpy.context.window_manager.event_timer_add(1, window=bpy.context.window)

        bpy.ops.lp.bake_macro('INVOKE_DEFAULT')

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}