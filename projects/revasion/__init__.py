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
import re
from bpy.utils import register_class, unregister_class
import addon_utils
from math import radians

#VIEW3D PANELS
class UI_PT_view3d_enclume_revasion(bpy.types.Panel):
    bl_label = "Revasion"
    bl_idname = "WORKFLOW_PT_enclume_revasion"
    bl_space_type = "VIEW_3D"   
    bl_region_type = "UI"
    bl_category = "L'Enclume"

    def draw(self, context):
        project_settings = "R:\enclume\Revasion.json"

        layout = self.layout
        layout.use_property_split = True    
        
        layout.label(text = "File Manager" ) 
        open = layout.operator("pipeline.open")
        create = layout.operator("pipeline.create")        
        open.project_settings = project_settings
        create.project_settings = project_settings
        layout.operator("pipeline.version")

        layout.label(text = "Scene Manager" ) 
        layout.operator("revasion.setup_scene")
        layout.operator("revasion.import_animatic")
        layout.operator("pipeline.make_override")
        # link = layout.operator("pipeline.link_asset")
        # link.project_settings = project_settings

        layout.label(text = "Export" ) 
        op = layout.operator("pipeline.playblast") 
        currentFile = bpy.data.filepath
        op.playblastFile = currentFile.replace (".blend", ".mp4")
        


class REVASION_OT_setup_scene(bpy.types.Operator):    
    bl_idname = "revasion.setup_scene"
    bl_label = "Scene Setup"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    def unlinkColl(self, coll):
        for parent in bpy.data.collections:
            if  coll.name in parent.children:
                parent.children.unlink(coll)
    
    def unlinkObj(self, obj):
        for parent in bpy.data.collections:
            if  obj.name in parent.objects:
                parent.objects.unlink(obj) 
        if obj.name in bpy.context.scene.collection.objects:
            bpy.context.scene.collection.objects.unlink(obj)

    def execute(self, context):
        if not bpy.data.is_saved:
            self.report({'ERROR'}, 'Save file before setup scene')
            return {'CANCELLED'}      
        
        filepath = bpy.context.blend_data.filepath
        sceneName = bpy.path.basename(filepath)
        shotName = '_'.join(sceneName.split('_')[1:3])

        context.scene.render.resolution_x = 1998
        context.scene.render.resolution_y = 1080
        context.scene.sync_mode = "AUDIO_SYNC"
        context.scene.render.fps = 25
        context.scene.view_settings.view_transform = "Standard"
        context.preferences.filepaths.use_relative_paths = True
        context.preferences.filepaths.use_file_compression = True

        # context.scene.render.use_simplify = True
        context.scene.render.simplify_subdivision = 0
        
        if context.scene.camera is None:
            camera_data = bpy.data.cameras.new(name='Camera')
            camera = bpy.data.objects.new('Camera', camera_data)
            bpy.context.scene.collection.objects.link(camera)
            camera.location = (0,-10,0)
            camera.rotation_euler = (radians(90.0),0,0)
        else:
            camera = context.scene.camera
        camera.name = '_'.join(("camera", shotName))
        camera.data.lens = 35
        camera.data.passepartout_alpha = 0.99

        #COLLECTIONS
        if "LAYOUT" not in bpy.data.collections:
            layout = bpy.data.collections.new("LAYOUT")        
        layout = bpy.data.collections["LAYOUT"]
        layout.color_tag = "COLOR_03"
        if "CHARS" not in bpy.data.collections:
            chars = bpy.data.collections.new("CHARS")        
        chars = bpy.data.collections["CHARS"]
        chars.color_tag = "NONE"
        if "PROPS" not in bpy.data.collections:
            props = bpy.data.collections.new("PROPS")        
        props = bpy.data.collections["PROPS"]
        props.color_tag = "NONE"
        if "SETS" not in bpy.data.collections:
            sets = bpy.data.collections.new("SETS")        
        sets = bpy.data.collections["SETS"]
        sets.color_tag = "COLOR_02"
        if "CAMERAS" not in bpy.data.collections:
            cameras = bpy.data.collections.new("CAMERAS")        
        cameras = bpy.data.collections["CAMERAS"]
        cameras.color_tag = "COLOR_01"

        self.unlinkColl(layout)
        self.unlinkColl(chars)
        self.unlinkColl(props)
        self.unlinkColl(sets)
        self.unlinkColl(cameras)

        if layout.name not in bpy.context.scene.collection.children:
            bpy.context.scene.collection.children.link(layout)
        if chars.name not in layout.children:
            layout.children.link(chars)
        if props.name not in layout.children:
            layout.children.link(props)
        if sets.name not in bpy.context.scene.collection.children:
            bpy.context.scene.collection.children.link(sets)
        if cameras.name not in bpy.context.scene.collection.children:
            bpy.context.scene.collection.children.link(cameras)

        self.unlinkObj(camera)
        if camera.name not in cameras.objects:
            cameras.objects.link(camera)

        for screen in bpy.data.screens:
            for area in screen.areas:
                    if area.type == 'VIEW_3D':
                        for space in area.spaces:
                            if space.type == 'VIEW_3D':                       
                                space.overlay.show_overlays = True
                                space.overlay.show_relationship_lines = False   
                                  

        return {'FINISHED'}

