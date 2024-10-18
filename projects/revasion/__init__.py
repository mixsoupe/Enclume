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
import os
from bpy.utils import register_class, unregister_class
import addon_utils

#VIEW3D PANELS
class UI_PT_view3d_enclume_revasion(bpy.types.Panel):
    bl_label = "Revasion"
    bl_idname = "WORKFLOW_PT_enclume_revasion"
    bl_space_type = "VIEW_3D"   
    bl_region_type = "UI"
    bl_category = "L'Enclume"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True    
        
        #NIJIGP TOOLS
        layout.label(text = "Test" ) 
        row = layout.row()
        layout.label(text = "File Manager" ) 
        op = layout.operator("pipeline.open")
        project_settings = "A:\\Aigle.json"
        op.project_settings = project_settings

        row.operator("revasion.setup_scene")
        # row.operator("gpencil.nijigp_bool_selected", text="-", icon="SELECT_SUBTRACT").operation_type = 'DIFFERENCE'
        # row.operator("gpencil.nijigp_bool_selected", text="×", icon="SELECT_INTERSECT").operation_type = 'INTERSECTION'

        #GPTOOLBOX
        layout.label(text = "Test2" ) 
        col = layout.column()

class REVASION_OT_aigle_setup_scene(bpy.types.Operator):    
    bl_idname = "revasion.setup_scene"
    bl_label = "Scene Setup"
    bl_description = ""


    def execute(self, context):               
        context.scene.render.resolution_x = 1998
        context.scene.render.resolution_y = 1080
        context.scene.sync_mode = "AUDIO_SYNC"
        context.scene.render.fps = 25
        context.scene.view_settings.view_transform = "Standard"
        context.preferences.filepaths.use_relative_paths = True
        context.preferences.filepaths.use_file_compression = True
        
        
        # #BLACK BARS
        # for mod in addon_utils.modules():
        #     if mod.bl_info['name'] == "L'Enclume":
        #         filepath = mod.__file__
        #         directory = os.path.dirname(filepath)
        #         image_path = os.path.join(directory, "projects", "revasion", "back_bars.psd")
                

        # camera = context.scene.camera
        # camera.data.show_background_images = True
        
        # for bg in camera.data.background_images:
        #     print (bg.image)
        #     # if bg.image:
        #     #     if bg.image.name == "back_bars.psd":
        #     #         print (bg)


        # # bg_image = camera.data.background_images.new()
        # # bg_image.image = bpy.data.images.load(image_path)
        # # bg_image.display_depth = 'FRONT'
        # # bg_image.alpha = 1.0


        

        return {'FINISHED'}


#REGISTER
classes = (
    UI_PT_view3d_enclume_revasion,
    REVASION_OT_aigle_setup_scene,
    )

def register():    
    for cls in classes:
        register_class(cls)

def unregister():
    for cls in reversed(classes):
        unregister_class(cls)
