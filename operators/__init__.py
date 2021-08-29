import bpy
from . import layers, channels, presets, interface, assets, masks, filters, paint


classes = (
    layers.LP_OT_AddFillLayer,
    layers.LP_OT_AddPaintLayer,
    layers.LP_OT_RemoveLayer,
    layers.LP_OT_MoveLayerUp,
    layers.LP_OT_MoveLayerDown,
    layers.LP_OT_CycleChannelData,
    channels.LP_OT_MakeChannel,
    channels.LP_OT_RemoveChannel,
    channels.LP_OT_MoveChannelUp,
    channels.LP_OT_MoveChannelDown,
    presets.LP_OT_PbrSetup,
    interface.LP_OT_SwitchToNodeEditor,
    assets.LP_AssetImportProps,
    assets.LP_OT_LoadFile,
    assets.LP_OT_ProcessFile,
    assets.LP_OT_ReloadAssets,
    assets.LP_OT_RemoveAsset,
    assets.LP_OT_RemoveAssetFile,
    assets.LP_OT_LoadThumbnail,
    assets.LP_OT_LoadThumbnails,
    masks.LP_OT_AddMask,
    masks.LP_OT_RemoveMask,
    masks.LP_OT_MoveMask,
    filters.LP_OT_AddFilter,
    filters.LP_OT_RemoveFilter,
    filters.LP_OT_MoveFilter,
    paint.LP_OT_PaintChannel,
    paint.LP_OT_StopPainting,
)
reg_classes, unreg_classes = bpy.utils.register_classes_factory(classes)


def register():
    reg_classes()


def unregister():
    unreg_classes()
    assets.remove_pcolls()
