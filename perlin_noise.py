import numpy as np
import matplotlib.pyplot as plt
import time

def lerp(a, b, t):
    return a + t * (b - a)

def fade(t):
    return ((6 * t - 15) * t + 10) * t * t * t

class PerlinNoise:
    _gradients = np.array([
        [1,1], [-1,1], [1,-1], [-1,-1],
        [1,0], [-1,0], [0,1], [0,-1]
    ])

    def __init__(self, seed=0):
        self.seed = seed
        self._perm = self._generate_permutation(seed)

    def _generate_permutation(self, seed):
        rng = np.random.default_rng(seed)
        p = np.arange(256, dtype=int)
        rng.shuffle(p)
        return np.tile(p, 2)

    def _grad(self, hash, x, y):
        g = self._gradients[hash & 7]
        return g[..., 0]*x + g[..., 1]*y

    def _perlin(self, x, y):
        xi = np.floor(x).astype(int) & 255
        yi = np.floor(y).astype(int) & 255
        xf = x - np.floor(x)
        yf = y - np.floor(y)

        u = fade(xf)
        v = fade(yf)

        aa = self._perm[self._perm[xi] + yi]
        ab = self._perm[self._perm[xi] + yi + 1]
        ba = self._perm[self._perm[xi + 1] + yi]
        bb = self._perm[self._perm[xi + 1] + yi + 1]

        x1 = lerp(self._grad(aa, xf, yf), self._grad(ba, xf - 1, yf), u)
        x2 = lerp(self._grad(ab, xf, yf - 1), self._grad(bb, xf - 1, yf - 1), u)
        return (lerp(x1, x2, v) + 1) / 2  # normalize

    def noise(self, x, y, octaves=1, persistence=0.5, lacunarity=2.0):
        # Accept scalars or numpy arrays
        x = np.asarray(x, dtype=np.float32)
        y = np.asarray(y, dtype=np.float32)

        total = np.zeros_like(x, dtype=np.float32)
        amplitude = 1.0
        frequency = 1.0
        max_amplitude = 0.0

        for _ in range(octaves):
            total += self._perlin(x * frequency, y * frequency) * amplitude
            max_amplitude += amplitude
            amplitude *= persistence
            frequency *= lacunarity

        return total / max_amplitude


if __name__ == '__main__':
    noise = PerlinNoise(seed=1337)
    # Generate grid
    size = 1000
    xs, ys = np.meshgrid(np.linspace(0, 5, size), np.linspace(0, 5, size))

    # Get noise
    start_time = time.perf_counter()
    z = noise.noise(xs, ys, octaves=4, persistence=0.5, lacunarity=2.0)
    end_time = time.perf_counter()

    print(f"Time taken: {end_time - start_time:.6f}s")

    # Show as image
    plt.imshow(z, cmap="terrain")
    plt.colorbar()
    plt.show()
