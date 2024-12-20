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
import re
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

class PIPELINE_OT_version(bpy.types.Operator):    
    bl_idname = "pipeline.version"
    bl_label = "New Version"
    bl_description = "Make new version"
    
    def execute(self, context):
        # Folder process
        currentFile = Path(bpy.data.filepath)
        sceneName = currentFile.stem
        currentFolder  = currentFile.parent


        #Check if file is saved
        if not bpy.data.is_saved:
            self.report({'ERROR'}, 'File not saved!')
            return {'CANCELLED'}    
        
        match = re.search(r'v(\d{3})', sceneName)  # Cherche un motif 'v000', 'v001', etc.
        if match:
            versionNumber = (int(match.group(1)))
            versionV = match.group(0)

            filepath = str(currentFile).replace(versionV, "v" + "{:03d}".format(versionNumber + 1))

            bpy.ops.wm.save_as_mainfile( filepath = filepath, check_existing=True, relative_remap = True)
            
            self.report({'INFO'}, "New version saved")
            return {'FINISHED'}
        
        else:
            self.report({'ERROR'}, "File name pattern doesn't match")
            return {'CANCELLED'}
        
    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)
    
        
        
        
    

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
        # scene.render.use_stamp_date = False
        # scene.render.use_stamp_time = False
        # scene.render.use_stamp_render_time = False
        # scene.render.use_stamp_frame = True
        # scene.render.use_stamp_frame_range = False
        # scene.render.use_stamp_memory = False
        # scene.render.use_stamp_hostname = False
        # scene.render.use_stamp_camera = False
        # scene.render.use_stamp_lens = False
        # scene.render.use_stamp_scene = False
        # scene.render.use_stamp_marker = False
        # scene.render.use_stamp_filename = False
        # scene.render.use_stamp_note = True
        scene.render.use_stamp = False

        #Render
        # Check range
        for sequence in scene.sequence_editor.sequences:            
            if sequence.type == 'SOUND':
                scene.frame_start = int(sequence.frame_start)
                scene.frame_end = int(sequence.frame_start + sequence.frame_final_duration - 1)

            

        #settings = {}
        for screen in bpy.data.screens:
            for area in screen.areas:
                    if area.type == 'VIEW_3D':
                        for space in area.spaces:
                            if space.type == 'VIEW_3D':                       
                                space.overlay.show_overlays = False    
                                space.shading.type = 'MATERIAL'                          

        bpy.context.space_data.region_3d.view_perspective = 'CAMERA'
        

        filename =  bpy.path.basename(self.playblastFile)
        filename = filename.rsplit(".", 1)[0]        
        scene.render.stamp_note_text = filename        
        
        bpy.ops.render.opengl('INVOKE_DEFAULT', animation = True)   

        # bpy.app.timers.register(check_opengl_render_status)  
        
        # #Restore Settings
        # for space in settings.keys():
        #     space.overlay.show_overlays = settings[space]["overlays"]
        #     space.shading.type = settings[space]["shading.type"]

        #Open Folder
        folder = os.path.dirname(self.playblastFile)
        os.startfile(folder)

        return {'FINISHED'}
    
# def check_opengl_render_status():

#     # Vérifie si Blender est en train de rendre
#     if bpy.context.scene.frame_current == bpy.context.scene.frame_end:
#         for screen in bpy.data.screens:
#             for area in screen.areas:
#                     if area.type == 'VIEW_3D':
#                         for space in area.spaces:
#                             if space.type == 'VIEW_3D':                       
#                                 space.overlay.show_overlays = True    
#                                 space.shading.type = 'MATERIAL'                        

#         return None
#     return 0.1


def enum_tasks(self, context):
    _enum_tasks = []
    
    with open(self.project_settings, 'r') as f:
        data = json.load(f)
    for task in data["task"]:
        _enum_tasks.append((task, task, ""))

    return _enum_tasks

def enum_sequences(self, context):
    _enum_sequences = []
    
    with open(self.project_settings, 'r') as f:
        data = json.load(f)
    for sequence in data["sequences"]:
        _enum_sequences.append((sequence, sequence, ""))

    return _enum_sequences

def enum_shots(self, sequence, context):
    _enum_shots = []
    
    with open(self.project_settings, 'r') as f:
        data = json.load(f)
    for shot in data["sequences"][sequence]:
        _enum_shots.append((shot, shot, ""))

    return _enum_shots

