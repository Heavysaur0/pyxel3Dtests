import pyxel
from time import perf_counter

from mesh import Mesh
from camera import Camera
from render import Render
from scene import Scene

from options import W_WIDTH, W_HEIGHT


CUBE_VERTICES = tuple((a, b, c) for a in (-1, 1) for b in (-1, 1) for c in (-1, 1))
CUBE_INDICES = (
    (1, 3, 2, 0), # Front face
    (0, 2, 6, 4), # Left face
    (4, 6, 7, 5), # Back face
    (5, 7, 3, 1), # Right face
    (3, 7, 6, 2), # Top face
    (5, 1, 0, 4), # Bottom face
)
CUBE_COLOR = tuple((i % 15) + 1 for i in range(len(CUBE_INDICES)))


class App:
    def __init__(self, profiler = None):
        self.profiler = profiler
        
        pyxel.init(W_WIDTH, W_HEIGHT, fps=60)
        self.camera = Camera((1.4, 3.9, -7.2), -31, 190)
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
        
        if pyxel.btnp(pyxel.KEY_P) and self.profiler is not None:
            self.profiler.stop()
            print(self.profiler.output_text(unicode=True, color=True))
            sys.exit()

    def draw(self):
        pyxel.cls(0)
        self.render.clear()
        self.scene.draw()
        self.render.draw()

        current_time = perf_counter()
        self.delta_time = current_time - self.current_time
        print(f"Pyxel frame count: {pyxel.frame_count}")
        print(self.camera)
        print(f"  Num of vertices: {self.render.num_vertices}\n"
              f"  Number of triangles: {self.render.num_triangles}\n"
              f"FPS: {1 / self.delta_time:.3f}\n")

        self.current_time = current_time
        self.time += self.delta_time

    def run(self):
        self.load()
        pyxel.run(self.update, self.draw)

if __name__ == '__main__':
    import sys
    from pyinstrument import Profiler

    profiler = Profiler(async_mode='enabled')
    profiler.start()
    
    app = App(profiler)
    app.run()