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
from bpy.app.handlers import persistent

@persistent
def update_stroke(dummy):    
    if bpy.context.mode in {'PAINT_GPENCIL'}:
        stroke = bpy.context.active_object.data.layers.active.active_frame.strokes[-1]       

            
                

#REGISTER UNREGISTER
classes = (
    GPTOOLS_OT_arrange_depth,
    )

def register():

    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    bpy.app.handlers.depsgraph_update_post.append(update_stroke)

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

    bpy.app.handlers.depsgraph_update_post.remove(update_stroke)

