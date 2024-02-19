import bpy
import os

def playblast(filepath, publish = False):
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

    scene.render.filepath = filepath

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

    # settings = {}
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

    # #Restore Settings
    # for space in settings.keys():
    #     space.overlay.show_overlays = settings[space]["overlays"]
    #     space.shading.type = settings[space]["shading.type"]

    filename =  bpy.path.basename(filepath)
    filename = filename.rsplit(".", 1)[0]        
    scene.render.stamp_note_text = filename

    bpy.ops.render.opengl('INVOKE_DEFAULT', animation = True)     
    
    #Open Folder
    folder = os.path.dirname(filepath)
    os.startfile(folder)


def set_render_settings():
    scene = bpy.context.scene

    #Change Settings
    scene.render.engine = "CYCLES"
    scene.cycles.device = "GPU"
    scene.cycles.samples = 32

    
    scene.render.image_settings.file_format = "OPEN_EXR_MULTILAYER"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.image_settings.color_depth = "32"
    scene.render.image_settings.exr_codec = "ZIP"
    scene.render.use_overwrite = True
    
    scene.render.film_transparent = True

    #Metadata
    scene.render.use_stamp_note = False
    scene.render.use_stamp = False

    #Cryptomatte
    bpy.context.view_layer.use_pass_cryptomatte_object = True
    bpy.context.view_layer.use_pass_cryptomatte_material = False
    bpy.context.view_layer.use_pass_cryptomatte_asset = False
    bpy.context.view_layer.pass_cryptomatte_depth = 6
    bpy.context.view_layer.use_pass_cryptomatte_accurate = True

    #Render
    sound_count = 0
    for sequence in scene.sequence_editor.sequences:            
        if sequence.type == 'SOUND':
            sound_count += 1
    if sound_count == 1:
        scene.frame_start = 1
        scene.frame_end = sequence.frame_final_duration
