import math
import operator
from typing import Iterable

class Vec2:
    def __init__(self, *args):
        if len(args) == 2:
            self.x, self.y = args
        elif len(args) == 1:
            arg = args[0]
            if any(isinstance(arg, arg_type) for arg_type in (tuple, list)) and len(arg) == 2:
                self.x, self.y = arg
            else:
                raise ValueError("Single argument must be a 2-tuple or a 2-array")
        else:
            raise TypeError(f"Invalid arguments for Vec2 initialization: {args}")


    def __eq__(self, other): return isinstance(other, Vec3) and self.x == other.x and self.y == other.y
    def __ne__(self, other): return not self == other

    def __repr__(self):
        return f"Vec2<{self.x}, {self.y}>"

class Vec3:
    __slots__ = ('x', 'y', 'z')

    def __init__(self, *args):
        if len(args) == 1:
            arg = args[0]
            if isinstance(arg, Vec3):
                self.x, self.y, self.z = arg.x, arg.y, arg.z
            elif isinstance(arg, (tuple, list)) and len(arg) == 3:
                self.x, self.y, self.z = arg
            elif hasattr(arg, "__getitem__"):
                self.x, self.y, self.z = arg[0], arg[1], arg[2]
            else:
                raise TypeError("Expected Vec3 or tuple/list of 3 elements")
        elif len(args) == 2 and hasattr(args[0], "__getitem__"):
            self.x, self.y = args[0][0], args[0][1]
            self.z = args[1]
        elif len(args) == 3:
            self.x, self.y, self.z = args
        else:
            raise TypeError("Invalid arguments for Vec3 initialization")

    def __repr__(self):
        return f"Vec3<{self.x}, {self.y}, {self.z}>"

    # Item access and iteration
    def __getitem__(self, i):
        if i == 0: return self.x
        elif i == 1: return self.y
        elif i == 2: return self.z
        raise IndexError("Index out of range")

    def __setitem__(self, i, value):
        if i == 0: self.x = value
        elif i == 1: self.y = value
        elif i == 2: self.z = value
        else: raise IndexError("Index out of range")

    def __iter__(self):
        yield self.x
        yield self.y
        yield self.z

    # Internal helper for binary operations
    def _op(self, other, func):
        if isinstance(other, Vec3):
            return Vec3(func(self.x, other.x), func(self.y, other.y), func(self.z, other.z))
        elif isinstance(other, (tuple, list)) and len(other) == 3:
            return Vec3(func(self.x, other[0]), func(self.y, other[1]), func(self.z, other[2]))
        elif isinstance(other, (int, float)):
            return Vec3(func(self.x, other), func(self.y, other), func(self.z, other))
        raise TypeError("Unsupported operand")

    def __add__(self, other): return self._op(other, operator.add)
    def __sub__(self, other): return self._op(other, operator.sub)
    def __mul__(self, other): return self._op(other, operator.mul)
    def __truediv__(self, other): return self._op(other, operator.truediv)
    def __floordiv__(self, other): return self._op(other, operator.floordiv)
    def __mod__(self, other): return self._op(other, operator.mod)
    def __pow__(self, other): return self._op(other, operator.pow)

    def __radd__(self, other): return self + other
    def __rsub__(self, other): return -self + other
    def __rmul__(self, other): return self * other
    def __rtruediv__(self, other):
        if isinstance(other, (int, float)):
            return Vec3(other / self.x, other / self.y, other / self.z)
        raise TypeError("Unsupported reverse division")

    def __neg__(self): return Vec3(-self.x, -self.y, -self.z)
    def __eq__(self, other): return isinstance(other, Vec3) and self.x == other.x and self.y == other.y and self.z == other.z
    def __ne__(self, other): return not self == other

    def sum(self):
        return self.x + self.y + self.z

    # Vector operations
    def dot(self, other):
        return self.__mul__(other).sum()

    def cross(self, other):
        return Vec3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )

    def norm(self):
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)

    def normalize(self):
        n = self.norm()
        if n == 0:
            raise ZeroDivisionError("Cannot normalize zero vector")
        return self / n

    def distance(self, other):
        return math.sqrt(
            (self.x - other.x)**2 +
            (self.y - other.y)**2 +
            (self.z - other.z)**2
        )

    # Swizzling (read-only)
    @property
    def xy(self): return Vec2(self.x, self.y)
    @property
    def yz(self): return Vec2(self.y, self.z)
    @property
    def zx(self): return Vec2(self.z, self.x)
    @property
    def yx(self): return Vec2(self.y, self.x)
    @property
    def zy(self): return Vec2(self.z, self.y)
    @property
    def xz(self): return Vec2(self.x, self.z)

    @property
    def xxy(self): return Vec3(self.x, self.x, self.y)
    @property
    def xyz(self): return Vec3(self.x, self.y, self.z)
    @property
    def xzx(self): return Vec3(self.x, self.z, self.x)
    @property
    def xyx(self): return Vec3(self.x, self.y, self.x)
    @property
    def xzy(self): return Vec3(self.x, self.z, self.y)
    @property
    def xxz(self): return Vec3(self.x, self.x, self.z)

    @property
    def yxy(self): return Vec3(self.y, self.x, self.y)
    @property
    def yyz(self): return Vec3(self.y, self.y, self.z)
    @property
    def yzx(self): return Vec3(self.y, self.z, self.x)
    @property
    def yyx(self): return Vec3(self.y, self.y, self.x)
    @property
    def yzy(self): return Vec3(self.y, self.z, self.y)
    @property
    def yxz(self): return Vec3(self.y, self.x, self.z)

    @property
    def zxy(self): return Vec3(self.z, self.x, self.y)
    @property
    def zyz(self): return Vec3(self.z, self.y, self.z)
    @property
    def zzx(self): return Vec3(self.z, self.z, self.x)
    @property
    def zyx(self): return Vec3(self.z, self.y, self.x)
    @property
    def zzy(self): return Vec3(self.z, self.z, self.y)
    @property
    def zxz(self): return Vec3(self.z, self.x, self.z)

