from pyglm import glm
import numpy as np


class Mesh:
    def __init__(self, vertex_data, index_data, color_data, normal_data = None):
        if normal_data is None:
            normal_data = []
        self.vertex_data = np.array(vertex_data, dtype=np.float32)

        length = len(self.vertex_data)
        if length <= 256:
            index_dtype = np.uint8
        elif length <= 65536:
            index_dtype = np.uint16
        elif length <= 4294967296:
            index_dtype = np.uint32
        else:
            index_dtype = np.uint64

        self.index_data = np.array(index_data, dtype=index_dtype)
        self.color_data = np.array(color_data, dtype=np.uint8)
        self.num_triangles = len(index_data)

        if normal_data is None:
            self.normal_data = self.compute_normals()
        else:
            self.normal_data = np.array(normal_data, dtype=np.float32)

    def compute_normals(self):
        normal_data = np.zeros((self.num_triangles, 3), dtype=np.float32)
        for index in range(self.num_triangles):
            p0, p1, p2 = [self.vertex_data[i] for i in self.index_data[index]]
            normal_data[index] = glm.normalize(glm.cross(p2 - p1, p1 - p0))
        return normal_data