def enum_assets(self, context):
    _enum_assets = []
    
    with open(self.project_settings, 'r') as f:
        data = json.load(f)
    for asset in data["assets"]:
        _enum_assets.append((asset, asset, ""))

    return _enum_assets

class PIPELINE_OT_base():

    project_settings: bpy.props.StringProperty (default='', subtype="FILE_PATH")
    
    task: bpy.props.EnumProperty(
        name="Task",
        default=0,
        items = lambda self, context: enum_tasks(self, context),
        )
    
    sequence: bpy.props.EnumProperty(
        name="Sequence",
        default=0,
        items = lambda self, context: enum_sequences(self, context),
        )
    
    shot: bpy.props.EnumProperty(
        name="Shot",
        default=0,
        items = lambda self, context: enum_shots(self, self.sequence, context),
        )  
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
    

    def extract_version(self, file_name):
        match = re.search(r'v(\d{3})', file_name)  # Cherche un motif 'v000', 'v001', etc.
        if match:
            return int(match.group(1))  # Retourne le numéro de version sous forme d'entier
        return -1
    
class PIPELINE_OT_open(bpy.types.Operator, PIPELINE_OT_base):    
    bl_idname = "pipeline.open"
    bl_label = "Open File"
    bl_description = "Open File"

    ui: bpy.props.BoolProperty(
        name="Load UI",
        default=True,
        )   
  
    def execute(self, context):
        with open(self.project_settings, 'r') as f:
            data = json.load(f)

        # OPENER AIGLE
        # #TODO : Ce serait bien de renseigner le style de structure dans le fichier project settings
        # task_sequence = self.task + "_" + self.shot.split("_")[0]
        # task_shot = self.task + "_" + self.shot
        # task_file = self.task + "_" + self.shot + ".blend"
        # filepath = os.path.join(data["path"], self.task, task_sequence, task_shot, task_file)


        directory = os.path.join(data["path"], "sequences", self.sequence, self.shot, self.task)
        basename = "lgr_" + self.sequence + "_" + self.shot + "_" + self.task + "_"

        filtered_files = [f for f in os.listdir(directory) if basename in f and f.endswith('.blend')]

        if filtered_files:
            latest_file = max(filtered_files, key=self.extract_version)
            filepath = os.path.join(directory, latest_file)
            bpy.ops.wm.open_mainfile(filepath=filepath,load_ui=self.ui)
            self.report({'INFO'}, "File {} opened".format(latest_file))

        else:
            self.report({'ERROR'}, "No existing file")


        return {'FINISHED'}
    
class PIPELINE_OT_create(bpy.types.Operator, PIPELINE_OT_base):    
    bl_idname = "pipeline.create"
    bl_label = "Create File"
    bl_description = "Create File"

    blank: bpy.props.BoolProperty(
        name="Create from Blank",
        default=False,
        )
    
    def execute(self, context):
        with open(self.project_settings, 'r') as f:
            data = json.load(f)

        # OPENER AIGLE
        # #TODO : Ce serait bien de renseigner le style de structure dans le fichier project settings
        # task_sequence = self.task + "_" + self.shot.split("_")[0]
        # task_shot = self.task + "_" + self.shot
        # task_file = self.task + "_" + self.shot + ".blend"
        # filepath = os.path.join(data["path"], self.task, task_sequence, task_shot, task_file)


        directory = os.path.join(data["path"], "sequences", self.sequence, self.shot, self.task)
        basename = "lgr_" + self.sequence + "_" + self.shot + "_" + self.task + "_"

        filtered_files = [f for f in os.listdir(directory) if basename in f and f.endswith('.blend')]

        if filtered_files:
            latest_file = max(filtered_files, key=self.extract_version)
            self.report({'ERROR'}, "File {} already exist".format(latest_file))

        else:
            filename = basename + "v000.blend"
            filepath = os.path.join(directory, filename)
            if self.blank:
                bpy.ops.wm.read_homefile(app_template="")
            bpy.ops.wm.save_as_mainfile( filepath = filepath, check_existing=True, relative_remap = True)
            self.report({'INFO'}, "File {} created".format(filename))


        return {'FINISHED'}
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
    

    def extract_version(self, file_name):
        match = re.search(r'v(\d{3})', file_name)  # Cherche un motif 'v000', 'v001', etc.
        if match:
            return int(match.group(1))  # Retourne le numéro de version sous forme d'entier
        return -1
    
