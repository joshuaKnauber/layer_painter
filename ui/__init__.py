import bpy
from . import node_editor, viewport


classes = (
)
reg_classes, unreg_classes = bpy.utils.register_classes_factory(classes)


def register():
    reg_classes()
    viewport.register()
    node_editor.register()


def unregister():
    unreg_classes()
    viewport.unregister()
    node_editor.unregister()
