from pyglm import glm
from collections import deque
import numpy as np
import pyxel

from options import W_WIDTH, W_HEIGHT


def render_normal(normal, m_inv_transp) -> glm.vec3:
    # m inv transpose = glm.inverse(glm.transpose(m_model))
    return glm.normalize(m_inv_transp * normal)


class Render:
    def __init__(self, camera, cull_face: bool = False, depth_sort: bool = False):
        self.camera = camera
        self.render_stack = deque()

        self.cull_face = cull_face
        self.depth_sort = depth_sort

    def clear(self):
        self.render_stack = deque()

    def render_gl_position(self, vertex, m_model) -> glm.vec4:
        return self.camera.projection_matrix * self.camera.view_matrix * m_model * glm.vec4(vertex, 1.0)

    def render_vertex(self, vertex, m_model) -> tuple[glm.vec3, glm.vec4]:
        temp = m_model * glm.vec4(vertex, 1.0)
        frag_pos = glm.vec3(temp)
        gl_position = self.camera.m_proj * self.camera.m_view * temp
        return frag_pos, gl_position

    def append_polygon(self, polygon, color, normal, fill = True, border = False):
        clipped = homogeneous_clip_polygon(polygon)
        if not clipped:
            # print("Triangle is not rendered, fully outside frustum")
            return

        clipped = np.array([v[:3] / v[3] for v in clipped], dtype=np.float32)

        if self.cull_face and len(clipped) > 2:
            v1 = clipped[1] - clipped[0]
            v2 = clipped[2] - clipped[1]
            if v1[0] * v2[1] - v1[1] * v2[0] < 0:
                # print("Triangle is not rendered, face is not in the correct direction")
                return

        self.render_stack.append((clipped, color, normal, fill, border))

    def depth_sort(self, data):
        pass


    def draw(self):
        polygons_array = list(self.render_stack)
        if self.depth_sort:
            polygons_array.sort(key=lambda data: sum(v[2] ** 2 for v in data[0]) / len(data[0]), reverse=True)

        for data in polygons_array:
            points, color, normal, fill, border = data
            points = [(vertex[:2] + (1, 1)) * (W_WIDTH, W_WIDTH) / 2 for vertex in points]

            for triangle in triangulate(points):
                flatten_points = [point[i] for point in triangle for i in range(2)]
                if fill:
                    pyxel.tri(*flatten_points, color)
                else:
                    pyxel.trib(*flatten_points, color)

            if border >= 0:
                for i in range(len(points)):
                    j = (i + 1) % len(points)
                    a, b = points[i], points[j]
                    pyxel.line(*a, *b, border)


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

        if curr_inside ^ prev_inside:
            result.append(intersect_homogeneous(prev, curr, plane))
        if curr_inside:
            result.append(curr)

        prev, prev_inside = curr, curr_inside

    return result


def homogeneous_clip_polygon(polygon):
    """
    Clip a triangle in homogeneous space (vec4s) to the canonical view frustum.

    Args:
        polygon: list of n numpy arrays (shape: (4,))

    Returns:
        list of vec4 (numpy array shape (4,)), the clipped polygon (can be >3 vertices),
        or [] if fully clipped out
    """
    planes = [
        np.array([1, 0, 0, 1]),  # x + w >= 0   (left)
        np.array([-1, 0, 0, 1]),  # -x + w >= 0  (right)
        np.array([0, 1, 0, 1]),  # y + w >= 0   (bottom)
        np.array([0, -1, 0, 1]),  # -y + w >= 0  (top)
        np.array([0, 0, 1, 1]),  # z + w >= 0   (near)
        np.array([0, 0, -1, 1]),  # -z + w >= 0  (far)
    ]

    for plane in planes:
        polygon = clip_polygon_against_plane_homogeneous(polygon, plane)
        if not polygon:
            return []

    return polygon

def triangulate(polygon):
    """Triangulate a polygon into multiple triangles
    /!\ Only works on convex shapes"""
    if len(polygon) < 3:
        return []
    triangles = []
    for i in range(1, len(polygon) - 1):
        triangles.append([polygon[0], polygon[i], polygon[i + 1]])
    return triangles
