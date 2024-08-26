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
import json
import shutil
from bpy.utils import register_class, unregister_class
from pathlib import Path


class PIPELINE_OT_increment(bpy.types.Operator):    
    bl_idname = "pipeline.increment"
    bl_label = "Increment Save"
    bl_description = "Save a backup version with increment"
    
    def execute(self, context):
        # Folder process
        currentFile = Path(bpy.data.filepath)
        sceneName = currentFile.stem
        currentFolder  = currentFile.parent
        versionsFolder = currentFolder / '_versions'

        #Check if file is saved
        if not bpy.data.is_saved:
            self.report({'ERROR'}, 'File not saved!')
            return {'CANCELLED'}    
        
        # Version get
        if not versionsFolder.exists():
            versionsFolder.mkdir()
        versions = [0,]
        for f in versionsFolder.iterdir():
            if f.is_file() and f.stem.startswith(sceneName):
                versionName = f.stem
                versionString = versionName.replace(sceneName, '')
                versionString = versionString.replace('_v','')
                if versionString.isdecimal():                    
                    versions.append(int(versionString)) 
        last_version = max(versions)
        
        # Version save
        new_version = last_version + 1
        versionFileName = sceneName + "_v" + f"{new_version:03}" + ".blend"
        versionPath = str(versionsFolder / versionFileName)

        #bpy.ops.wm.save_as_mainfile() #Save Current File
        # bpy.ops.wm.save_as_mainfile( filepath = versionPath, check_existing=False, copy=True, relative_remap = True)
        shutil.copy(currentFile, versionPath)
        
        self.report({'INFO'}, "Version saved: " + versionFileName)

        return {'FINISHED'}    

class PIPELINE_OT_import_audio(bpy.types.Operator):    
    bl_idname = "pipeline.import_audio"
    bl_label = "Import Audio"
    bl_description = "Import audio and setup scene"
    bl_options = {"REGISTER", "UNDO"}    
    
    audioFile1: bpy.props.StringProperty (default='')
    audioFile2: bpy.props.StringProperty (default='')

    def execute(self, context):
        scene = bpy.context.scene

        if not scene.sequence_editor:
            scene.sequence_editor_create()

        for sequence in scene.sequence_editor.sequences:
                if sequence.type == 'SOUND':
                    scene.sequence_editor.sequences.remove(sequence)
        
        #Check if file exist
        abs_path1 = bpy.path.abspath(self.audioFile1)
        abs_path2 = bpy.path.abspath(self.audioFile2)

        audioToImport = self.audioFile1

        if not os.path.isfile(abs_path1):
            audioToImport = self.audioFile2
            if not os.path.isfile(abs_path2):
                self.report({'ERROR'}, 'No audio file to import')
                return {'CANCELLED'}

        soundstrip = scene.sequence_editor.sequences.new_sound("audio", audioToImport, 1, 1)

        scene.frame_start = 1
        scene.frame_end = soundstrip.frame_final_duration

        bpy.context.scene.use_audio_scrub = True
        bpy.context.scene.sync_mode = 'AUDIO_SYNC'

        return {'FINISHED'}
    
