import numpy as np
import math
import time
import pyxel

from perlin_noise import PerlinNoise


CHUNK_SIZE = 16
LG2_CS = math.floor(math.log2(CHUNK_SIZE))
NP_UINT_TYPE = [t for t in (np.uint8, np.uint16, np.uint32, np.uint64)
                if CHUNK_SIZE ** 2 < np.iinfo(t).max][-1]

SIDE_LENGTH = 2
SCALE = 256 / SIDE_LENGTH



class CubicSpline:
    def __init__(self, x, y):
        x = np.asarray(x, dtype=float)
        y = np.asarray(y, dtype=float)
        self.x = x
        self.y = y
        self.n = len(x) - 1
        self.h = x[1:] - x[:-1]
        self.a = y.copy()

        # Step 1: Solve for c using tridiagonal system
        alpha = np.zeros(self.n + 1)
        alpha[1:self.n] = 3 * ((y[2:] - y[1:-1]) / self.h[1:] - (y[1:-1] - y[:-2]) / self.h[:-1])

        l = np.ones(self.n + 1)
        mu = np.zeros(self.n + 1)
        z = np.zeros(self.n + 1)

        for i in range(1, self.n):
            l[i] = 2 * (x[i + 1] - x[i - 1]) - self.h[i - 1] * mu[i - 1]
            mu[i] = self.h[i] / l[i]
            z[i] = (alpha[i] - self.h[i - 1] * z[i - 1]) / l[i]

        self.c = np.zeros(self.n + 1)
        self.b = np.zeros(self.n)
        self.d = np.zeros(self.n)

        for j in range(self.n - 1, -1, -1):
            self.c[j] = z[j] - mu[j] * self.c[j + 1]
            self.b[j] = ((y[j + 1] - y[j]) / self.h[j]) - self.h[j] * (self.c[j + 1] + 2 * self.c[j]) / 3
            self.d[j] = (self.c[j + 1] - self.c[j]) / (3 * self.h[j])

    def evaluate(self, x_val):
        x_val = np.asarray(x_val, dtype=float)
        # Allocate result array
        result = np.empty_like(x_val)

        # Vectorized search for intervals
        indices = np.searchsorted(self.x, x_val) - 1
        indices = np.clip(indices, 0, self.n - 1)
        dx = x_val - self.x[indices]

        result = (
            self.a[indices] +
            self.b[indices] * dx +
            self.c[indices] * dx ** 2 +
            self.d[indices] * dx ** 3
        )
        return result

BIOME_POINTS = {
    # à chaque fois on met tous les points avec valeur x entre 0 et 1 triés avec leur valeur de hauteur respective,
    # Pour les valeurs entre les points on fait un mélange
    "plain": ((0.0, -0.3), (0.43, 0.0), (0.45, 0.05), (0.67, 0.1), (0.76, 0.2), (0.84, 0.67), (0.94, 0.82), (1.0, 1.0)), # plat
    "plateau": ((0.0, -0.3), (0.4, 0.0), (0.45, 0.18), (0.51, 0.19), (0.6, 0.26), (0.9, 0.88), (1.0, 1.0)), # plat avec falaise aux côtes
    "desert_dune":
    ((0.0, -0.2), (0.083, 0.0), (0.084, 0.065), (0.088, 0.085), (0.11, 0.11), (0.16, 0.09), (0.17, 0.07), (0.25, 0.11),
    (0.3, 0.1),  # Wiggle around 0.1
    (0.36, 0.125), (0.39, 0.165), (0.41, 0.13), (0.43, 0.145), (0.46, 0.17), (0.49, 0.18), (0.53, 0.17),
    # Wiggle around 0.15
    (0.55, 0.225), (0.58, 0.18), (0.61, 0.185), (0.65, 0.22), (0.67, 0.24),  # Wiggle around 0.2
    (0.8, 0.3), (0.85, 0.6), (1.0, 1.0)),  # désert de dunes
    "desert_rock": ((0.0, -0.3), (0.4, 0.0), (0.53, 0.11), (0.66, 0.22), (0.8, 0.98), (1.0, 1.0)),
    # plats avec grands rochers rouges
    "snowy": ((0.0, -0.3), (0.43, 0.0), (0.45, 0.05), (0.67, 0.1), (0.76, 0.2), (0.84, 0.47), (0.9, 0.62), (0.98, 0.9),
              (1.0, 1.0)),  # plat enneigé
    "tundra": ((0.0, -0.3), (0.4, 0.0), (0.45, 0.18), (0.51, 0.19), (0.6, 0.26), (0.9, 0.88), (1.0, 1.0)),
    # plat avec falaise aux côtes enneigé
    "archipel": (
    (0.0, -0.4), (0.55, 0.0), (0.58, 0.05), (0.7, 0.14), (0.75, 0.25), (0.84, 0.4), (0.89, 0.68), (0.92, 0.83),
    (1.0, 1.0)),  # îles
    "glaciers": ((0.0, -0.4), (0.5, 0.0), (0.53, 0.14), (0.57, 0.14), (0.6, 0.0), (0.64, -0.1),  # first row glaciers
                 (0.68, 0.0), (0.69, 0.15), (0.74, 0.16), (0.75, 0.25), (0.84, 0.4), (0.89, 0.68), (0.92, 0.83),
                 (1.0, 1.0)),  # océan gelé
    "volcanos": (
    (0.0, -0.3), (0.38, 0.0), (0.4, 0.09), (0.45, 0.19), (0.46, 0.15), (0.62, 0.18), (0.66, 0.22), (0.75, 0.8),
    (0.82, 1.0), (0.86, 0.65), (1.0, 0.62)),  # terre volcanique
}

