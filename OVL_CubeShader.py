import bpy
import gpu
from gpu_extras.batch import batch_for_shader
import mathutils


def scale_coords(coords, scale):
    coords = [((axis * scale)for axis in vector) for vector in coords]
    return coords

def locate_coords(coords, location):
    coords = [(x + location[0], y+ location[1], z+ location[2]) for x, y, z in coords]
    return coords

def rotate_coords(coords, rotation):
    out_coords = []
    for coord in coords:
        coord = mathutils.Vector(coord)
        coord.rotate(rotation)
        out_coords.append(coord)
    return out_coords

def draw(location, scale, color, rotation):
    coords = (
        (-1, -1, -1), (+1, -1, -1),
        (-1, +1, -1), (+1, +1, -1),
        (-1, -1, +1), (+1, -1, +1),
        (-1, +1, +1), (+1, +1, +1))
    indices = (
        (0, 1), (0, 2), (1, 3), (2, 3),
        (4, 5), (4, 6), (5, 7), (6, 7),
        (0, 4), (1, 5), (2, 6), (3, 7))
    shader = gpu.shader.from_builtin('UNIFORM_COLOR')

    coords = rotate_coords(coords, rotation)
    coords = scale_coords(coords, scale)
    coords = locate_coords(coords, location)

    batch = batch_for_shader(shader, 'LINES', {"pos": coords}, indices=indices)

    shader.uniform_float("color", color)
    # make shader use depth
    gpu.state.depth_test_set('LESS')
    
    batch.draw(shader)
    gpu.state.depth_test_set('NONE')

