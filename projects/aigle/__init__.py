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
from pathlib import Path
import os.path

class AIGLE_OT_aigle_new_file(bpy.types.Operator):    
    bl_idname = "aigle.new_file"
    bl_label = "Make New File"
    bl_description = "Make new file from current file"

    thisTask: bpy.props.StringProperty (default='THIS')       
    newTask: bpy.props.StringProperty (default='NEW')

    def execute(self, context):
        if not bpy.data.is_saved:
            self.report({'ERROR'}, 'File not saved!')
            return {'CANCELLED'}
        
        # Folder process
        currentFile = Path(bpy.data.filepath)
        rootFolder = currentFile.parents[3]
        taskFolder = currentFile.parents[2]

        #Check Current File
        if taskFolder.stem != self.thisTask:
            self.report({'ERROR'}, "This file is not a valid {} task".format(self.thisTask))
            return {'CANCELLED'}
        
        newFile = str(currentFile).replace(str(rootFolder), "")
        newFile = newFile.replace(self.thisTask, self.newTask)
        newFile = str(rootFolder) +newFile
        
        if os.path.exists(newFile):
            self.report({'ERROR'}, "{} file already exist".format(self.newTask))
            return {'CANCELLED'}
        
        #Create folder
        animFolder = Path(newFile).parent
        if not os.path.exists(animFolder): 
            os.makedirs(animFolder)

        #Save file
        bpy.ops.wm.save_as_mainfile( filepath = newFile, check_existing=True, relative_remap = True)

        self.report({'INFO'}, "{} created".format(self.newTask))
        return {'FINISHED'}
    
class AIGLE_OT_aigle_setup_gpencil(bpy.types.Operator):    
    bl_idname = "aigle.setup_gpencil"
    bl_label = "Grease Pencil Setup"
    bl_description = "Use Lights OFF, Autolock Layers ON"


    def execute(self, context):
        for obj in bpy.data.objects:
            if obj.type == "GPENCIL":
                obj.data.use_autolock_layers = True
                for layer in obj.data.layers:
                    layer.use_lights = False                    


        return {'FINISHED'}

#VIEW3D PANELS
class UI_PT_view3d_enclume_aigle(bpy.types.Panel):
    bl_label = "L'Aigle et le Roitelet"
    bl_idname = "WORKFLOW_PT_enclume_aigle"
    bl_space_type = "VIEW_3D"   
    bl_region_type = "UI"
    bl_category = "L'Enclume"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        
        layout.label(text = "File Manager" ) 
        op = layout.operator("pipeline.open")
        project_settings = "A:\\Aigle.json"
        op.project_settings = project_settings

        op = layout.operator("aigle.new_file", text = "Make Animation File")
        op.thisTask = "LAYOUT"
        op.newTask = "ANIM"

        op = layout.operator("aigle.new_file", text = "Make Clean File")
        op.thisTask = "ANIM"
        op.newTask = "CLEAN"

        op = layout.operator("aigle.new_file", text = "Make Rendering File")
        op.thisTask = "CLEAN"
        op.newTask = "RENDERING"

        layout.label(text = "Setup" ) 
        op = layout.operator("pipeline.import_audio")
        currentFile = bpy.data.filepath 
        folder1 = Path(currentFile).parent.parent.parent.parent
        shortName = currentFile[-13:][:7] + ".wav"
        op.audioFile1 = os.path.join(folder1, "SOUND" ,shortName)

        layout.operator("aigle.setup_gpencil")

        layout.label(text = "Export" ) 
        op = layout.operator("pipeline.playblast") 
        currentFile = bpy.data.filepath
        op.playblastFile = currentFile.replace (".blend", ".mp4")

    
#REGISTER
classes = (
    AIGLE_OT_aigle_new_file,
    AIGLE_OT_aigle_setup_gpencil,
    UI_PT_view3d_enclume_aigle,
    )

def register():    
    for cls in classes:
        register_class(cls)

def unregister():
    for cls in reversed(classes):
        unregister_class(cls)