class REVASION_OT_import_animatic(bpy.types.Operator):    
    bl_idname = "revasion.import_animatic"
    bl_label = "Import Animatic"
    bl_description = "Import Animatic"

    def version_extract(self, filename):
        version_pattern = r'_v(\d{3})'
        match = re.search(version_pattern, filename)
        return int(match.group(1)) if match else -1

    def execute(self, context):
        if not bpy.data.is_saved:
            self.report({'ERROR'}, 'Save file before setup scene')
            return {'CANCELLED'}  
           
        camera = context.scene.camera

        filepath = bpy.context.blend_data.filepath
        animatic_folder = os.path.dirname(filepath.replace('layout', 'animatic'))
        animatic_files = []
        for file in os.listdir(animatic_folder):
            if file.endswith('.mov'):
                version = self.version_extract(file)
                if version != -1:
                    animatic_files.append((file, version))
        most_recent_file = None
        version_max = -1
        for file, version in animatic_files:
            if version > version_max:
                version_max = version
                most_recent_file = file

        if most_recent_file:
            animatic_path = os.path.join(animatic_folder, most_recent_file)
        else:
            self.report({'ERROR'}, 'There is no animatic file')
            return {'CANCELLED'}  
        
        ##DISABLE BECAUSE FRAMERATE PROBLEM
        camera.data.show_background_images = True
        
        if camera.data.background_images:
            camera.data.background_images.clear()
        
        bg_image = camera.data.background_images.new()
        bg_image.source = 'MOVIE_CLIP'
        movie_clip = bpy.data.movieclips.load(animatic_path)
        movie_clip.frame_offset = -99 #CHECK
        bg_image.clip = movie_clip

        bg_image.display_depth = 'FRONT'

        if context.scene.sequence_editor is None:
            context.sequence_editor_create()

        for sequence in context.scene.sequence_editor.sequences:
            context.scene.sequence_editor.sequences.remove(sequence)

        sequencer_strip = context.scene.sequence_editor.sequences.new_movie(
            name="Movie Clip",
            filepath=animatic_path,
            channel=2,
            frame_start=100
        )
        audio_strip = context.scene.sequence_editor.sequences.new_sound(
            name="Movie Audio",
            filepath=animatic_path,
            channel=1,
            frame_start=100 
        )
        sequencer_strip.frame_start = 100
        sequencer_strip.frame_final_duration = movie_clip.frame_duration
        audio_strip.frame_start = 100
        audio_strip.frame_final_duration = movie_clip.frame_duration

        context.scene.frame_start = 100
        context.scene.frame_end = 100 + movie_clip.frame_duration - 1

        bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
        
        self.report({'INFO'}, "Animatic imported")
        return {'FINISHED'}
    

       


#REGISTER
classes = (
    UI_PT_view3d_enclume_revasion,
    REVASION_OT_setup_scene,
    REVASION_OT_import_animatic,        
    )

def register():    
    for cls in classes:
        register_class(cls)

def unregister():
    for cls in reversed(classes):
        unregister_class(cls)
