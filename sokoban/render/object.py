from pyglm import glm
import numpy as np

from render.render import render_normal

class Object:
    def __init__(self, render, mesh, model_matrix = glm.mat4()):
        self.render = render
        self.mesh = mesh
        self.model_matrix = model_matrix
        self.inv_tra_m_model = glm.mat4()

        self.computed_vertices = np.zeros((len(mesh.vertex_data), 4), dtype=np.float32)
        self.computed_normals = np.zeros((len(mesh.normal_data), 3), dtype=np.float32)

    def update(self):
        self.inv_tra_m_model = glm.mat3(glm.inverse(glm.transpose(self.model_matrix)))
        for i, vertex in enumerate(self.mesh.vertex_data):
            self.computed_vertices[i] = self.render.render_gl_position(vertex, self.model_matrix)

        for i, normal in enumerate(self.mesh.normal_data):
            self.computed_normals[i] = render_normal(normal, self.inv_tra_m_model)

    def draw(self):
        for i, indices in enumerate(self.mesh.index_data):
            points = [self.computed_vertices[index] for index in indices]
            color = self.mesh.color_data[i]
            normal = self.computed_normals[i]
            fill = self.mesh.fill_data[i]
            outer_border = self.mesh.outer_border_data[i]
            self.render.append_polygon(points, color, normal, fill=fill, border=outer_border)
