from object import Object
from pyglm import glm
import pyxel


class Scene:
    def __init__(self, app):
        self.app = app
        self.objects = []
        self.cube = None

    def load_objects(self):
        self.cube = Object(self.app.render, self.app.meshes["cube"])

    def update(self):
        for obj in self.objects:
            obj.update()
        self.cube.update()

    def draw(self):
        for obj in self.objects:
            obj.draw()
        self.cube.draw()