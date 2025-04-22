from vector import normalize, cross

class Mesh:
    def __init__(self, vertex_data, index_data, color_data, normal_data=None):
        self.num_triangles = len(index_data)

        self.vertex_data = tuple(vertex_data)  # (num_vertices, 3)
        self.index_data = tuple(index_data)  # (num_triangles, 3)
        self.color_data = tuple(color_data)  # (num_triangles, )
        if normal_data is None:
            self.normal_data = self.compute_normals()
        else:
            self.normal_data = tuple(normal_data)

    def compute_normals(self):
        normal_data = [None for _ in range(self.num_triangles)]
        for index in range(self.num_triangles):
            p0, p1, p2 = [self.vertex_data[i] for i in self.index_data[index]]
            normal_data[index] = glm.normalize(glm.cross(p2 - p1, p1 - p0))
        return tuple(normal_data)