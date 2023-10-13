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

from bpy.types import (
    Operator,
    Menu,
    Panel,
    UIList,
    PropertyGroup,
)
from bpy.props import (
    StringProperty,
    IntProperty,
    EnumProperty,
    BoolProperty,
    CollectionProperty,
)

# Data Structure ##############################################################
class StrokeEntry(PropertyGroup):
    name: StringProperty(name="Bone Name", override={'LIBRARY_OVERRIDABLE'})


class StrokeSet(PropertyGroup):
    name: StringProperty(name="Set Name", override={'LIBRARY_OVERRIDABLE'})
    bone_ids: CollectionProperty(
        type=StrokeEntry,
        override={'LIBRARY_OVERRIDABLE', 'USE_INSERTION'}
    )
    is_selected: BoolProperty(name="Is Selected", override={'LIBRARY_OVERRIDABLE'})

class GPTOOLS_MT_stroke_sets_context_menu(Menu):
    bl_label = "Selection Sets Specials"

    def draw(self, context):
        layout = self.layout

        layout.operator("gptools.stroke_set_delete_all", icon='X')
        layout.operator("gptools.stroke_set_remove_strokes", icon='X')
        layout.operator("gptools.selection_set_copy", icon='COPYDOWN')
        layout.operator("gptools.selection_set_paste", icon='PASTEDOWN')

class GPTOOLS_PT_stroke_sets(Panel):
    bl_label = "Stroke Sets"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return (context.object.type == 'GPENCIL')

    def draw(self, context):
        layout = self.layout

        gp = context.object.data

        row = layout.row()
        #row.enabled = (context.mode == 'POSE')

        # UI list
        rows = 4 if len(gp.stroke_sets) > 0 else 1
        row.template_list(
            "GPTOOLS_UL_stroke_set", "",  # type and unique id
            gp, "stroke_sets",  # pointer to the CollectionProperty
            gp, "active_stroke_set",  # pointer to the active identifier
            rows=rows
        )

        # add/remove/specials UI list Menu
        col = row.column(align=True)
        col.operator("gptools.stroke_set_add", icon='ADD', text="")
        col.operator("gptools.stroke_set_remove", icon='REMOVE', text="")
        col.menu("GPTOOLS_MT_stroke_sets_context_menu", icon='DOWNARROW_HLT', text="")

        # move up/down arrows
        if len(gp.stroke_sets) > 0:
            col.separator()
            col.operator("gptools.stroke_set_move", icon='TRIA_UP', text="").direction = 'UP'
            col.operator("gptools.stroke_set_move", icon='TRIA_DOWN', text="").direction = 'DOWN'

        # buttons
        row = layout.row()

        sub = row.row(align=True)
        sub.operator("gptools.stroke_set_assign", text="Assign")
        sub.operator("gptools.stroke_set_unassign", text="Remove")

        sub = row.row(align=True)
        sub.operator("gptools.stroke_set_select", text="Select")
        sub.operator("gptools.stroke_set_deselect", text="Deselect")