BIOME_COLORS = {
    "archipel": [1, 2, 3, 4, 5, 8, 9],  # Peak
}

BIOME_HEIGHTS_LIMIT = {
    "plain": [0.46, 0.65, 0.71, 0.74, 0.76, 0.79, 0.85],
    "plateau": [0.4, 0.475, 0.54, 0.63, 0.69, 0.74, 0.8],
    "desert_dune": [0.16, 0.5, 0.71, 0.75, 0.8, 0.9, 0.95],
    "desert_rock": [0.43, 0.5, 0.7, 0.73, 0.75, 0.8, 0.95],
    "snowy": [0.48, 0.6, 0.76, 0.79, 0.81, 0.84, 0.93],
    "tundra": [0.45, 0.525, 0.59, 0.68, 0.74, 0.79, 0.89],
    "archipel": [0.6, 0.7, 0.76, 0.81, 0.85, 0.9],
    "glaciers": [0.76, 0.78, 0.81, 0.85, 0.9],
    "volcanos": [0.41, 0.6, 0.75, 0.83, 0.88, 0.92],
}

class SplineHeightParams:
    """Class for height parameters with spline calculation (smoothness)"""

    __slots__ = ['num_points', 'x_values', 'y_values', 'spline']

    def __init__(self, biome: str, scale: float = 1.0) -> None:
        """Class constructor

        Args:
            biome (str): biome name for the heights
            scale (float, optional): height scale factor. Defaults to 1.0.
        """
        points = BIOME_POINTS[biome]
        self.num_points = len(points)

        # Precompute values for smooth interpolation
        self.x_values = np.array([p[0] for p in points])  # For binary search
        self.y_values = np.array([p[1] * scale for p in points])  # Y-values for interpolation

        # Use Cubic Spline for smooth interpolation
        self.spline = CubicSpline(self.x_values, self.y_values)

    def height_from_noise(self, noise_value: float | np.ndarray) -> float | np.ndarray:
        """Height calculation for a given Perlin noise

        Args:
            noise_value (float | np.ndarray): Perlin noise value(s)

        Returns:
            float | np.ndarray: height(s) associated with noise value
        """
        return self.spline.evaluate(noise_value)


class ColorParams:
    """Class for color parameters"""

    __slots__ = ['heights_limit', 'colors']

    def __init__(self, biome: str) -> None:
        """Class constructor

        Args:
            biome (str): biome name for color parameters"""
        self.heights_limit = np.asarray(BIOME_HEIGHTS_LIMIT[biome], dtype=float)
        self.colors = np.asarray(BIOME_COLORS[biome], dtype=int)

    def get_id_from_noise(self, noise_value: float | np.ndarray):
        """Give the id(s) of a point for Perlin noise value(s)

        Args:
            noise_value (float | np.ndarray): Perlin noise value(s)

        Returns:
            int | np.ndarray: id(s) of the point(s)
        """
        noise_value = np.asarray(noise_value)
        ids = np.sum(noise_value[..., None] > self.heights_limit, axis=-1)
        return np.clip(ids, 0, len(self.colors) - 1)

    def get_color_from_id(self, id: int | np.ndarray):
        """Give the color(s) for id(s)

        Args:
            id (int | np.ndarray): input id(s)

        Returns:
            tuple[int, int, int] | np.ndarray: color(s) associated with id(s)
        """
        id = np.asarray(id)
        return self.colors[id]


