import pyxel
from time import perf_counter

from mesh import Mesh
from camera import Camera
from render import Render
from scene import Scene

from options import W_WIDTH, W_HEIGHT


CUBE_VERTICES = tuple((a, b, c) for a in (-1, 1) for b in (-1, 1) for c in (-1, 1))
CUBE_INDICES = (
    (0, 1, 2), (2, 1, 3), # Bottom face
    (1, 0, 4), (1, 4, 5), # Front face
    (0, 2, 4), (4, 2, 6), # Left face
    (3, 1, 5), (3, 5, 7), # Right face
    (5, 4, 6), (5, 6, 7), # Top face
    (2, 3, 6), (6, 3, 7) # Back face
)
CUBE_COLOR = tuple((i % 15) + 1 for i in range(len(CUBE_INDICES)))


class App:
    def __init__(self):
        pyxel.init(W_WIDTH, W_HEIGHT, fps=60)
        self.camera = Camera()
        self.render = Render(self.camera, cull_face=True, depth_sort=True)
        self.meshes = {}
        self.scene = Scene(self)

        self.current_time = perf_counter()
        self.delta_time = 0
        self.time = 0

    def load(self):
        self.load_meshes()
        self.scene.load_objects()

    def load_meshes(self):
        self.meshes["cube"] = Mesh(CUBE_VERTICES, CUBE_INDICES, CUBE_COLOR)

    def update(self):
        self.camera.update()
        self.scene.update()

    def draw(self):
        pyxel.cls(0)
        self.render.clear()
        self.scene.draw()
        self.render.draw()

        current_time = perf_counter()
        self.delta_time = current_time - self.current_time
        print(f"FPS: {1 / self.delta_time}")

        self.current_time = current_time
        self.time += self.delta_time

    def run(self):
        self.load()
        pyxel.run(self.update, self.draw)

if __name__ == '__main__':
    app = App()
    app.run()