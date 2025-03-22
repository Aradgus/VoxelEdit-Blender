import bpy
import sys
from bpy_extras import view3d_utils
import mathutils
from . import main_utils
from . import OVL_CubeShader

draw_location = (1,1,1)
draw_scale = 1.2
draw_color = (1,1,1,1)
draw_rotation = mathutils.Euler((0,0,0), "XYZ")

def draw_wrapper():
    global draw_location, draw_scale, draw_color, draw_rotation 
    OVL_CubeShader.draw(draw_location, draw_scale, draw_color, draw_rotation)

class VoxelTool(bpy.types.WorkSpaceTool):
    bl_label = "VoxelTool"
    bl_idname = "voxeltool.test1"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'voxeltool'
    bl_icon = "None" # this may raise an error
    bl_context_mode = 'EDIT_MESH'
    bl_widget = None
    bl_keymap = (
        ("voxeltool.add_voxel", {"type": 'LEFTMOUSE', "value": 'PRESS'},
         {"properties": [("wait_for_input", False)]}),
        ("voxeltool.deletevoxel", {"type": 'RIGHTMOUSE', "value": 'PRESS'},
         {"properties": [("wait_for_input", False)]}),
        ("wm.call_menu_pie", {"type": 'G', "value": 'PRESS'},
         {"properties": [("name", "VIEW3D_MT_PIE_vgroup_select")]}),
    )


    def draw_settings(context, layout, tool):
        layout.label(text="Active Group:")
        if context.active_object.vertex_groups.active:
            layout.label(text=str(context.active_object.vertex_groups.active.name))
        pass

class DeleteVoxel(bpy.types.Operator):
    bl_idname = "voxeltool.deletevoxel"
    bl_label = "DeleteVoxel"

    def modal(self, context, event):
        global draw_location, draw_scale, draw_color, draw_rotation 
        region = context.region
        rv3d = context.region_data
        coord = (event.mouse_region_x, event.mouse_region_y)
        loc = event.mouse_region_x, event.mouse_region_y

        dir_vec = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
        origin = rv3d.view_matrix.inverted()

        if event.type == 'MOUSEMOVE':                    
            bpy.ops.view3d.select(location=loc)
            bpy.ops.view3d.select(deselect_all=True, location=loc)
            bpy.ops.mesh.select_linked()
            
            location, normal, index, distance, add_location = main_utils.ray_cast_bvh_object(origin.translation, dir_vec, distance=sys.float_info.max)
            vec = mathutils.Vector((1,1,1))
            vec = vec * normal
            draw_location = add_location - vec * 2

            context.area.tag_redraw()

        elif event.type == 'RIGHTMOUSE':
            bpy.ops.view3d.select(location=loc)
            bpy.ops.view3d.select(deselect_all=True, location=loc)
            bpy.ops.mesh.select_linked()
            bpy.ops.mesh.delete(type='VERT')

            bpy.ops.ed.undo_push(message="Delete Voxel")
            context.space_data.draw_handler_remove(self._handle, 'WINDOW')
            context.area.tag_redraw()

            return {'FINISHED'}

        elif event.type in {'LEFTMOUSE', 'ESC'}:
            context.space_data.draw_handler_remove(self._handle, 'WINDOW')
            context.area.tag_redraw()
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        global draw_location, draw_scale, draw_color, draw_rotation 
        draw_scale = 1.1
        draw_color = (1,0,0,1)
        draw_rotation = context.active_object.rotation_euler 
        region = context.region
        rv3d = context.region_data
        coord = (event.mouse_region_x, event.mouse_region_y)
        self.obj = bpy.context.active_object

        dir_vec = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
        origin = rv3d.view_matrix.inverted()

        location, normal, index, distance, add_location = main_utils.ray_cast_bvh_object(origin.translation, dir_vec, distance=sys.float_info.max)
        vec = mathutils.Vector((1,1,1))
        vec = vec * normal
        draw_location = add_location - vec * 2

        loc = event.mouse_region_x, event.mouse_region_y
        bpy.ops.view3d.select(location=loc)
        bpy.ops.view3d.select(deselect_all=True, location=loc)
        bpy.ops.mesh.select_linked()
        if not hasattr(self, "_handle"):
            self._handle = context.space_data.draw_handler_add(draw_wrapper, (), 'WINDOW', 'POST_VIEW')
            context.area.tag_redraw()
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}


class AddVoxel(bpy.types.Operator):
    bl_idname = "voxeltool.add_voxel"
    bl_label = "Add Voxel"

    def modal(self, context, event):
        global current_mouse_x, current_mouse_y
        global draw_location, draw_scale, draw_color, draw_rotation 
        region = context.region
        rv3d = context.region_data
        coord = (event.mouse_region_x, event.mouse_region_y)

        dir_vec = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
        origin = rv3d.view_matrix.inverted()
        if event.type == 'MOUSEMOVE':
            location, normal, index, distance, add_location = main_utils.ray_cast_bvh_object(origin.translation, dir_vec, distance=sys.float_info.max)
            draw_location = add_location
            context.area.tag_redraw()
            return {'PASS_THROUGH'}

        elif event.type == 'LEFTMOUSE':
            scene = context.scene
            region = context.region
            rv3d = context.region_data

            location, normal, index, distance, add_location = main_utils.ray_cast_bvh_object(origin.translation, dir_vec, distance=sys.float_info.max)

            bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', location = add_location, rotation=(context.active_object.rotation_euler), scale=(1, 1, 1)) 
            bpy.ops.object.vertex_group_assign()
            bpy.ops.ed.undo_push(message="Add Voxel")
            
            context.space_data.draw_handler_remove(self._handle, 'WINDOW')
            return {'FINISHED'}

        if event.type in {'RIGHTMOUSE', 'ESC'}:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            context.area.tag_redraw()
            return {'CANCELLED'}

        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        global draw_location, draw_scale, draw_color, draw_rotation 
        draw_scale = 1.0
        draw_color = (0,1,0.5,1)
        draw_rotation = context.active_object.rotation_euler 
        region = context.region
        rv3d = context.region_data
        coord = (event.mouse_region_x, event.mouse_region_y)

        dir_vec = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
        origin = rv3d.view_matrix.inverted()
        location, normal, index, distance, add_location = main_utils.ray_cast_bvh_object(origin.translation, dir_vec, distance=sys.float_info.max)
        draw_location = add_location
        if not hasattr(self, "_handle"):
            self._handle = context.space_data.draw_handler_add(draw_wrapper, (), 'WINDOW', 'POST_VIEW')
            context.area.tag_redraw()
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

classes = [DeleteVoxel, AddVoxel]
# Factory function to register classes
class_register, class_unregister = bpy.utils.register_classes_factory(classes)

def register():
    bpy.utils.register_tool(VoxelTool, separator=True)
    class_register()


def unregister():
    bpy.utils.unregister_tool(VoxelTool)
    class_unregister()



if __name__ == "__main__":
    register()

