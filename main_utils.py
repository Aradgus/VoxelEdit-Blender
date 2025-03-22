import bpy
import sys
import bpy_extras
from bpy_extras import view3d_utils
import mathutils
from mathutils import Vector, Matrix
import bmesh
from mathutils.bvhtree import BVHTree

def get_mouse_in_3d(event, region, rv3d):
    coord = (event.mouse_region_x, event.mouse_region_y)
    depthLocation = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
    loc = view3d_utils.region_2d_to_location_3d(region, rv3d, coord, depthLocation)
    return loc

def ray_cast_bvh_object(origin, direction, distance):
    obj_mesh = bpy.context.active_object.data
    obj = bpy.context.active_object
    # Create a BVH tree from the target_object mesh
    bm = bmesh.from_edit_mesh(obj_mesh) 

    # this is for getting the real position of the bmesh, if this is not used it whould not apply the 
    # objects transformations to the mesh and whould get wrong hit positions when the object is transformt
    transform_matrix = obj.matrix_world 
    bm.transform(transform_matrix)

    bm.faces.ensure_lookup_table()
    
    bvh_tree = BVHTree.FromBMesh(bm)
    
    location, normal, index, distance = bvh_tree.ray_cast(origin, direction, distance)
    # rotate the normal by the obj rotation to make the vector look in the right direction
    normal.rotate(obj.rotation_euler)

    # the vec vector can be used to scale the normal vector, usefull if the voxel size is different
    vec = mathutils.Vector((1,1,1))
    vec = vec * normal
    add_location = bm.faces[index].calc_center_median() + vec

    #this transforms the bmesh back to its original position
    bm.transform(transform_matrix.inverted())
    
    bm.free()
    return location, normal, index, distance, add_location

