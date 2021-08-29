import bpy

from .. import utils


IS_BAKING = False

def is_baking():
    global IS_BAKING
    return IS_BAKING


class LP_OT_BakeSetupChannel(bpy.types.Operator):
    bl_idname = "lp.bake_setup_channel"
    bl_label = "Bake Setup"
    bl_options = {'INTERNAL'}

    channel: bpy.props.StringProperty()

    def execute(self, context):
        mat = utils.active_material(context)
        channel = mat.lp.channel_by_uid(self.channel)
        channel.completed_bake = False
        return {'FINISHED'}



class LP_OT_BakeCleanupChannel(bpy.types.Operator):
    bl_idname = "lp.bake_cleanup_channel"
    bl_label = "Bake Clean Up"
    bl_options = {'INTERNAL'}

    channel: bpy.props.StringProperty()

    def execute(self, context):
        mat = utils.active_material(context)
        channel = mat.lp.channel_by_uid(self.channel)
        channel.completed_bake = True
        utils.redraw()
        return {'FINISHED'}



class LP_OT_BakeFinish(bpy.types.Operator):
    bl_idname = "lp.bake_finish"
    bl_label = "Bake Finish"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        global IS_BAKING
        IS_BAKING = False
        return {'FINISHED'}



class LP_OT_BakeMacro(bpy.types.Macro):
    bl_idname = "lp.bake_macro"
    bl_label = "Bake Macro"
    bl_options = {'INTERNAL'}



def get_macro():
    """ cleans the macro and returns it for defining """
    # unregister macro for clean
    if hasattr(bpy.types, "LP_OT_BakeMacro"):
        bpy.utils.unregister_class(bpy.types.LP_OT_BakeMacro)

    # register macro
    bpy.utils.register_class(LP_OT_BakeMacro)
    return LP_OT_BakeMacro



class LP_OT_BakeChannelsModal(bpy.types.Operator):
    bl_idname = "lp.bake_modal"
    bl_label = "Bake Modal"


    def modal(self, context, event):
        global IS_BAKING
        if not IS_BAKING:
            return {'FINISHED'}
        return {'PASS_THROUGH'}


    def invoke(self, context, event):
        global IS_BAKING
        IS_BAKING = True

        macro = get_macro()

        # set up all bake channels
        for channel in utils.active_material(context).lp.channels:
            if channel.bake:

                setup = macro.define('LP_OT_bake_setup_channel')
                setup.properties.channel = channel.uid

                bake = macro.define('OBJECT_OT_bake')
                bake.properties.margin = 24

                clean = macro.define('LP_OT_bake_cleanup_channel')
                clean.properties.channel = channel.uid

        macro.define('LP_OT_bake_finish')

        bpy.ops.lp.bake_macro('INVOKE_DEFAULT')

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}