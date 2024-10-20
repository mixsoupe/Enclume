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

import bpy
from bpy.utils import register_class, unregister_class

#VIEW3D PANELS
class UI_PT_view3d_enclume_tools(bpy.types.Panel):
    bl_label = "Tools"
    bl_idname = "WORKFLOW_PT_enclume_tools"
    bl_space_type = "VIEW_3D"   
    bl_region_type = "UI"
    bl_category = "L'Enclume"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True    
        
        layout.label(text = "Grease Pencil" ) 
        row = layout.row()
        row.prop(context.scene, "create_material_color")
        row.operator("gptools.create_material")        
        layout.operator("gptools.edit_color")
        layout.operator("gptools.get_gp_material")
        #layout.operator("gptools.save_materials")
        #layout.label(text = "Save" ) 
        #layout.operator("pipeline.increment")

#REGISTER
classes = (
    UI_PT_view3d_enclume_tools,
    )

def register():    
    for cls in classes:
        register_class(cls)

def unregister():
    for cls in reversed(classes):
        unregister_class(cls)
