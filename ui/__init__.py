import bpy
from . import layer_panel, material_panel, node_channel_panel, layer_settings_panel, channel_panel, groups_panel


classes = (
    layer_panel.LP_PT_LayerPanel,
    layer_panel.LP_UL_Layers,
    material_panel.LP_PT_MaterialPanel,
    node_channel_panel.LP_PT_NodeChannels,
    channel_panel.LP_PT_Channels,
    layer_settings_panel.LP_PT_LayerSettingsPanel,
    groups_panel.LP_PT_Groups,
    groups_panel.LP_PT_GroupPreview,
)
reg_classes, unreg_classes = bpy.utils.register_classes_factory(classes)


def register():
    reg_classes()


def unregister():
    unreg_classes()