class GPTOOLS_UL_stroke_set(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        sel_set = item
        layout.prop(item, "name", text="", icon='GROUP_BONE', emboss=False)
        if self.layout_type in ('DEFAULT', 'COMPACT'):
            layout.prop(item, "is_selected", text="")


class GPTOOLS_MT_stroke_set_create(Menu):
    bl_label = "Choose Stroke Set"

    def draw(self, context):
        layout = self.layout
        layout.operator("gptools.stroke_set_add_and_assign",
                        text="New Stroke Set")


class GPTOOLS_MT_stroke_sets_select(Menu):
    bl_label = 'Select Stroke Set'

    @classmethod
    def poll(cls, context):
        return GPTOOLS_OT_stroke_set_select.poll(context)

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'EXEC_DEFAULT'
        for idx, sel_set in enumerate(context.object.data.stroke_sets):
            props = layout.operator(GPTOOLS_OT_stroke_set_select.bl_idname, text=sel_set.name)
            props.stroke_set_index = idx


# Operators ###################################################################

class PluginOperator(Operator):
    """Operator only available for objects of type gpature in pose mode."""
    @classmethod
    def poll(cls, context):
        return (context.object.type == 'GPENCIL')


class NeedSelSetPluginOperator(PluginOperator):
    """Operator only available if the gpature has a selected selection set."""
    @classmethod
    def poll(cls, context):
        if not super().poll(context):
            return False
        gp = context.object.data
        return 0 <= gp.active_stroke_set < len(gp.stroke_sets)


class GPTOOLS_OT_stroke_set_delete_all(PluginOperator):
    bl_idname = "gptools.stroke_set_delete_all"
    bl_label = "Delete All Sets"
    bl_description = "Deletes All Stroke Sets"
    bl_options = {'UNDO', 'REGISTER'}

    def execute(self, context):
        gp = context.object.data
        gp.stroke_sets.clear()
        return {'FINISHED'}


class GPTOOLS_OT_stroke_set_remove_strokes(PluginOperator):
    bl_idname = "gptools.stroke_set_remove_strokes"
    bl_label = "Remove Selected Strokes from All Sets"
    bl_description = "Removes the Selected Strokes from All Sets"
    bl_options = {'UNDO', 'REGISTER'}

    def execute(self, context):
        gp = context.object.data

        # iterate only the selected bones in current pose that are not hidden
        for bone in context.selected_pose_bones:
            for selset in gp.stroke_sets:
                if bone.name in selset.bone_ids:
                    idx = selset.bone_ids.find(bone.name)
                    selset.bone_ids.remove(idx)

        return {'FINISHED'}


class GPTOOLS_OT_stroke_set_move(NeedSelSetPluginOperator):
    bl_idname = "gptools.stroke_set_move"
    bl_label = "Move Stroke Set in List"
    bl_description = "Move the active Stroke Set up/down the list of sets"
    bl_options = {'UNDO', 'REGISTER'}

    direction: EnumProperty(
        name="Move Direction",
        description="Direction to move the active Stroke Set: UP (default) or DOWN",
        items=[
            ('UP', "Up", "", -1),
            ('DOWN', "Down", "", 1),
        ],
        default='UP',
        options={'HIDDEN'},
    )

    @classmethod
    def poll(cls, context):
        if not super().poll(context):
            return False
        gp = context.object.data
        return len(gp.stroke_sets) > 1

    def execute(self, context):
        gp = context.object.data

        active_idx = gp.active_stroke_set
        new_idx = active_idx + (-1 if self.direction == 'UP' else 1)

        if new_idx < 0 or new_idx >= len(gp.stroke_sets):
            return {'FINISHED'}

        gp.stroke_sets.move(active_idx, new_idx)
        gp.active_stroke_set = new_idx

        return {'FINISHED'}


class GPTOOLS_OT_stroke_set_add(PluginOperator):
    bl_idname = "pose.stroke_set_add"
    bl_label = "Create Stroke Set"
    bl_description = "Creates a new empty Stroke Set"
    bl_options = {'UNDO', 'REGISTER'}

    def execute(self, context):
        gp = context.object.data
        sel_sets = gp.stroke_sets
        new_sel_set = sel_sets.add()
        new_sel_set.name = uniqify("StrokeSet", sel_sets.keys())

        # select newly created set
        gp.active_stroke_set = len(sel_sets) - 1

        return {'FINISHED'}


class GPTOOLS_OT_stroke_set_remove(NeedSelSetPluginOperator):
    bl_idname = "gptools.stroke_set_remove"
    bl_label = "Delete Stroke Set"
    bl_description = "Delete a Stroke Set"
    bl_options = {'UNDO', 'REGISTER'}

    def execute(self, context):
        gp = context.object.data

        gp.stroke_sets.remove(gp.active_stroke_set)

        # change currently active selection set
        numsets = len(gp.stroke_sets)
        if (gp.active_stroke_set > (numsets - 1) and numsets > 0):
            gp.active_stroke_set = len(gp.stroke_sets) - 1

        return {'FINISHED'}


class GPTOOLS_OT_stroke_set_assign(PluginOperator):
    bl_idname = "gptools.stroke_set_assign"
    bl_label = "Add Bones to Stroke Set"
    bl_description = "Add selected strokes to Stroke Set"
    bl_options = {'UNDO', 'REGISTER'}

    def invoke(self, context, event):
        gp = context.object.data

        if not (gp.active_stroke_set < len(gp.stroke_sets)):
            bpy.ops.wm.call_menu("INVOKE_DEFAULT",
                                 name="GPTOOLS_MT_stroke_set_create")
        else:
            bpy.ops.gptools.stroke_set_assign('EXEC_DEFAULT')

        return {'FINISHED'}

    def execute(self, context):
        gp = context.object.data
        act_sel_set = gp.stroke_sets[gp.active_stroke_set]

        # iterate only the selected bones in current pose that are not hidden
        for bone in context.selected_pose_bones:
            if bone.name not in act_sel_set.bone_ids:
                bone_id = act_sel_set.bone_ids.add()
                bone_id.name = bone.name

        return {'FINISHED'}


class GPTOOLS_OT_stroke_set_unassign(NeedSelSetPluginOperator):
    bl_idname = "gptools.stroke_set_unassign"
    bl_label = "Remove Strokes from Stroke Set"
    bl_description = "Remove selected strokes from Stroke Set"
    bl_options = {'UNDO', 'REGISTER'}

    def execute(self, context):
        gp = context.object.data
        act_sel_set = gp.stroke_sets[gp.active_stroke_set]

        # iterate only the selected bones in current pose that are not hidden
        for bone in context.selected_pose_bones:
            if bone.name in act_sel_set.bone_ids:
                idx = act_sel_set.bone_ids.find(bone.name)
                act_sel_set.bone_ids.remove(idx)

        return {'FINISHED'}


class GPTOOLS_OT_stroke_set_select(NeedSelSetPluginOperator):
    bl_idname = "gptools.stroke_set_select"
    bl_label = "Select Stroke Set"
    bl_description = "Add Stroke Set strokes to current selection"
    bl_options = {'UNDO', 'REGISTER'}

    stroke_set_index: IntProperty(
        name='Selection Set Index',
        default=-1,
        description='Which Stroke Set to select; -1 uses the active Stroke Set',
        options={'HIDDEN'},
    )

    def execute(self, context):
        gp = context.object.data

        if self.stroke_set_index == -1:
            idx = gp.active_stroke_set
        else:
            idx = self.stroke_set_index
        sel_set = gp.stroke_sets[idx]

        for bone in context.visible_pose_bones:
            if bone.name in sel_set.bone_ids:
                bone.bone.select = True

        return {'FINISHED'}


class GPTOOLS_OT_stroke_set_deselect(NeedSelSetPluginOperator):
    bl_idname = "gptools.stroke_set_deselect"
    bl_label = "Deselect Stroke Set"
    bl_description = "Remove Stroke Set strokes from current selection"
    bl_options = {'UNDO', 'REGISTER'}

    def execute(self, context):
        gp = context.object.data
        act_sel_set = gp.stroke_sets[gp.active_stroke_set]

        for bone in context.selected_pose_bones:
            if bone.name in act_sel_set.bone_ids:
                bone.bone.select = False

        return {'FINISHED'}


class GPTOOLS_OT_stroke_set_add_and_assign(PluginOperator):
    bl_idname = "gptools.stroke_set_add_and_assign"
    bl_label = "Create and Add Strokes to Stroke Set"
    bl_description = "Creates a new Stroke Set with the currently selected strokes"
    bl_options = {'UNDO', 'REGISTER'}

    def execute(self, context):
        bpy.ops.gptools.stroke_set_add('EXEC_DEFAULT')
        bpy.ops.gptools.stroke_set_assign('EXEC_DEFAULT')
        return {'FINISHED'}


class GPTOOLS_OT_stroke_set_copy(NeedSelSetPluginOperator):
    bl_idname = "gptools.stroke_set_copy"
    bl_label = "Copy Stroke Set(s)"
    bl_description = "Copies the selected Stroke Set(s) to the clipboard"
    bl_options = {'UNDO', 'REGISTER'}

    def execute(self, context):
        context.window_manager.clipboard = to_json(context)
        self.report({'INFO'}, 'Copied Stroke Set(s) to Clipboard')
        return {'FINISHED'}


class GPTOOLS_OT_stroke_set_paste(PluginOperator):
    bl_idname = "gptools.stroke_set_paste"
    bl_label = "Paste Stroke Set(s)"
    bl_description = "Adds new Stroke Set(s) from the Clipboard"
    bl_options = {'UNDO', 'REGISTER'}

    def execute(self, context):
        import json

        try:
            from_json(context, context.window_manager.clipboard)
        except (json.JSONDecodeError, KeyError):
            self.report({'ERROR'}, 'The clipboard does not contain a Stroke Set')
        else:
            # Select the pasted Selection Set.
            context.object.data.active_stroke_set = len(context.object.data.stroke_sets) - 1

        return {'FINISHED'}
    

# Helper Functions ############################################################
def menu_func_select_selection_set(self, context):
    self.layout.menu('GPTOOLS_MT_stroke_sets_select', text="Strokes Set")


def to_json(context) -> str:
    """Convert the selected Stroke Sets to JSON.

    Selected Sets are the active_stroke_set determined by the UIList
    plus any with the is_selected checkbox on."""
    import json

    gp = context.object.data
    active_idx = gp.active_stroke_set

    json_obj = {}
    for idx, sel_set in enumerate(context.object.data.stroke_sets):
        if idx == active_idx or sel_set.is_selected:
            bones = [bone_id.name for bone_id in sel_set.bone_ids]
            json_obj[sel_set.name] = bones

    return json.dumps(json_obj)


def from_json(context, as_json: str):
    """Add the stroke sets (one or more) from JSON."""
    import json

    json_obj = json.loads(as_json)
    gp_sel_sets = context.object.data.stroke_sets

    for name, bones in json_obj.items():
        new_sel_set = gp_sel_sets.add()
        new_sel_set.name = uniqify(name, gp_sel_sets.keys())
        for bone_name in bones:
            bone_id = new_sel_set.bone_ids.add()
            bone_id.name = bone_name


def uniqify(name: str, other_names: list) -> str:
    """Return a unique name with .xxx suffix if necessary.

    Example usage:

    >>> uniqify('hey', ['there'])
    'hey'
    >>> uniqify('hey', ['hey.001', 'hey.005'])
    'hey'
    >>> uniqify('hey', ['hey', 'hey.001', 'hey.005'])
    'hey.002'
    >>> uniqify('hey', ['hey', 'hey.005', 'hey.001'])
    'hey.002'
    >>> uniqify('hey', ['hey', 'hey.005', 'hey.001', 'hey.left'])
    'hey.002'
    >>> uniqify('hey', ['hey', 'hey.001', 'hey.002'])
    'hey.003'

    It also works with a dict_keys object:
    >>> uniqify('hey', {'hey': 1, 'hey.005': 1, 'hey.001': 1}.keys())
    'hey.002'
    """

    if name not in other_names:
        return name

    # Construct the list of numbers already in use.
    offset = len(name) + 1
    others = (n[offset:] for n in other_names
              if n.startswith(name + '.'))
    numbers = sorted(int(suffix) for suffix in others
                     if suffix.isdigit())

    # Find the first unused number.
    min_index = 1
    for num in numbers:
        if min_index < num:
            break
        min_index = num + 1
    return "{}.{:03d}".format(name, min_index)