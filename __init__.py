# ***** BEGIN GPL LICENSE BLOCK *****
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
# ***** END GPL LICENCE BLOCK *****
#

bl_info = {
    "name" : "GPTools",
    "author" : "Paul",
    "description" : "",
    "blender" : (3, 6, 0),
    "version" : (0, 0, 1),
    "location" : "View3D",
    "warning" : "",
    "category" : "",
}

from . operators import *
from . stroke_sets import *

from bpy.props import (
    StringProperty,
    IntProperty,
    EnumProperty,
    BoolProperty,
    CollectionProperty,
)

from bpy.app.handlers import persistent

@persistent
def update_stroke(dummy):    
    if bpy.context.mode in {'PAINT_GPENCIL'}:
        #print(bpy.context.object.type)
        stroke = bpy.context.active_object.data.layers.active.active_frame.strokes[-1]                     


#REGISTER UNREGISTER
classes = (
    GPTOOLS_OT_arrange_depth,

    GPTOOLS_MT_stroke_set_create,
    GPTOOLS_MT_stroke_sets_context_menu,
    GPTOOLS_MT_stroke_sets_select,
    GPTOOLS_PT_stroke_sets,
    GPTOOLS_UL_stroke_set,
    StrokeEntry,
    StrokeSet,
    GPTOOLS_OT_stroke_set_delete_all,
    GPTOOLS_OT_stroke_set_remove_strokes,
    GPTOOLS_OT_stroke_set_move,
    GPTOOLS_OT_stroke_set_add,
    GPTOOLS_OT_stroke_set_remove,
    GPTOOLS_OT_stroke_set_assign,
    GPTOOLS_OT_stroke_set_unassign,
    GPTOOLS_OT_stroke_set_select,
    GPTOOLS_OT_stroke_set_deselect,
    GPTOOLS_OT_stroke_set_add_and_assign,
    GPTOOLS_OT_stroke_set_copy,
    GPTOOLS_OT_stroke_set_paste,
    )

def register():

    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

        # Add properties.
    bpy.types.GreasePencil.stroke_sets = CollectionProperty(
        type=StrokeSet,
        name="Stroke Sets",
        description="List of groups of strokes for easy selection",
        override={'LIBRARY_OVERRIDABLE', 'USE_INSERTION'}
    )
    bpy.types.GreasePencil.active_stroke_set = IntProperty(
        name="Active Stroke Set",
        description="Index of the currently active stroke set",
        default=0,
        override={'LIBRARY_OVERRIDABLE'}
    )

    bpy.app.handlers.depsgraph_update_post.append(update_stroke)

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

    # Clear properties.
    del bpy.types.GreasePencil.stroke_sets
    del bpy.types.GreasePencil.active_stroke_set

    bpy.app.handlers.depsgraph_update_post.remove(update_stroke)

