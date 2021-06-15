import bpy
from . import operator_utils
from .. import utils


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
        return operator_utils.base_poll(context)

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
        return operator_utils.base_poll(context)

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
        mat = utils.get_active_material(context)
        return operator_utils.base_poll(context) and mat.lp.active

    def execute(self, context):
        mat = bpy.data.materials[self.material]
        
        if self.overwrite_uid:
            mat.lp.selected = mat.lp.layer_uid_index( self.overwrite_uid )
            
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
        mat = utils.get_active_material(context)
        return operator_utils.base_poll(context) and mat.lp.selected < len(mat.lp.layers)-1

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
        mat = utils.get_active_material(context)
        return operator_utils.base_poll(context) and mat.lp.selected > 0

    def execute(self, context):
        bpy.data.materials[self.material].lp.move_active_layer_down()
        utils.redraw()
        return {"FINISHED"}