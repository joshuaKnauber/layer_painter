import bpy

from ..operators import utils_operator
from .. import utils
from ..data.materials.layers.layer_types import layer_fill


class LP_OT_AddFillLayer(bpy.types.Operator):
    bl_idname = "lp.add_fill_layer"
    bl_label = "Add Fill Layer"
    bl_description = "Adds a fill layer to the active material"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}
    
    material: bpy.props.StringProperty(name="Material",
                                    description="Name of the material to use",
                                    options={"HIDDEN", "SKIP_SAVE"})

    @classmethod
    def poll(cls, context):
        return utils_operator.base_poll(context)

    def execute(self, context):
        bpy.data.materials[self.material].lp.add_fill_layer()
        utils.redraw()
        return {"FINISHED"}


class LP_OT_AddPaintLayer(bpy.types.Operator):
    bl_idname = "lp.add_paint_layer"
    bl_label = "Add Paint Layer"
    bl_description = "Adds a paint layer to the active material"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}
    
    material: bpy.props.StringProperty(name="Material",
                                    description="Name of the material to use",
                                    options={"HIDDEN", "SKIP_SAVE"})

    @classmethod
    def poll(cls, context):
        return utils_operator.base_poll(context)

    def execute(self, context):
        bpy.data.materials[self.material].lp.add_paint_layer()
        utils.redraw()
        return {"FINISHED"}


class LP_OT_RemoveLayer(bpy.types.Operator):
    bl_idname = "lp.remove_layer"
    bl_label = "Remove Layer"
    bl_description = "Removes the selected layer from the active material"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}
    
    material: bpy.props.StringProperty(name="Material",
                                    description="Name of the material to use",
                                    options={"HIDDEN", "SKIP_SAVE"})
    
    overwrite_uid: bpy.props.StringProperty(options={"HIDDEN", "SKIP_SAVE"})

    @classmethod
    def poll(cls, context):
        mat = utils.active_material(context)
        return utils_operator.base_poll(context) and mat.lp.selected

    def execute(self, context):
        mat = bpy.data.materials[self.material]
        
        if self.overwrite_uid:
            mat.lp.selected_index = mat.lp.layer_uid_index( self.overwrite_uid )
            
        mat.lp.remove_active_layer()
        utils.redraw()
        return {"FINISHED"}


class LP_OT_MoveLayerUp(bpy.types.Operator):
    bl_idname = "lp.move_layer_up"
    bl_label = "Move Layer Up"
    bl_description = "Moves this layer up"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}
    
    material: bpy.props.StringProperty(name="Material",
                                    description="Name of the material to use",
                                    options={"HIDDEN", "SKIP_SAVE"})

    @classmethod
    def poll(cls, context):
        mat = utils.active_material(context)
        return utils_operator.base_poll(context) and mat.lp.selected_index < len(mat.lp.layers)-1

    def execute(self, context):
        bpy.data.materials[self.material].lp.move_active_layer_up()
        utils.redraw()
        return {"FINISHED"}


class LP_OT_MoveLayerDown(bpy.types.Operator):
    bl_idname = "lp.move_layer_down"
    bl_label = "Move Layer Down"
    bl_description = "Moves this layer down"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}
    
    material: bpy.props.StringProperty(name="Material",
                                    description="Name of the material to use",
                                    options={"HIDDEN", "SKIP_SAVE"})

    @classmethod
    def poll(cls, context):
        mat = utils.active_material(context)
        return utils_operator.base_poll(context) and mat.lp.selected_index > 0

    def execute(self, context):
        bpy.data.materials[self.material].lp.move_active_layer_down()
        utils.redraw()
        return {"FINISHED"}


class LP_OT_CycleChannelData(bpy.types.Operator):
    bl_idname = "lp.cycle_channel_data"
    bl_label = "Cycle Channel Data"
    bl_description = "Cycles this channels data type to the next"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}
    
    material: bpy.props.StringProperty(name="Material",
                                    description="Name of the material to use",
                                    options={"HIDDEN", "SKIP_SAVE"})
    
    layer_uid: bpy.props.StringProperty(options={"HIDDEN", "SKIP_SAVE"})

    channel_uid: bpy.props.StringProperty(options={"HIDDEN", "SKIP_SAVE"})

    @classmethod
    def poll(cls, context):
        return utils_operator.base_poll(context)

    def execute(self, context):
        mat = bpy.data.materials[self.material]
        layer = mat.lp.layer_by_uid( self.layer_uid )

        if layer:
            layer_fill.cycle_channel_data_type(layer, self.channel_uid)

        utils.redraw()
        return {"FINISHED"}
