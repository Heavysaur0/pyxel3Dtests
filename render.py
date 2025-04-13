from pyglm import glm
from collections import deque
import numpy as np
import pyxel

from options import W_WIDTH, W_HEIGHT


class Render:
    def __init__(self, camera, cull_face: bool = False, depth_sort: bool = False):
        self.camera = camera
        self.triangle_stack = deque()
        self.triangle_array = None

        self.cull_face = cull_face
        self.depth_sort = depth_sort

    def clear(self):
        self.triangle_stack = deque()
        self.triangle_array = None

    def render_gl_position(self, vertex, m_model) -> glm.vec4:
        return self.camera.projection_matrix * self.camera.view_matrix * m_model * glm.vec4(vertex, 1.0)

    def render_vertex(self, vertex, m_model) -> tuple[glm.vec3, glm.vec4]:
        temp = m_model * glm.vec4(vertex, 1.0)
        frag_pos = glm.vec3(temp)
        gl_position = self.camera.m_proj * self.camera.m_view * temp
        return frag_pos, gl_position

    def render_normal(self, normal, m_inv_transp) -> glm.vec3:
        # m inv transpose = glm.inverse(glm.transpose(m_model))
        return glm.normalize(m_inv_transp * normal)

    def append_triangle(self, triangle, normal, color):
        """Add a triangle in the stack of the render (simulation of buffers)

        Args:
            * triangle (tuple[glm.vec4]): the position of the triangle in the frustum
            * normal (glm.vec3): normal vector of the triangle
            * color (np.uint8): pyxel color of the triangle
        """
        clipped = homogeneous_clip_triangle(triangle)
        if not clipped:
            print("Triangle is not rendered, fully outside frustum")
            return

        clipped = np.array([v[:3] / v[3] for v in clipped], dtype=np.float32)

        triangles = clip_triangle_to_unit_cube(*clipped[:3]) if len(clipped) == 3 else triangulate(clipped)

        if self.cull_face:
            v1 = triangles[0][2][:2] - triangles[0][1][:2]
            v2 = triangles[0][1][:2] - triangles[0][0][:2]
            if v1[0] * v2[1] - v1[1] * v2[0] >= 0:
                print("Triangle is not rendered, face is not in the correct direction")
                return

        [self.triangle_stack.append((tri, normal, color)) for tri in triangles]

    def draw(self):
        triangle_array = list(self.triangle_stack)
        if self.depth_sort:
            triangle_array.sort(key = lambda data: min(v[2] for v in data[0]), reverse=True)

        for triangle, normal, color in triangle_array:
            points = [(vertex[:2] + (1, 1)) * (W_WIDTH, W_WIDTH) / 2 for vertex in triangle]
            flatten_points = [point[i] for point in points for i in range(2)]
            pyxel.tri(*flatten_points, color)


def inside_homogeneous(v, plane):
    # Plane is a tuple (a, b, c, d) meaning ax + by + cz + dw >= 0
    return np.dot(v, plane) >= 0

def intersect_homogeneous(v1, v2, plane):
    # plane: (a, b, c, d)
    d1 = np.dot(v1, plane)
    d2 = np.dot(v2, plane)
    if d1 == d2:
        return v1  # avoid division by zero; shouldn't happen
    t = d1 / (d1 - d2)
    return v1 + t * (v2 - v1)

def clip_polygon_against_plane_homogeneous(polygon, plane):
    result = []
    prev = polygon[-1]
    prev_inside = inside_homogeneous(prev, plane)

    for curr in polygon:
        curr_inside = inside_homogeneous(curr, plane)

        if curr_inside:
            if not prev_inside:
                result.append(intersect_homogeneous(prev, curr, plane))
            result.append(curr)
        elif prev_inside:
            result.append(intersect_homogeneous(prev, curr, plane))

        prev = curr
        prev_inside = curr_inside

    return result

def homogeneous_clip_triangle(triangle):
    """
    Clip a triangle in homogeneous space (vec4s) to the canonical view frustum.

    Args:
        triangle: list of 3 numpy arrays (shape: (4,))

    Returns:
        list of vec4 (numpy array shape (4,)), the clipped polygon (can be >3 vertices),
        or [] if fully clipped out
    """
    planes = [
        np.array([ 1,  0,  0,  1]),  # x + w >= 0   (left)
        np.array([-1,  0,  0,  1]),  # -x + w >= 0  (right)
        np.array([ 0,  1,  0,  1]),  # y + w >= 0   (bottom)
        np.array([ 0, -1,  0,  1]),  # -y + w >= 0  (top)
        np.array([ 0,  0,  1,  1]),  # z + w >= 0   (near)
        np.array([ 0,  0, -1,  1]),  # -z + w >= 0  (far)
    ]

    polygon = list(triangle)
    for plane in planes:
        polygon = clip_polygon_against_plane_homogeneous(polygon, plane)
        if not polygon:
            return []

    return polygon

def inside(p, normal, offset):
    return np.dot(normal, p) <= offset

def intersect(p1, p2, normal, offset):
    direction = p2 - p1
    denom = np.dot(normal, direction)
    if denom == 0:
        return p1
    t = (offset - np.dot(normal, p1)) / denom
    return p1 + t * direction

def clip_polygon_against_plane(polygon, normal, offset):
    result = []
    prev = polygon[-1]
    prev_inside = inside(prev, normal, offset)

    for curr in polygon:
        curr_inside = inside(curr, normal, offset)

        if curr_inside:
            if not prev_inside:
                result.append(intersect(prev, curr, normal, offset))
            result.append(curr)
        elif prev_inside:
            result.append(intersect(prev, curr, normal, offset))

        prev = curr
        prev_inside = curr_inside

    return result

def triangulate(polygon):
    if len(polygon) < 3:
        return []
    triangles = []
    for i in range(1, len(polygon) - 1):
        triangles.append([polygon[0], polygon[i], polygon[i + 1]])
    return triangles

def clip_triangle_to_unit_cube(v0, v1, v2):
    poly = [np.array(v0), np.array(v1), np.array(v2)]
    planes = [
        (np.array([ 1, 0, 0]), 1),
        (np.array([-1, 0, 0]), 1),
        (np.array([ 0, 1, 0]), 1),
        (np.array([ 0,-1, 0]), 1),
        (np.array([ 0, 0, 1]), 1),
        (np.array([ 0, 0,-1]), 1)
    ]

    for normal, offset in planes:
        poly = clip_polygon_against_plane(poly, normal, offset)
        if not poly:
            return []

    return triangulate(poly)