class Vec4:
    __slots__ = ('x', 'y', 'z', 'w')

    def __init__(self, *args):
        if len(args) == 1:
            arg = args[0]
            if hasattr(arg, "__getitem__") and len(arg) == 4:
                self.x, self.y, self.z, self.w = arg[0], arg[1], arg[2], arg[3]
            else:
                raise TypeError("Expected Vec4 or tuple/list of 4 elements")
        elif len(args) == 2:
            arg = args[0]
            if hasattr(arg, "__getitem__") and len(arg) == 3:
                self.x, self.y, self.z = arg[0], arg[1], arg[2]
            else:
                raise TypeError("Expected Vec3 or tuple/list of 3 elements")
            self.z = args[1]
        elif len(args) == 3:
            arg = args[0]
            if hasattr(arg, "__getitem__") and len(arg) == 2:
                self.x, self.y = arg[0], arg[1]
            else:
                raise TypeError("Expected Vec2 or tuple/list of 2 elements")
            self.z, self.w = args[1], args[2]
        elif len(args):
            self.x, self.y, self.z, self.w = args
        else:
            raise TypeError("Invalid arguments for Vec3 initialization")

    def __repr__(self):
        return f"Vec4<{self.x}, {self.y}, {self.z}, {self.w}>"

    # Item access and iteration
    def __len__(self):
        return 4

    def __getitem__(self, i):
        if i == 0: return self.x
        elif i == 1: return self.y
        elif i == 2: return self.z
        elif i == 3: return self.w
        raise IndexError("Index out of range")

    def __setitem__(self, i, value):
        if i == 0: self.x = value
        elif i == 1: self.y = value
        elif i == 2: self.z = value
        elif i == 3: self.w = value
        else: raise IndexError("Index out of range")

    def __iter__(self):
        yield self.x
        yield self.y
        yield self.z
        yield self.w

    # Internal helper for binary operations
    def _op(self, other, func):
        if isinstance(other, Vec4):
            return Vec4(func(self.x, other.x), func(self.y, other.y), func(self.z, other.z), func(self.w, other.w))
        elif isinstance(other, (tuple, list)) and len(other) == 3:
            return Vec4(func(self.x, other[0]), func(self.y, other[1]), func(self.z, other[2]), func(self.w, other[2]))
        elif isinstance(other, (int, float)):
            return Vec4(func(self.x, other), func(self.y, other), func(self.z, other), func(self.w, other))
        raise TypeError("Unsupported operand")

    def __add__(self, other): return self._op(other, operator.add)
    def __sub__(self, other): return self._op(other, operator.sub)
    def __mul__(self, other): return self._op(other, operator.mul)
    def __truediv__(self, other): return self._op(other, operator.truediv)
    def __floordiv__(self, other): return self._op(other, operator.floordiv)
    def __mod__(self, other): return self._op(other, operator.mod)
    def __pow__(self, other): return self._op(other, operator.pow)

    def __radd__(self, other): return self + other
    def __rsub__(self, other): return -self + other
    def __rmul__(self, other): return self * other
    def __rtruediv__(self, other):
        if isinstance(other, (int, float)):
            return Vec3(other / self.x, other / self.y, other / self.z, other / self.w)
        raise TypeError("Unsupported reverse division")

    def __neg__(self): return Vec3(-self.x, -self.y, -self.z, -self.w)
    def __eq__(self, other): return isinstance(other, Vec3) and self.x == other.x and self.y == other.y and self.z == other.z and self.w == other.w
    def __ne__(self, other): return not self == other

    def sum(self):
        return self.x + self.y + self.z + self.w

    # Vector operations
    def dot(self, other):
        return self.__mul__(other).sum()

    def cross(self, other):
        return Vec3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )

    def norm(self):
        return math.sqrt(self.x**2 + self.y**2 + self.z**2 + self.w**2)

    def normalize(self):
        n = self.norm()
        if n == 0:
            raise ZeroDivisionError("Cannot normalize zero vector")
        return self / n

    def distance(self, other):
        return math.sqrt(
            (self.x - other.x)**2 +
            (self.y - other.y)**2 +
            (self.z - other.z)**2 +
            (self.w - other.w)**2
        )

    # Swizzling (read-only)
    @property
    def xy(self): return Vec2(self.x, self.y)
    @property
    def yz(self): return Vec2(self.y, self.z)
    @property
    def zx(self): return Vec2(self.z, self.x)
    @property
    def yx(self): return Vec2(self.y, self.x)
    @property
    def zy(self): return Vec2(self.z, self.y)
    @property
    def xz(self): return Vec2(self.x, self.z)

    @property
    def xxy(self): return Vec3(self.x, self.x, self.y)
    @property
    def xyz(self): return Vec3(self.x, self.y, self.z)
    @property
    def xzx(self): return Vec3(self.x, self.z, self.x)
    @property
    def xyx(self): return Vec3(self.x, self.y, self.x)
    @property
    def xzy(self): return Vec3(self.x, self.z, self.y)
    @property
    def xxz(self): return Vec3(self.x, self.x, self.z)

    @property
    def yxy(self): return Vec3(self.y, self.x, self.y)
    @property
    def yyz(self): return Vec3(self.y, self.y, self.z)
    @property
    def yzx(self): return Vec3(self.y, self.z, self.x)
    @property
    def yyx(self): return Vec3(self.y, self.y, self.x)
    @property
    def yzy(self): return Vec3(self.y, self.z, self.y)
    @property
    def yxz(self): return Vec3(self.y, self.x, self.z)

    @property
    def zxy(self): return Vec3(self.z, self.x, self.y)
    @property
    def zyz(self): return Vec3(self.z, self.y, self.z)
    @property
    def zzx(self): return Vec3(self.z, self.z, self.x)
    @property
    def zyx(self): return Vec3(self.z, self.y, self.x)
    @property
    def zzy(self): return Vec3(self.z, self.z, self.y)
    @property
    def zxz(self): return Vec3(self.z, self.x, self.z)