class AssetItem(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Asset Name")
    is_selected: bpy.props.BoolProperty(name="Select", default=False)

class PIPELINE_OT_link_asset(bpy.types.Operator):    
    bl_idname = "pipeline.link_asset"
    bl_label = "Link Asset"
    bl_description = "Link asset"
    bl_options = {"REGISTER", "UNDO"}    
    
    project_settings: bpy.props.StringProperty (default='', subtype="FILE_PATH")
    
    assets: bpy.props.EnumProperty(
        name="Asset",
        default=0,
        items = lambda self, context: enum_assets(self, context),
        )
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)


    def execute(self, context):
        print (self.asset)
        return {'FINISHED'}

    # def draw(self, context):
    #     layout = self.layout
    #     col = layout.column()

    #     # Afficher chaque item de la liste avec une case à cocher
    #     for i, asset in enumerate(self.assets):
    #         row = col.row()
    #         row.prop(asset, "is_selected", text="")
    #         row.label(text=asset.name)

    # def execute(self, context):
    #     # Récupérer les assets sélectionnés
    #     selected_assets = [asset.name for asset in self.assets if asset.is_selected]

    #     if not selected_assets:
    #         self.report({'WARNING'}, "Aucun asset sélectionné")
    #         return {'CANCELLED'}

    #     # Importer les assets sélectionnés
    #     for asset_path in selected_assets:
    #         print (asset_path)
        
    #     self.report({'INFO'}, f"{len(selected_assets)} assets importés")
    #     return {'FINISHED'}

class PIPELINE_OT_make_override(bpy.types.Operator):    
    bl_idname = "pipeline.make_override"
    bl_label = "Make Override"
    bl_description = "Make Override"
    bl_options = {"REGISTER", "UNDO"}    
    
    keep: bpy.props.BoolProperty(name="Keep Position", default=True)

    def execute(self, context):
        main_bone = "pose" 
        assets = []
        for obj in bpy.context.selected_objects:
            if obj.type == "EMPTY":
                if obj.instance_type == "COLLECTION":
                    tempEmpty = bpy.data.objects.new( "empty", None )
                    bpy.context.scene.collection.objects.link(tempEmpty)
                    tempEmpty.location = obj.location
                    tempEmpty.rotation_euler = obj.rotation_euler
                    tempEmpty.scale = obj.scale

                    collection = bpy.data.collections.new(obj.name)
                    name = collection.name
                    bpy.data.collections.remove(collection)

                    with bpy.context.temp_override(active_object=obj):
                        bpy.ops.object.make_override_library()

                    if self.keep:
                        for child in bpy.data.collections[name].all_objects:
                            if child.type == "ARMATURE":
                                main = child.pose.bones[main_bone]

                                main.location = tempEmpty.location
                                main.rotation_euler = tempEmpty.rotation_euler
                                main.scale = tempEmpty.scale

                    bpy.data.objects.remove(tempEmpty, do_unlink=True)
                    assets.append(name)
        if assets:
            self.report({'INFO'}, "{} overrided".format(assets))
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "Nothing to override")
            return {'CANCELLED'}
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

                        


                

        
    

def create_library_override(library_collection):
    # Vérifiez que l'objet ou la collection a une bibliothèque liée
    if not library_collection.library:
        raise ValueError(f"La collection {library_collection.name} n'est pas liée à une bibliothèque.")
    
    # Créez une override de bibliothèque à l'aide de l'API low-level
    library_override_collection = bpy.data.collections.new(name=f"{library_collection.name}_override")
    bpy.context.scene.collection.children.link(library_override_collection)
    
    # Remplir la collection override avec des overrides des objets de la collection source
    for obj in library_collection.objects:
        # Créez une copie de l'objet avec un override
        override_obj = obj.override_create()
        library_override_collection.objects.link(override_obj)
    
    # Optionnel : copier les sous-collections si nécessaire
    for sub_collection in library_collection.children:
        override_sub_collection = create_library_override(sub_collection)
        library_override_collection.children.link(override_sub_collection)
    
    return library_override_collection


#REGISTER
classes = (
    PIPELINE_OT_increment,
    PIPELINE_OT_import_audio,
    PIPELINE_OT_playblast,
    PIPELINE_OT_open,
    PIPELINE_OT_create,
    PIPELINE_OT_version,
    #PIPELINE_OT_link_asset,
    PIPELINE_OT_make_override,
    )

def register():    
    for cls in classes:
        register_class(cls)

def unregister():
    for cls in reversed(classes):
        unregister_class(cls)