class PerlinGenerator:
    """Perlin noise generation class"""

    __slots__ = ['noise', 'seed', 'scale', 'octaves', 'persistence', 'lacunarity']

    def __init__(self, seed: int = 0, scale: float = 1.0, octaves: int = 1,
                 persistence: float = 0.5, lacunarity: float = 2.0):
        """Class constructor

        Args:
            seed (int, optional): Perlin seed. Defaults to 0.
            scale (float, optional): inital frequence of Perlin noise. Defaults to 1.0.
            octaves (int, optional): number of fractal octaves. Defaults to 1.
            persistence (float, optional): weight of each octave. Defaults to 0.5.
            lacunarity (float, optional): weight of frequence of each octave. Defaults to 2.0.
        """
        self.noise = PerlinNoise(seed)
        self.seed = seed
        self.scale = scale
        self.octaves = octaves
        self.persistence = persistence
        self.lacunarity = lacunarity

    def noise_value(self, x: float | np.ndarray, y: float | np.ndarray) -> float | np.ndarray:
        """Return the Perlin noise value for a point in 2d

        Args:
            x (float | np.ndarray): x-axis coordinate(s)
            y (float | np.ndarray): y-axis coordinate(s)

        Returns:
            float | np.ndarray: Perlin noise value(s)
        """
        # Accept scalars or numpy arrays
        x = np.asarray(x, dtype=np.float32)
        y = np.asarray(y, dtype=np.float32)

        noise_value = self.noise.noise(
            x / self.scale, y / self.scale,
            octaves=self.octaves,
            persistence=self.persistence,
            lacunarity=self.lacunarity
        )

        return np.clip(noise_value, 0, 1)  # Ensure within [0,1]

    def noise_value_override(self, x: float, y: float, **overrides) -> float:
        """Return the Perlin noise value for a point in 2d

        Args:
            x (float): x-axis coordinate
            y (float): y-axis coordinate
            **overrides (Any): the kwargs to override the class attributes

        Returns:
            float: Perlin noise value
        """
        # Use provided overrides or fall back to the object's default attributes
        params = {
            "octaves": self.octaves,
            "persistence": self.persistence,
            "lacunarity": self.lacunarity,
            "scale": self.scale
        }
        params.update(overrides)  # Override defaults with any specified values

        noise_value = self.noise.noise(
            x / params["scale"], y / params["scale"],
            octaves=params["octaves"],
            persistence=params["persistence"],
            lacunarity=params["lacunarity"]
        )

        return np.clip(noise_value, 0, 1)  # Ensure within [0,1]