class Mat4:
    def __init__(self, data=None):
        if data is None:
            # Identity matrix
            self.data = [[1 if i == j else 0 for j in range(4)] for i in range(4)]
        elif isinstance(data, Iterable):
            flat = list(data)
            if len(flat) == 16:
                # Flat list
                self.data = [flat[i*4:(i+1)*4] for i in range(4)]
            elif all(isinstance(row, Iterable) and len(row) == 4 for row in data) and len(data) == 4:
                # 4x4 nested list
                self.data = [list(row) for row in data]
            else:
                raise ValueError("Mat4 must be initialized with 16 values or 4x4 iterable.")
        else:
            raise TypeError("Unsupported type for Mat4 initialization.")

    def __repr__(self):
        return '\n'.join(['[' + ' '.join(f"{val: .2f}" for val in row) + ']' for row in self.data])

    def copy(self):
        return Mat4([row[:] for row in self.data])

    def __getitem__(self, index):
        return self.data[index]

    def __setitem__(self, index, value):
        self.data[index] = list(value)

    def __mul__(self, other):
        if isinstance(other, Mat4):
            # Matrix multiplication
            result = Mat4([[0]*4 for _ in range(4)])
            for i in range(4):
                for j in range(4):
                    result[i][j] = sum(self.data[i][k] * other[k][j] for k in range(4))
            return result
        elif isinstance(other, (list, tuple)):
            if len(other) == 4:
                return [
                    sum(self.data[i][j] * other[j] for j in range(4))
                    for i in range(4)
                ]
            raise ValueError("Can only multiply Mat4 with 4D vector")
        elif isinstance(other, (int, float)):
            return Mat4([[val * other for val in row] for row in self.data])
        else:
            return NotImplemented

    def __rmul__(self, other):
        if isinstance(other, (int, float)):
            return self * other
        return NotImplemented

    def __eq__(self, other):
        if not isinstance(other, Mat4): return False
        return all(math.isclose(self[i][j], other[i][j], rel_tol=1e-9) for i in range(4) for j in range(4))

    def transpose(self):
        return Mat4([[self.data[j][i] for j in range(4)] for i in range(4)])

    def inverse(self):
        # Inversion using Gauss-Jordan elimination on a 4x4 matrix
        m = [row[:] for row in self.data]
        inv = [[1 if i == j else 0 for j in range(4)] for i in range(4)]

        for i in range(4):
            # Find the pivot
            pivot = m[i][i]
            if abs(pivot) < 1e-10:
                raise ValueError("Matrix is not invertible")
            inv_row = [val / pivot for val in inv[i]]
            m_row = [val / pivot for val in m[i]]
            inv[i] = inv_row
            m[i] = m_row

            for j in range(4):
                if i != j:
                    factor = m[j][i]
                    m[j] = [a - factor * b for a, b in zip(m[j], m[i])]
                    inv[j] = [a - factor * b for a, b in zip(inv[j], inv[i])]

        return Mat4(inv)

    @staticmethod
    def identity():
        return Mat4()

    @staticmethod
    def translation(x, y, z):
        m = Mat4.identity()
        m[0][3] = x
        m[1][3] = y
        m[2][3] = z
        return m

    @staticmethod
    def scale(sx, sy, sz):
        m = Mat4()
        m[0][0] = sx
        m[1][1] = sy
        m[2][2] = sz
        return m

    @staticmethod
    def rotation_x(angle_rad):
        c, s = math.cos(angle_rad), math.sin(angle_rad)
        m = Mat4.identity()
        m[1][1], m[1][2] = c, -s
        m[2][1], m[2][2] = s, c
        return m

    @staticmethod
    def rotation_y(angle_rad):
        c, s = math.cos(angle_rad), math.sin(angle_rad)
        m = Mat4.identity()
        m[0][0], m[0][2] = c, s
        m[2][0], m[2][2] = -s, c
        return m

    @staticmethod
    def rotation_z(angle_rad):
        c, s = math.cos(angle_rad), math.sin(angle_rad)
        m = Mat4.identity()
        m[0][0], m[0][1] = c, -s
        m[1][0], m[1][1] = s, c
        return m

    @staticmethod
    def perspective(fov, aspect, near, far):
        f = 1.0 / math.tan(fov / 2)
        nf = 1 / (near - far)
        return Mat4([
            [f / aspect, 0, 0, 0],
            [0, f, 0, 0],
            [0, 0, (far + near) * nf, 2 * far * near * nf],
            [0, 0, -1, 0]
        ])

    @staticmethod
    def rotate(axis, angle):
        x, y, z = axis.normalize()
        c = math.cos(angle)
        s = math.sin(angle)
        t = 1 - c
        return Mat4([
            [t*x*x + c,   t*x*y - s*z, t*x*z + s*y, 0],
            [t*x*y + s*z, t*y*y + c,   t*y*z - s*x, 0],
            [t*x*z - s*y, t*y*z + s*x, t*z*z + c,   0],
            [0, 0, 0, 1]
        ])

    @staticmethod
    def translate(v):
        m = Mat4.identity()
        m[0][3], m[1][3], m[2][3] = v[0], v[1], v[2]
        return m

    @staticmethod
    def look_at(eye, center, up):
        # 'self' is the camera position (Vec3)
        f = (center - eye).normalize()
        s = f.cross(up.normalize()).normalize()
        u = s.cross(f)

        rot = Mat4([
            [s[0], u[0], -f[0], 0],
            [s[1], u[1], -f[1], 0],
            [s[2], u[2], -f[2], 0],
            [0,    0,    0,     1]
        ])
        trans = Mat4.translate(-eye)
        return rot * trans



