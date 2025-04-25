from pyglm import glm
import pyxel

from options import FOV, ASPECT, NEAR, FAR, SENSITIVITY

class Camera:
    """Camera class for frustum rendering"""
    
    def __init__(self, position=(0, 0, 0), pitch=0, yaw=0, roll=0):
        """Class constructor

        Args:
            position (Iterable[float], optional): starting position of the camera in 3D space. Defaults to (0, 0, 0).
            pitch (int, optional): angle of pitch of the camera in degrees. Defaults to 0.
            yaw (int, optional): angle of yaw of the camera in degrees. Defaults to 0.
            roll (int, optional): angle of roll of the camera in degrees. Defaults to 0.
        """
        self.position = glm.vec3(position)
        self.pitch = glm.radians(pitch)
        self.yaw = glm.radians(yaw)
        self.roll = glm.radians(roll)
        self.fov = FOV

        self.frame_count = 0
        self.mouse_x, self.mouse_y = 0, 0

        self.forward = glm.vec3(0, 0, -1)
        self.right = glm.vec3(1, 0, 0)
        self.up = glm.vec3(0, 1, 0)

        self.projection_matrix = glm.perspective(self.fov, ASPECT, NEAR, FAR)
        self.view_matrix = glm.mat4()

    def handle_input(self):
        """Take care of input to move around the camera"""
        dx = dz = dy = 0
        if pyxel.btn(pyxel.KEY_Z):
            dx += 0.1
        if pyxel.btn(pyxel.KEY_S):
            dx -= 0.1
        if pyxel.btn(pyxel.KEY_SPACE):
            dy += 0.1
        if pyxel.btn(pyxel.KEY_CTRL):
            dy -= 0.1
        if pyxel.btn(pyxel.KEY_Q):
            dz += 0.1
        if pyxel.btn(pyxel.KEY_D):
            dz -= 0.1
        if pyxel.btn(pyxel.KEY_A):
            self.roll -= 1 / 30
        if pyxel.btn(pyxel.KEY_E):
            self.roll += 1 / 30

        self.position += self.forward * dx
        self.position += self.up * dy
        self.position += self.right * dz
    
    def handle_mouse_movement(self):
        """Take care of mouse movement for camera viewing (pitch and yaw)"""
        print("pitch/yaw", self.pitch, self.yaw)
        mx, my = pyxel.mouse_x, pyxel.mouse_y
        print("mx/my", mx, my)
        dx, dy = mx - self.mouse_x, my - self.mouse_y
        print("dx/dy", dx, dy)
        self.mouse_x, self.mouse_y = mx, my
        
        if self.frame_count < 5:
            self.frame_count += 1
            return

        self.yaw += dx * SENSITIVITY
        self.pitch -= dy * SENSITIVITY

        max_pitch = glm.radians(89.0)
        self.pitch = glm.clamp(self.pitch, - max_pitch, max_pitch)
        print("pitch/yaw", self.pitch, self.yaw)

    def update_matrices(self):
        """Update view matrix and forward, right, and up vectors"""
        direction = glm.vec3(
            glm.cos(self.pitch) * glm.sin(self.yaw),
            glm.sin(self.pitch),
            -glm.cos(self.pitch) * glm.cos(self.yaw)
        )
        self.forward = glm.normalize(direction)

        world_up = glm.vec3(0, 1, 0)
        self.right = glm.normalize(glm.cross(world_up, self.forward))
        self.up = glm.normalize(glm.cross(self.forward, self.right))

        if self.roll != 0:
            roll_matrix = glm.rotate(glm.mat4(1.0), self.roll, self.forward)
            self.right = glm.vec3(roll_matrix * glm.vec4(self.right, 0.0))
            self.up = glm.normalize(glm.cross(self.forward, self.right))

        self.view_matrix = glm.lookAt(self.position, self.position + self.forward, self.up)

    def update(self):
        """Update method for pyxel run loop"""
        self.handle_input()
        self.handle_mouse_movement()
        self.update_matrices()
    
    def __repr__(self):
        return f"Camera<position:{self.position}, yaw:{self.yaw}, pitch:{self.pitch}, roll:{self.roll}>"
