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
    "name" : "L'Enclume",
    "author" : "Paul",
    "description" : "",
    "blender" : (3, 6, 0),
    "version" : (0, 0, 2),
    "location" : "View3D",
    "warning" : "",
    "category" : "",
}

import bpy
from bpy.utils import register_class, unregister_class

from .grease_pencil_tools import *
from .pipeline import *
from .stroke_sets import *
from .ui_global import *

import bpy


#projects
from .projects import aigle, custom, revasion

from bpy.app.handlers import persistent


active_projects = [revasion]

all_projects = [aigle, custom, revasion]

submodules = [grease_pencil_tools, pipeline, ui_global] + active_projects


class ENCLUME_Preferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    # aigle: bpy.props.BoolProperty(
    #     name="L'Aigle et le Roitelet",
    #     default=True,
    # )
    # revasion: bpy.props.BoolProperty(
    #     name="Révasion",
    #     default=True,
    # )
    # custom: bpy.props.BoolProperty(
    #     name="Custom",
    #     default=True,
    # )
 


    def draw(self, context):
        layout = self.layout
        column = layout.column()
        
        # column.prop(self, 'aigle', expand=True)
        # column.prop(self, 'revasion', expand=True)
        # column.prop(self, 'custom', expand=True)





# @persistent
# def update_stroke(dummy):    
#     if bpy.context.mode in {'PAINT_GPENCIL'}:
#         #print(bpy.context.object.type)
#         stroke = bpy.context.active_object.data.layers.active.active_frame.strokes[-1]                     


#REGISTER UNREGISTER
classes = (ENCLUME_Preferences,)

def register():
    for cls in classes:
        register_class(cls)

    for submdule in submodules:
        submdule.register()



    # bpy.app.handlers.depsgraph_update_post.append(update_stroke)

def unregister():
    for submdule in submodules:
        submdule.unregister()

    
    for cls in reversed(classes):
        unregister_class(cls)

    # bpy.app.handlers.depsgraph_update_post.remove(update_stroke)

