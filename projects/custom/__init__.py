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
class UI_PT_view3d_enclume_custom(bpy.types.Panel):
    bl_label = "Custom"
    bl_idname = "WORKFLOW_PT_enclume_custom"
    bl_space_type = "VIEW_3D"   
    bl_region_type = "UI"
    bl_category = "L'Enclume"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True    
        
        #NIJIGP TOOLS
        layout.label(text = "NijiGP" ) 
        row = layout.row()
        row.operator("gpencil.nijigp_bool_selected", text="+", icon="SELECT_EXTEND").operation_type = 'UNION'
        row.operator("gpencil.nijigp_bool_selected", text="-", icon="SELECT_SUBTRACT").operation_type = 'DIFFERENCE'
        row.operator("gpencil.nijigp_bool_selected", text="×", icon="SELECT_INTERSECT").operation_type = 'INTERSECTION'

        #GPTOOLBOX
        layout.label(text = "GP Toolbox" ) 
        col = layout.column()
        ## draw/manipulation camera
        if context.scene.camera and context.scene.camera.name.startswith(('draw', 'obj')):
            row = col.row(align=True)
            row.operator('gp.draw_cam_switch', text = 'Main cam', icon = 'OUTLINER_OB_CAMERA')
            row.label(text='',icon='LOOP_BACK')
            if context.scene.camera.name.startswith('draw'):
                col.operator('gp.reset_cam_rot', text='reset rotation')#.swapmethod ? = CAM
            else:
                col.operator('gp.set_view_as_cam', text='set view')#.swapmethod ? = CAM

        else:
            row = col.row(align=True)
            row.operator('gp.draw_cam_switch', text = 'Draw cam', icon = 'CON_CAMERASOLVER').cam_mode = 'draw'
            row.operator('gp.draw_cam_switch', text = 'Object cam', icon = 'CON_CAMERASOLVER').cam_mode = 'object'
            col.label(text='In main camera', icon = 'OUTLINER_OB_CAMERA')

        if context.scene.camera:
            row = layout.row(align=True)# .split(factor=0.5)
            row.label(text='Passepartout')
            if context.scene.camera.name == 'draw_cam':
                row.prop(context.scene.gptoolprops, 'drawcam_passepartout', text='', icon ='OBJECT_HIDDEN') 
            else:
                row.prop(context.scene.camera.data, 'show_passepartout', text='', icon ='OBJECT_HIDDEN')
            row.prop(context.scene.camera.data, 'passepartout_alpha', text='')
        
        row = layout.row()
        row.prop(context.scene.gptoolprops, 'edit_lines_opacity')

    
#REGISTER
classes = (
    UI_PT_view3d_enclume_custom,
    )

def register():    
    for cls in classes:
        register_class(cls)

def unregister():
    for cls in reversed(classes):
        unregister_class(cls)
