# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.


import bpy

from . import handlers, addon, ui, data, operators, keymaps


bl_info = {
    "name": "Layer Painter",
    "author": "Joshua Knauber",
    "description": "Layer based texture painting inside blender",
    "blender": (2, 93, 0),
    "version": (2, 0, 0),
    "location": "View3D > N-Panel > Layer Painter",
    "category": "Material",
    "wiki_url": "https://github.com/joshuaKnauber/layer_painter",
    "tracker_url": "https://github.com/joshuaKnauber/layer_painter/issues",
    "warning": "This version of Layer Painter is still under heavy development!"
}


def register():
    handlers.register()
    data.register()
    addon.register()
    operators.register()
    ui.register()
    keymaps.register()


def unregister():
    ui.unregister()
    keymaps.unregister()
    operators.unregister()
    addon.unregister()
    data.unregister()
    handlers.unregister()
