from pyglm import glm
import numpy as np



class Object:
    def __init__(self, render, mesh, model_matrix = glm.mat4()):
        self.render = render
        self.mesh = mesh
        self.model_matrix = model_matrix
        self.inv_tra_m_model = glm.mat4()

        self.computed_vertices = np.zeros((len(mesh.vertex_data), 4), dtype=np.float32)
        self.computed_normals = np.zeros((len(mesh.normal_data), 3), dtype=np.float32)

    def update(self, render):
        self.inv_tra_m_model = glm.mat3(glm.inverse(glm.transpose(self.model_matrix)))
        for i, vertex in enumerate(self.mesh.vertex_data):
            self.computed_vertices[i] = np.array(render.render_gl_position(vertex, self.model_matrix), dtype=np.float32)

        # for i, normal in enumerate(self.mesh.normal_data):
        #     self.computed_normals[i] = render.render_normal(normal, self.inv_tra_m_model)

    def draw(self):
        for i, indices in enumerate(self.mesh.index_data):
            triangle = [self.computed_vertices[index] for index in indices]
            normal = self.computed_normals[i]
            color = self.mesh.color_data[i]
            self.render.append_triangle(triangle, normal, color)