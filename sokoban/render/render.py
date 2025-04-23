from pyglm import glm
from collections import deque
import numpy as np
import pyxel
import time

from render.options import W_HALF_WIDTH, W_HALF_HEIGHT


PLANES = [
    (0, +1),  # x + w >= 0   (left)
    (0, -1),  # -x + w >= 0  (right)
    (1, +1),  # y + w >= 0   (bottom)
    (1, -1),  # -y + w >= 0  (top)
    (2, +1),  # z + w >= 0   (near)
    (2, -1),  # -z + w >= 0  (far)
]


def render_normal(normal, m_inv_transp) -> glm.vec3:
    # m inv transpose = glm.inverse(glm.transpose(m_model))
    return glm.normalize(m_inv_transp * normal)


def lerp(a, b, t):
    return a + t * (b - a)


def inside_homogeneous_fast(v, axis, sign):
    return sign * v[axis] + v[3] >= 0


def intersect_homogeneous_fast(v1, v2, axis, sign):
    d1 = sign * v1[axis] + v1[3]
    d2 = sign * v2[axis] + v2[3]
    if d1 == d2:
        return v1
    t = d1 / (d1 - d2)
    return lerp(v1, v2, t)


def clip_against_plane_fast(polygon, axis, sign):
    n = len(polygon)
    # max possible after clip is 2*n
    buf = [None] * (2*n)
    out_count = 0

    prev = polygon[-1]
    prev_in = (sign * prev[axis] + prev[3] >= 0)

    for curr in polygon:
        curr_in = (sign * curr[axis] + curr[3] >= 0)

        if curr_in ^ prev_in:
            # insert intersection
            buf[out_count] = intersect_homogeneous_fast(prev, curr, axis, sign)
            out_count += 1
        if curr_in:
            buf[out_count] = curr
            out_count += 1

        prev, prev_in = curr, curr_in

    # slice down to actual count
    return buf[:out_count]


def clip_polygon_against_plane_fast_flags(polygon, axis, sign, flags) -> list:
    # max possible after clip is 2 times the number of corners of polygon
    buf = [None for _ in range(2 * len(polygon))]
    out_count = 0

    for i, curr in enumerate(polygon):
        if flags[i]:
            if not flags[i-1]:
                buf[out_count] = intersect_homogeneous_fast(polygon[i - 1], curr, axis, sign)
                out_count += 1
            buf[out_count] = curr
            out_count += 1
        elif flags[i-1]:
            buf[out_count] = intersect_homogeneous_fast(polygon[i - 1], curr, axis, sign)
            out_count += 1

    # slice down to actual count
    if out_count:
        return buf[:out_count]
    return []


def homogeneous_clip_polygon_fast(polygon):
    for axis, sign in PLANES:
        flags = np.array([inside_homogeneous_fast(v, axis, sign) for v in polygon])
        
        if all(flags):
            continue
        if not any(flags):
            return []
        
        polygon = clip_polygon_against_plane_fast_flags(polygon, axis, sign, flags)
        
        if not polygon:
            return []
    return polygon


def triangulate(polygon):
    """Triangulate a polygon into multiple triangles
    /!\ Only works on convex shapes"""
    if len(polygon) < 3:
        return
    for i in range(2, len(polygon)):
        yield polygon[0], polygon[i - 1], polygon[i]


class Render:
    __slots__ = ('camera', 'render_stack', 'num_vertices', 'num_triangles', 'cull_face', 'depth_sort')
    
    def __init__(self, camera, cull_face: bool = False, depth_sort: bool = False):
        self.camera = camera
        self.render_stack = deque()
        self.num_vertices = 0
        self.num_triangles = 0

        self.cull_face = cull_face
        self.depth_sort = depth_sort

    def clear(self):
        self.render_stack = deque()
        self.num_vertices = 0
        self.num_triangles = 0

    def render_gl_position(self, vertex, m_model) -> glm.vec4:
        self.num_vertices += 1
        return self.camera.projection_matrix * self.camera.view_matrix * m_model * glm.vec4(vertex, 1.0)

    def render_vertex(self, vertex, m_model) -> tuple[glm.vec3, glm.vec4]:
        frag_pos = glm.vec3(m_model * glm.vec4(vertex, 1.0))
        gl_position = self.render_gl_position(vertex, m_model)
        return frag_pos, gl_position

    def append_polygon(self, polygon, color, normal, fill = True, border = False):
        clipped = homogeneous_clip_polygon_fast(polygon)
        if not clipped:
            # print("Triangle is not rendered, fully outside frustum")
            return

        clipped = np.array([v[:3] / v[3] for v in clipped], dtype=np.float32)

        if self.cull_face and len(clipped) > 2:
            v1 = clipped[1] - clipped[0]
            v2 = clipped[2] - clipped[1]
            if v1[0] * v2[1] < v1[1] * v2[0]:
                # print("Triangle is not rendered, face is not in the correct direction")
                return

        self.render_stack.append((clipped, color, normal, fill, border))

    def draw(self):
        # start_time = time.perf_counter()
        
        polygons_array = list(self.render_stack)
        if self.depth_sort:
            polygons_array.sort(key=lambda data: sum(v[2] ** 2 for v in data[0]) / len(data[0]), reverse=True)

        for points, color, _, fill, border in polygons_array:
            points = [((vertex[0] + 1) * W_HALF_WIDTH, (1 - vertex[1]) * W_HALF_HEIGHT) for vertex in points]

            for triangle in triangulate(points):
                flatten_points = [point[i] for point in triangle for i in range(2)]
                if fill:
                    pyxel.tri(*flatten_points, color)
                else:
                    pyxel.trib(*flatten_points, color)
                self.num_triangles += 1

            if border >= 0:
                for i in range(len(points)):
                    j = (i + 1) % len(points)
                    a, b = points[i], points[j]
                    pyxel.line(*a, *b, border)
        
        # end_time = time.perf_counter()
        # print(f"    render.draw(): {end_time - start_time:.6f}s")