if __name__ == "__main__":
    print("Running Vec3 tests...")

    v1 = Vec3(1, 2, 3)
    v2 = Vec3((4, 5), 6)
    v3 = Vec3([7, 8, 9])
    v4 = Vec3(v3)

    # Init checks
    assert v1.x == 1 and v1.y == 2 and v1.z == 3
    assert v2 == Vec3(4, 5, 6)
    assert v3 == Vec3(7, 8, 9)
    assert v4 == v3
    assert not v3 is v4

    # Addition and subtraction
    assert (v1 + v2) == Vec3(5, 7, 9)
    assert (v3 - v1) == Vec3(6, 6, 6)
    assert (v1 + [1, 1, 1]) == Vec3(2, 3, 4)
    assert (v1 + 1) == Vec3(2, 3, 4)
    assert (v1 + v2) == Vec3(5, 7, 9)
    assert ([1, 1, 1] - v1) == Vec3(0, -1, -2)
    assert (2 + v3) == Vec3(9, 10, 11)

    # Scalar multiplication and division
    assert (v1 * 2) == Vec3(2, 4, 6)
    assert (v1 / 2) == Vec3(0.5, 1.0, 1.5)
    assert (2 * v1) == Vec3(2, 4, 6)

    # Reverse operations
    assert (10 / Vec3(1, 2, 5)) == Vec3(10, 5, 2)

    # Unary and equality
    assert (-v1) == Vec3(-1, -2, -3)
    assert (v1 == Vec3(1, 2, 3))
    assert (v1 != v2)

    # Dot and cross
    assert v1.dot(v2) == 1*4 + 2*5 + 3*6  # 32
    assert v1.cross(v2) == Vec3(-3, 6, -3)

    # Norm and normalize
    assert round(v1.norm(), 5) == round(math.sqrt(14), 5)
    vnorm = v1.normalize()
    assert round(vnorm.norm(), 5) == 1.0

    # Distance
    assert round(v1.distance(v2), 5) == round(math.sqrt(27), 5)

    # Indexing and setting
    assert v1[0] == 1 and v1[1] == 2 and v1[2] == 3
    v1[0] = 9
    assert v1[0] == 9
    try:
        a = v1[3]
        assert False, "IndexError expected"
    except IndexError:
        pass

    # Iteration
    values = list(Vec3(1, 2, 3))
    assert values == [1, 2, 3]

    # Swizzling
    """
    assert Vec3(1, 2, 3).xy == Vec2(1, 2)
    assert Vec3(1, 2, 3).yz == Vec2(2, 3)
    assert Vec3(1, 2, 3).zx == Vec2(3, 1)
    """

    print("✅ All Vec3 tests passed.")

    print("Testing Mat4...")

    # Identity
    m1 = Mat4()
    assert m1 == Mat4.identity()

    # From flat list
    flat = [i for i in range(16)]
    m2 = Mat4(flat)
    assert m2[0][0] == 0 and m2[3][3] == 15

    # Matrix multiplication (identity * m2 = m2)
    assert m1 * m2 == m2

    # Vector multiplication
    vec4 = [1, 2, 3, 1]
    out = m1 * vec4
    assert out == [1, 2, 3, 1]

    # Transpose
    mt = m2.transpose()
    for i in range(4):
        for j in range(4):
            assert mt[i][j] == m2[j][i]

    # Scale and translation
    ms = Mat4.scale(2, 3, 4)
    assert ms[0][0] == 2 and ms[1][1] == 3 and ms[2][2] == 4

    mt = Mat4.translation(5, 6, 7)
    assert mt[0][3] == 5 and mt[1][3] == 6 and mt[2][3] == 7

    # Rotation test (simple rotation around Z by 90 degrees)
    rz = Mat4.rotation_z(math.pi / 2)
    vec = [1, 0, 0, 1]
    result = rz * vec
    assert math.isclose(result[0], 0, abs_tol=1e-5)
    assert math.isclose(result[1], 1, abs_tol=1e-5)

    print("✅ All Mat4 tests passed.")
