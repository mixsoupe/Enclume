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
        if sceneName == '':
            #asks the user to save as
            self.report({'ERROR'}, "Not Saved! Save this scene first using the \"save as\" command [CTRL + SHIFT + S]")
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

        bpy.ops.wm.save_as_mainfile() #Save Current File
        bpy.ops.wm.save_as_mainfile( filepath = versionPath, check_existing=False, copy=True, relative_remap = True)
        self.report({'INFO'}, "Version saved: " + versionFileName)

        return {'FINISHED'}


#REGISTER
classes = (
    PIPELINE_OT_increment,
    )

def register():    
    for cls in classes:
        register_class(cls)

def unregister():
    for cls in reversed(classes):
        unregister_class(cls)