class SoloChunkMesh:
    def __init__(self, perlin_generator: PerlinGenerator,
                 height_params: SplineHeightParams, color_params: ColorParams,
                 x_chunk: int, y_chunk: int, scale: float = 1.0):
        print("Generating mesh...")
        self.coord = np.array([x_chunk, y_chunk], dtype=np.int32)
        self.scale = scale

        xs, ys = np.meshgrid(np.linspace(0, 1, CHUNK_SIZE + 1),
                             np.linspace(0, 1, CHUNK_SIZE + 1))
        start_time = time.perf_counter()
        self.noise_data = perlin_generator.noise_value(xs, ys).reshape(-1)
        vertex_time = time.perf_counter()
        print(f"  * Perlin values: {vertex_time - start_time:.6f}s")


        self.height_data = np.array(height_params.height_from_noise(self.noise_data), dtype=np.float32)
        height_time = time.perf_counter()
        print(f"  * Height values: {height_time - vertex_time:.6f}s")

        self.color_data = np.array(color_params.get_id_from_noise(self.noise_data), dtype=np.uint8)
        color_time = time.perf_counter()
        print(f"  * Colors data: {color_time - height_time:.6f}s")

        self.vertex_data = np.zeros(((CHUNK_SIZE + 1) ** 2, 3), dtype=np.float32)
        np_dtype = [t for t in (np.uint8, np.uint16, np.uint32, np.uint64)
                    if len(self.noise_data) < np.iinfo(t).max][-1]
        num_triangles = 2 * (CHUNK_SIZE ** 2)
        self.triangles = np.zeros((num_triangles, 3), dtype=np_dtype)
        self.colors = np.zeros((num_triangles, ), dtype=np.uint8)

        start_time = time.perf_counter()
        self.generate_data(color_params)
        end_time = time.perf_counter()
        print(f"  * Vertex, triangles and colors: {end_time - start_time:.6f}s")

        del self.noise_data
        del self.height_data
        del self.color_data

    def generate_data(self, color_params: ColorParams):
        offset = np.linspace(0, 1, CHUNK_SIZE + 1)
        for y in range(CHUNK_SIZE + 1):
            for x in range(CHUNK_SIZE + 1):
                index = y * (CHUNK_SIZE + 1) + x
                self.vertex_data[index] = [offset[x], self.height_data[index], offset[y]]

                if x < CHUNK_SIZE and y < CHUNK_SIZE:
                    triangle_index = y * CHUNK_SIZE + x

                    # Odd vs Pair triangles
                    if (x & 1) ^ (y & 1):
                        self.triangles[2 * triangle_index] = (index, index + 1, index + CHUNK_SIZE)
                        self.triangles[2 * triangle_index + 1] = (index + CHUNK_SIZE, index + 1, index + CHUNK_SIZE + 1)
                    else:
                        self.triangles[2 * triangle_index] = (index, index + CHUNK_SIZE + 1, index + CHUNK_SIZE)
                        self.triangles[2 * triangle_index + 1] = (index + CHUNK_SIZE + 1, index, index + 1)

        for index, triangle in enumerate(self.triangles):
            self.colors[index] = color_params.get_color_from_id(max([self.color_data[i] for i in triangle]))

    def get_byte_size(self):
        return sum(ele.nbytes for ele in (self.vertex_data, self.triangles, self.colors))

    def __repr__(self):
        return f"SoloChunkMesh<{self.coord}>"

# Function to format the size
def format_size(size_bytes):
    """Formats size in bytes into a human-readable string."""
    if size_bytes < 1024:
        return f"{size_bytes}o"
    elif size_bytes < 1024 ** 2:
        return f"{size_bytes / 1024:.3f}Ko"
    else:
        return f"{size_bytes / 1024 ** 2:.3f}Mo"


def display_chunk(chunk_mesh: SoloChunkMesh, scale: float | int):
    """Display a chunk on the screen with optional offsets for positioning."""
    for index, triangle in enumerate(chunk_mesh.triangles):
        color = chunk_mesh.colors[index]
        points = [chunk_mesh.vertex_data[i] for i in triangle]
        points = [128 + point[i] * scale for point in points for i in (0, 2)]
        pyxel.tri(*points, color)

def generate_chunk(noise, height_params, color_params, x_chunk, y_chunk):
    return SoloChunkMesh(noise, height_params, color_params, x_chunk, y_chunk)


if __name__ == "__main__":
    biome = "archipel"
    height_param = SplineHeightParams(biome)
    color_param = ColorParams(biome)
    perlin_noise = PerlinGenerator(seed=1133, scale=30.0, octaves=10, persistence=0.5, lacunarity=2.0)

    st = time.perf_counter()
    chunk_meshes = []
    for x in range(-SIDE_LENGTH // 2, SIDE_LENGTH // 2 + 1):
        for y in range(-SIDE_LENGTH // 2, SIDE_LENGTH // 2 + 1):
            chunk_mesh = SoloChunkMesh(perlin_noise, height_param, color_param, x, y, SCALE)
            chunk_meshes.append(chunk_mesh)
    et = time.perf_counter()
    print(f"Size of chunks: {format_size(sum(chunk_mesh.get_byte_size() for chunk_mesh in chunk_meshes))}")
    print(f"Total time: {et - st:.5f}s")

    def draw():
        pyxel.cls(0)
        for cm in chunk_meshes:
            print(cm)
            display_chunk(cm, SCALE)
        print("frame")

    pyxel.init(256, 256, fps=30)
    pyxel.run(lambda: None, draw)
