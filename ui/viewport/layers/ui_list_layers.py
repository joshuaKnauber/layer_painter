import bpy

from layer_painter import utils


class LP_UL_Layers(bpy.types.UIList):
    
    def draw_item(self, context, layout, data, layer, icon, active_data, active_propname):
        row = layout.row(align=True)
        
        # draw layer item
        if layer.node:
            self.draw_layer(row, layer)
        else:
            self.draw_faulty_layer(row, utils.get_active_material(context), layer)
            
    
    def draw_faulty_layer(self, layout, mat, layer):
        layout.alert = True
        
        layout.label(text="Faulty layer found!", icon="ERROR")
        op = layout.operator("lp.remove_layer", text="", icon="TRASH", emboss=False)
        op.overwrite_uid = layer.uid
        op.material = mat.name
        
    
    def draw_layer(self, layout, layer):
        # layer hide
        hide_icon = "HIDE_ON" if layer.node.mute else "HIDE_OFF"
        layout.prop(layer.node, "mute", text="", invert_checkbox=True, icon=hide_icon, emboss=False)

        # layer name
        split = layout.split(factor=0.7)
        split.prop(layer.node, "label", text="", emboss=False)

        # layer opacity
        split.prop(layer.get_layer_opacity_socket(), "default_value", text="", slider=True, emboss=False)