class PIPELINE_OT_playblast(bpy.types.Operator):    
    bl_idname = "pipeline.playblast"
    bl_label = "Playblast"
    bl_description = "Playblast"

    playblastFile: bpy.props.StringProperty (default='')

    def execute(self, context):
        if not bpy.data.is_saved:
            self.report({'ERROR'}, 'File not saved!')
            return {'CANCELLED'}
        
        scene = bpy.context.scene

        #Change Settings
        scene.render.engine = "BLENDER_EEVEE"
        scene.render.image_settings.file_format = "FFMPEG"
        scene.render.image_settings.color_mode = "RGB"
        scene.render.ffmpeg.format = "MPEG4"
        scene.render.ffmpeg.codec = "H264"
        scene.render.ffmpeg.constant_rate_factor = "HIGH"
        scene.render.ffmpeg.ffmpeg_preset = "GOOD"
        scene.render.ffmpeg.audio_codec = "MP3"

        scene.render.film_transparent = False

        scene.render.filepath = self.playblastFile

        #Metadata
        scene.render.use_stamp_date = False
        scene.render.use_stamp_time = False
        scene.render.use_stamp_render_time = False
        scene.render.use_stamp_frame = True
        scene.render.use_stamp_frame_range = False
        scene.render.use_stamp_memory = False
        scene.render.use_stamp_hostname = False
        scene.render.use_stamp_camera = False
        scene.render.use_stamp_lens = False
        scene.render.use_stamp_scene = False
        scene.render.use_stamp_marker = False
        scene.render.use_stamp_filename = False
        scene.render.use_stamp_note = True
        scene.render.use_stamp = True

        #Render
        # Check range
        sound_count = 0
        for sequence in scene.sequence_editor.sequences:            
            if sequence.type == 'SOUND':
                sound_count += 1
        if sound_count == 1:
            scene.frame_start = 1
            scene.frame_end = sequence.frame_final_duration

        #settings = {}
        for screen in bpy.data.screens:
            for area in screen.areas:
                    if area.type == 'VIEW_3D':
                        for space in area.spaces:
                            if space.type == 'VIEW_3D':
                                # space_settings = {"overlays" : space.overlay.show_overlays,
                                #                   "shading.type" : space.shading.type
                                #                   }
                                # settings[space] = space_settings
                                space.overlay.show_overlays = False    
                                space.shading.type = 'MATERIAL'                                

        bpy.context.space_data.region_3d.view_perspective = 'CAMERA'



        filename =  bpy.path.basename(self.playblastFile)
        filename = filename.rsplit(".", 1)[0]        
        scene.render.stamp_note_text = filename

        bpy.ops.render.opengl('INVOKE_DEFAULT', animation = True)     
        
        # #Restore Settings
        # for space in settings.keys():
        #     space.overlay.show_overlays = settings[space]["overlays"]
        #     space.shading.type = settings[space]["shading.type"]

        #Open Folder
        folder = os.path.dirname(self.playblastFile)
        os.startfile(folder)

        return {'FINISHED'}



def enum_tasks(self, context):
    _enum_tasks = []
    
    with open(self.project_settings, 'r') as f:
        data = json.load(f)
    for task in data["task"]:
        _enum_tasks.append((task, task, ""))

    return _enum_tasks

def enum_shots(self, context):
    _enum_shots = []
    
    with open(self.project_settings, 'r') as f:
        data = json.load(f)
    for shot in data["shots"]:
        _enum_shots.append((shot, shot, ""))

    return _enum_shots

class PIPELINE_OT_open(bpy.types.Operator):    
    bl_idname = "pipeline.open"
    bl_label = "Open File"
    bl_description = "Open File"

    project_settings: bpy.props.StringProperty (default='', subtype="FILE_PATH")
    
    # def enum_tasks(self, context):
    #     _enum_tasks = []
    #     _enum_tasks.clear()
    #     _enum_tasks.append(("Layout", "Layout", ""))
    #     _enum_tasks.append(("Clean", "Clean", ""))

    #     return _enum_tasks

    ui: bpy.props.BoolProperty(
        name="Load UI",
        default=True,
        )
    
    task: bpy.props.EnumProperty(
        name="Task",
        default=0,
        items = lambda self, context: enum_tasks(self, context),
        )
    
    shot: bpy.props.EnumProperty(
        name="Shot",
        default=0,
        items = lambda self, context: enum_shots(self, context),
        )
    
    def execute(self, context):
        with open(self.project_settings, 'r') as f:
            data = json.load(f)
        
        #TODO : Ce serait bien de renseigner le style de structure dans le fichier project settings
        task_sequence = self.task + "_" + self.shot.split("_")[0]
        task_shot = self.task + "_" + self.shot
        task_file = self.task + "_" + self.shot + ".blend"

        filepath = os.path.join(data["path"], self.task, task_sequence, task_shot, task_file)
        
        if not os.path.isfile(filepath) :
            self.report({'ERROR'}, "File doesn't exist!")
            return {'CANCELLED'}
        
        bpy.ops.wm.open_mainfile(filepath=filepath,load_ui=self.ui)        

        return {'FINISHED'}
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)



#REGISTER
classes = (
    PIPELINE_OT_increment,
    PIPELINE_OT_import_audio,
    PIPELINE_OT_playblast,
    PIPELINE_OT_open,
    )

def register():    
    for cls in classes:
        register_class(cls)

def unregister():
    for cls in reversed(classes):
        unregister_class(cls)
