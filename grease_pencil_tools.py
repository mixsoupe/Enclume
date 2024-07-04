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
import numpy as np
import colorsys

class GPTOOLS_OT_arrange_depth(bpy.types.Operator):
    
    bl_idname = "gptools.arrange_depth"
    bl_label = "Arrange Strokes Depth"
    bl_description = "Arrange strokes depth based on point of view"

    @classmethod
    def poll(cls,context):
        context = bpy.context.mode
        is_edit_mode = (context in {'EDIT_GPENCIL'})
        return is_edit_mode
    
    def execute(self, context):
        camera = bpy.context.scene.camera
        camera_loc = camera.location 
        
        strokes = bpy.context.editable_gpencil_strokes
        strokes_order = {}
        for stroke in strokes:
            if stroke.select:
                depth = get_depth(stroke, camera_loc)
                strokes_order[stroke] = depth
        sorted_strokes = sorted(strokes_order, key=strokes_order.get)
        
        #Arrange
        for stroke in sorted_strokes:
            bpy.ops.gpencil.select_all(action='DESELECT')
            stroke.select = True
            bpy.ops.gpencil.stroke_arrange(direction='BOTTOM')

        return {'FINISHED'}

class GPTOOLS_OT_draw(bpy.types.Operator):
    
    bl_idname = "gptools.draw"
    bl_label = "Draw Tool"
    bl_description = "Change object mode to Draw and select draw tool"

    @classmethod
    def poll(cls,context):
        obj = context.active_object
        if obj is not None:
            obj_type = obj.type
            is_geometry = (obj_type in {'GPENCIL',})

            return is_geometry
    
    def execute(self, context):
        bpy.ops.object.mode_set(mode = 'PAINT_GPENCIL')
        bpy.ops.wm.tool_set_by_id(name="builtin_brush.Draw")
        return {'FINISHED'}
    

class GPTOOLS_OT_erase(bpy.types.Operator):
    
    bl_idname = "gptools.erase"
    bl_label = "Erase Tool"
    bl_description = "Change object mode to Draw and select erase tool"

    @classmethod
    def poll(cls,context):
        obj = context.active_object
        if obj is not None:
            obj_type = obj.type
            is_geometry = (obj_type in {'GPENCIL',})

            return is_geometry
    
    def execute(self, context):
        bpy.ops.object.mode_set(mode = 'PAINT_GPENCIL')
        bpy.ops.wm.tool_set_by_id(name="builtin_brush.Erase")
        return {'FINISHED'}
    
class GPTOOLS_OT_lasso(bpy.types.Operator):
    
    bl_idname = "gptools.lasso"
    bl_label = "Lasso Tool"
    bl_description = "Change object mode to Edit and select erase tool"

    @classmethod
    def poll(cls,context):
        obj = context.active_object
        if obj is not None:
            obj_type = obj.type
            is_geometry = (obj_type in {'GPENCIL',})

            return is_geometry
    
    def execute(self, context):
        bpy.ops.object.mode_set(mode = 'EDIT_GPENCIL')
        bpy.ops.wm.tool_set_by_id(name="builtin.select_lasso")
        return {'FINISHED'}
    
class GPTOOLS_OT_push(bpy.types.Operator):
    
    bl_idname = "gptools.push"
    bl_label = "Push Tool"
    bl_description = "Change object mode to Sculpt and select push tool"

    @classmethod
    def poll(cls,context):
        obj = context.active_object
        if obj is not None:
            obj_type = obj.type
            is_geometry = (obj_type in {'GPENCIL',})

            return is_geometry
    
    def execute(self, context):
        bpy.ops.object.mode_set(mode = 'SCULPT_GPENCIL')
        bpy.ops.wm.tool_set_by_id(name="builtin_brush.Push")
        return {'FINISHED'}
    

class GPTOOLS_OT_create_material(bpy.types.Operator):
    
    bl_idname = "gptools.create_material"
    bl_label = "Create Materials"
    bl_description = "Create materials tool"

    name: bpy.props.StringProperty("Name", default = "Material")
    stroke: bpy.props.BoolProperty("Stroke", default = True)
    fill: bpy.props.BoolProperty("Fill", default = True)
    
    @classmethod
    def poll(cls,context):  
        obj = context.active_object
        if obj is not None:
            obj_type = obj.type
            is_geometry = (obj_type in {'GPENCIL',})

            return is_geometry
    
    def execute(self, context):  
        ob = bpy.context.active_object
        
        #Create Material
        mat = bpy.data.materials.new(name=self.name)
        bpy.data.materials.create_gpencil_data(mat)

        #Change Material
        mat.grease_pencil.show_stroke = self.stroke
        mat.grease_pencil.show_fill = self.fill        
        mat.grease_pencil.color = bpy.context.scene.create_material_color
        mat.grease_pencil.fill_color = bpy.context.scene.create_material_color

        #Attach material
        ob.data.materials.append(mat)    
        ob.active_material_index = len(ob.material_slots)-1

        return {'FINISHED'}
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
    

