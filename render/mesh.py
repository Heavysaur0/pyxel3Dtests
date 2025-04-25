from pyglm import glm
import numpy as np


class Mesh:
    """Mesh class for 3D model data"""
    
    __slots__ = ('vertex_data', 'index_data', 'color_data', 'num_triangles', 'normal_data', 'fill_data', 'outer_border_data')

    def __init__(self, vertex_data, index_data, color_data,
                 normal_data = None, fill_data = None, outer_border_data = None):
        """Class constructor

        Args:
            vertex_data (Iterable[Iterable]): all vertices that compose the 3D model
            index_data (Iterable[int]): each vertex indices for each face
            color_data (Iterable[int]): each pyxel color for each face
            normal_data (Iterable[Iterable] | None, optional): each normal vector for each face. 
                Defaults to None to compute normal on the fly.
            fill_data (Iterable[bool] | None, optional): fill or not each face. 
                Defaults to None to initialize values to True.
            outer_border_data (Iterable[int] | None, optional): add a border or not for each face (pyxel color or -1 respectively). 
                Defaults to None to initialize values to -1.
        """
        self.vertex_data = np.array(vertex_data, dtype=np.float32)

        # index_dtype = self.get_index_type()
        # self.index_data = np.array(index_data, dtype=index_dtype)
        self.index_data = index_data # inhomogeneous shape
        self.color_data = np.array(color_data, dtype=np.uint8)
        self.num_triangles = len(index_data)

        if normal_data is None:
            self.normal_data = self.get_normals()
        else:
            self.normal_data = np.array(normal_data, dtype=np.float32)

        if outer_border_data is None:
            self.outer_border_data = np.zeros((self.num_triangles, ), dtype=np.int8) - 1
        else:
            self.outer_border_data = np.array(outer_border_data, dtype=np.int8)
        
        if fill_data is None:
            self.fill_data = np.ones((self.num_triangles, ), dtype=bool)
        else:
            self.fill_data = np.array(fill_data, dtype=bool)

    # def get_index_type(self):
    #     """Return the numpy index type to use

    #     Returns:
    #         _type_: _description_
    #     """
    #     length = len(self.vertex_data)
    #     if length <= 256:
    #         return np.uint8
    #     if length <= 65536:
    #         return np.uint16
    #     if length <= 4294967296:
    #         return np.uint32
    #     return np.uint64

    def get_normals(self):
        """Compute normal data if none were given

        Returns:
            np.ndarray: numpy array of all normals
        """
        normal_data = np.zeros((self.num_triangles, 3), dtype=np.float32)
        for index in range(self.num_triangles):
            indices = self.index_data[index]
            if len(indices) == 3:
                p0, p1, p2 = [self.vertex_data[i] for i in indices]
                normal_data[index] = glm.normalize(glm.cross(p2 - p1, p1 - p0))
        return normal_data

    def __repr__(self):
        """String representation of the class

        Returns:
            str: string representation (of the form Mesh<num_vertices, num_faces>)
        """
        return f"Mesh<vertex_data={len(self.vertex_data)}, index_data={len(self.index_data)}>"
