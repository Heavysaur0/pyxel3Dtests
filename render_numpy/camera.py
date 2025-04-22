from pyglm import glm
import pyxel

from options import FOV, ASPECT, NEAR, FAR


class Camera:
    def __init__(self, position = (0, 0, -5), pitch = 0, yaw = 0, roll = 0):
        self.position = glm.vec3(position)
        self.fov = FOV

        self.pitch = pitch
        self.yaw = yaw
        self.roll = roll

        self.right = glm.vec3(1, 0, 0)
        self.up = glm.vec3(0, 1, 0)
        self.forward = glm.vec3(0, 0, -1)

        self.mouse_x, self.mouse_y = 0, 0

        self.projection_matrix = glm.mat4()
        self.view_matrix = glm.mat4()

    def handle_input(self):
        dx = dz = dy = 0
        if pyxel.btn(pyxel.KEY_Q):
            dz += 0.01
        if pyxel.btn(pyxel.KEY_D):
            dz -= 0.01
        if pyxel.btn(pyxel.KEY_Z):
            dx += 0.01
        if pyxel.btn(pyxel.KEY_S):
            dx -= 0.01
        if pyxel.btn(pyxel.KEY_SPACE):
            dy += 0.01
        if pyxel.btn(pyxel.KEY_CTRL):
            dy -= 0.01
        if pyxel.btn(pyxel.KEY_A):
            self.roll -= 1 / 60
        if pyxel.btn(pyxel.KEY_E):
            self.roll += 1 / 60

        self.position += self.forward * dx
        self.position += self.right * dz
        self.position += self.up * dy

    def handle_mouse_movement(self):
        mx, my = pyxel.mouse_x, pyxel.mouse_y
        dx, dy = self.mouse_x - mx, self.mouse_y - my
        self.pitch += dx
        self.yaw += dy
        self.mouse_x, self.mouse_y = mx, my

    def update_matrices(self):
        rotation = glm.rotate(glm.mat4(), self.pitch, glm.vec3(1, 0, 0))
        rotation = glm.rotate(rotation, self.yaw, glm.vec3(0, 1, 0))
        rotation = glm.rotate(rotation, self.roll, glm.vec3(0, 0, -1))

        self.right = glm.vec3(rotation * glm.vec4(1, 0, 0, 1.0))
        self.up = glm.vec3(rotation * glm.vec4(0, 1, 0, 1.0))
        self.forward = glm.vec3(rotation * glm.vec4(0, 0, -1, 1.0))

        translation = glm.translate(self.position)
        self.view_matrix = rotation * translation

        self.projection_matrix = glm.perspective(self.fov, ASPECT, NEAR, FAR)

    def update(self):
        self.handle_input()
        self.update_matrices()