class GPTOOLS_OT_get_material(bpy.types.Operator):
    
    bl_idname = "gptools.get_gp_material"
    bl_label = "Get Grease Pencil Material"
    bl_description = "get grease pencil material from selected stroke"

    @classmethod
    def poll(cls,context):
        context = bpy.context.mode
        is_edit_mode = (context in {'EDIT_GPENCIL'})
        return is_edit_mode
    
    def execute(self, context):
        strokes = bpy.context.editable_gpencil_strokes
        for stroke in strokes:
            if stroke.select:
                index = stroke.material_index
                material = bpy.context.object.data.materials[index]
                bpy.context.object.active_material_index = index

                self.report({'INFO'}, "Stroke material is {}".format(material.name))
                return {'FINISHED'}
                
        self.report({'WARNING'}, "No stroke selected")
        return {'CANCELLED'}

       
# _enum_cameras = []

# def enum_cameras(self, context):
#     _enum_cameras.clear()

#     strokes = bpy.context.editable_gpencil_strokes
#     for stroke in strokes:
#         if stroke.select:
#             index = stroke.material_index
#             material = bpy.context.object.data.materials[index]
#             _enum_cameras.append((material.name, material.name, ""))
    
#     return _enum_cameras

class GPTOOLS_OT_edit_color(bpy.types.Operator):
    
    bl_idname = "gptools.edit_color"
    bl_label = "Edit Material Color"
    bl_description = "Edit Material Color"
    bl_options = {'REGISTER', 'UNDO'}
    
    hue: bpy.props.FloatProperty(name="Hue", min=-180.0, max=180.0, default=0.0)
    saturation: bpy.props.FloatProperty(name="Saturation", min=-100.0, max=100.0, default=0.0)
    value: bpy.props.FloatProperty(name="Value", min=-100.0, max=100.0, default=0.0)

    @classmethod
    def poll(cls,context):
        context = bpy.context.mode
        is_edit_mode = (context in {'EDIT_GPENCIL'})
        return is_edit_mode
    
    def execute(self, context):
        strokes = bpy.context.editable_gpencil_strokes
        for stroke in strokes:
            if stroke.select:
                index = stroke.material_index
                material = bpy.context.object.data.materials[index]
                
                stroke_color = material.grease_pencil.color                
                new_stroke_color = adjust_color(stroke_color, self.hue, self.saturation, self.value)
                
                fill_color = material.grease_pencil.fill_color                
                new_fill_color = adjust_color(fill_color, self.hue, self.saturation, self.value)
                
                material.grease_pencil.color = new_stroke_color
                material.grease_pencil.fill_color = new_fill_color

        return {'FINISHED'}
    
    def invoke(self, context, event):
        self.hue = 0.0
        self.saturation = 0.0
        self.value = 0.0
        return self.execute(context)
    
    
#FUNCTIONS
def get_depth(stroke, pov):
    matrix = bpy.context.active_object.matrix_world 
    vlen = len(stroke.points)

    #Get coordinates
    points = np.empty((vlen, 3), 'f')
    stroke.points.foreach_get(
            "co", np.reshape(points, vlen * 3))

    #Set to world coordinate
    transposed_matrix = np.array(matrix).T
    local_points_homogeneous = np.column_stack((points, np.ones(vlen)))   
    world_points_homogeneous = np.dot(local_points_homogeneous, transposed_matrix )
    world_points = world_points_homogeneous[:, :3]
    # world_points = np.matmul(points, matrix)

    distances = np.linalg.norm(world_points - pov, ord=2, axis=1.)
    distance_average = np.average(distances)

    return distance_average

def adjust_color(color, hue, saturation, value):
    r, g, b, a = color
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    h = (h + hue/180) % 1.0
    s = min(max(s + saturation/100, 0.0), 1.0)
    v = min(max(v + value/100, 0.0), 1.0)
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return (r, g, b, a)

##CONVERTER

#REGISTER
classes = (
    GPTOOLS_OT_arrange_depth,
    GPTOOLS_OT_draw,
    GPTOOLS_OT_erase,
    GPTOOLS_OT_lasso,
    GPTOOLS_OT_push,
    GPTOOLS_OT_create_material,
    GPTOOLS_OT_get_material,
    GPTOOLS_OT_edit_color,
    )

def register():
    if not hasattr( bpy.types.Scene, 'create_material_color'):
        bpy.types.Scene.create_material_color = bpy.props.FloatVectorProperty(
                    name = "Color",
                    subtype = "COLOR",
                    size = 4,
                    min = 0.0,
                    max = 1.0,
                    default = (1.0,1.0,1.0,1.0),
                    options=set())
       
    for cls in classes:
        register_class(cls)

def unregister(): 
    for cls in reversed(classes):
        unregister_class(cls)

    del bpy.types.Scene.create_material_color
