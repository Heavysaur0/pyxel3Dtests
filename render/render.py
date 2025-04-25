from pyglm import glm
from collections import deque
import numpy as np
import pyxel
import time

from options import W_HALF_WIDTH, W_HALF_HEIGHT


PLANES = [
    (0, +1),  # x + w >= 0   (left)
    (0, -1),  # -x + w >= 0  (right)
    (1, +1),  # y + w >= 0   (bottom)
    (1, -1),  # -y + w >= 0  (top)
    (2, +1),  # z + w >= 0   (near)
    (2, -1),  # -z + w >= 0  (far)
]


def render_normal(normal, m_inv_transp) -> glm.vec3:
    """Render a normal vector thanks the inverse of the transpose of the model matrix

    Args:
        normal (glm.vec3): normal 3D vector
        m_inv_transp (glm.mat3): inverse of transpose of model matrix 
            (it is glm.inverse(glm.transpose(m_model)))

    Returns:
        glm.vec3: rendered normal
    """
    # m inv transpose = glm.inverse(glm.transpose(m_model))
    return glm.normalize(m_inv_transp * normal)


def lerp(a, b, t):
    """Linear interpolation

    Args:
        a (Any): _description_
        b (Any): _description_
        t (float): _description_

    Returns:
        Any: _description_
    """
    return a + t * (b - a)


def inside_homogeneous_fast(v, axis, sign):
    """Tells if a point is "inside" or not a plane
    Uses plane optimization

    Args:
        v (Iterable): 3D vertex
        axis (int): which axis is the plane on (0 for x, 1 for y and 2 for z)
        sign (int): the sign of the plane (-1 or 1)

    Returns:
        bool: True if the point is "inside" the plane, False if it's "outside"
    """
    return sign * v[axis] + v[3] >= 0


def intersect_homogeneous_fast(v1, v2, axis, sign):
    """Find the intersection of a line (v1 <-> v2) and a plane (axis, sign)
    Uses plane optimization

    Args:
        v1 (np.ndarray): first vertex of the line
        v2 (np.ndarray): second vertex of the line
        axis (int): which axis is the plane on (0 for x, 1 for y and 2 for z)
        sign (int): the sign of the plane (-1 or 1)

    Returns:
        np.ndarray: intersection of the line and the plane
    """
    d1 = sign * v1[axis] + v1[3]
    d2 = sign * v2[axis] + v2[3]
    if d1 == d2:
        return v1
    t = d1 / (d1 - d2)
    return lerp(v1, v2, t)


def clip_against_plane_fast(polygon, axis, sign):
    """Clip a polygon against a plane
    Uses plane optimization

    Args:
        polygon (_type_): convex input polygon
        axis (int): which axis is the plane on (0 for x, 1 for y and 2 for z)
        sign (int): the sign of the plane (-1 or 1)

    Returns:
        list: the list of corners return, which is the clipped polygon
    """
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


def clip_polygon_against_plane_fast_flags(polygon, axis, sign, flags, buf) -> list:
    """Clip a polygon against a plane thanks to precomputed flags
    Uses plane optimization

    Args:
        polygon (_type_): convex input polygon
        axis (int): which axis is the plane on (0 for x, 1 for y and 2 for z)
        sign (int): the sign of the plane (-1 or 1)
        flags (list[bool]): precomputed flags, list of booleans telling which corners are inside the plane or not
        buf (list[np.ndarray]): a buffer preallocated list of size n + 6 used to return polygon
            n + 6 for worst case scenario for a convex polygon full plane clip in 3D space (polygon being n-sided)

    Returns:
        list: the list of corners return, which is the clipped polygon
    """
    # max possible after clip is 2 times the number of corners of polygon
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
    """Clip a convex polygon (in 3D space but all points on a plane) in [-1; 1]^3
    Uses plane optimization

    Args:
        polygon (list[np.ndarray]): list of corners of the convex polygon

    Returns:
        list[np.ndarray]: list of corners of the clipped convex polygon
    """
    buf = [False for _ in range(len(polygon) + 6)] # Worst case scenario is n + 6 for a convex polygon plane clip in 3D 
    
    for axis, sign in PLANES:
        flags = np.array([inside_homogeneous_fast(v, axis, sign) for v in polygon])
        
        if all(flags):
            continue
        if not any(flags):
            return []
        
        polygon = clip_polygon_against_plane_fast_flags(polygon, axis, sign, flags, buf)
        
        if not polygon:
            return []
    return polygon


def triangulate(polygon):
    """Triangulate a polygon into multiple triangles
    /!\ Only works on convex shapes

    Args:
        polygon (list[Any]): list of corners of the polygon

    Yields:
        tuple[Any, Any, Any]: tuple of 3 corners (a triangle)
    """
    if len(polygon) < 3:
        return
    for i in range(2, len(polygon)):
        yield polygon[0], polygon[i - 1], polygon[i]


class Render:
    """Class for 3D rendering"""
    
    __slots__ = ('camera', 'render_stack', 'num_vertices', 'num_triangles', 'cull_face', 'depth_sort')
    
    def __init__(self, camera, cull_face: bool = False, depth_sort: bool = False):
        """Class constructor

        Args:
            camera (Camera): camera object for rendering origin
            cull_face (bool, optional): use backface culling or not. Defaults to False.
            depth_sort (bool, optional): sort which faces are displayed first with depth or not. Defaults to False.
        """
        self.camera = camera
        self.render_stack = deque()
        self.num_vertices = 0
        self.num_triangles = 0

        self.cull_face = cull_face
        self.depth_sort = depth_sort

    def clear(self):
        """Clear the rendering stack (essential before drawing objects)"""
        self.render_stack = deque()
        self.num_vertices = 0
        self.num_triangles = 0

    def render_gl_position(self, vertex, m_model) -> glm.vec4:
        """Render a vertex in 3D space to 4D homogeneous camera frustum space

        Args:
            vertex (glm.vec3): vertex to be rendered
            m_model (glm.mat4): model matrix of the vertex

        Returns:
            glm.vec4: 4D homogeneous vertex from camera frustum space
        """
        self.num_vertices += 1
        return self.camera.projection_matrix * self.camera.view_matrix * m_model * glm.vec4(vertex, 1.0)

    def render_vertex(self, vertex, m_model) -> tuple[glm.vec3, glm.vec4]:
        """Render a vertex in 3D space to 4D homogeneous camera frustum space and to frag pos

        Args:
            vertex (glm.vec3): vertex to be rendered
            m_model (glm.mat4): model matrix of the vertex

        Returns:
            tuple[glm.vec3, glm.vec4]: fragment position and 4D homogeneous vertex from camera frustum space
        """
        frag_pos = glm.vec3(m_model * glm.vec4(vertex, 1.0))
        gl_position = self.render_gl_position(vertex, m_model)
        return frag_pos, gl_position

    def append_polygon(self, polygon, color, normal, fill = True, border = -1):
        """Append a polygon to the rendering stack

        Args:
            polygon (list[np.ndarray]): list of corners that make the convex polygon
            color (int): pyxel face color
            normal (np.ndarray): useless, the normal vector of the face
            fill (bool, optional): fill the face or not (for debugging). Defaults to True.
            border (int, optional): add to the face a border (pyxel of the color, -1 for no border). Defaults to -1.
        """
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
        """Draw all the polygons of the rendering stack to the screen"""
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
