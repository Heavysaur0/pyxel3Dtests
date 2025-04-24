from pyinstrument import Profiler
import time

from render.mesh import Mesh


def load_mesh_from_file(path: str) -> Mesh:
    vertex_data = []
    color_data = []
    index_data = []
    normal_data = []
    fill_data = []
    border_data = []

    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split()
            prefix = parts[0]
            values = parts[1:]

            if prefix == 'v':
                vertex_data.append([float(x) for x in values])
            elif prefix == 'c':
                color_data.append(int(values[0]))
            elif prefix == 'f':
                index_data.append([int(x) for x in values])
            elif prefix == 'n':
                normal_data.append([float(x) for x in values])
            elif prefix == 'fill':
                fill_data.append(bool(int(values[0])))
            elif prefix == 'border':
                border_data.append(int(values[0]))
    
    lengths = [len(data) for data in (index_data, color_data, normal_data, fill_data, border_data) if data]
    assert all(lengths[i] == lengths[i + 1] for i in range(0, len(lengths) - 1)), f"Data is not same size: {lengths}"

    # Handle optional data
    kwargs = {}
    if normal_data:
        kwargs['normal_data'] = normal_data
    if fill_data:
        kwargs['fill_data'] = fill_data
    if border_data:
        kwargs['outer_border_data'] = border_data

    return Mesh(vertex_data, index_data, color_data, **kwargs)


def main():
    mesh = load_mesh_from_file("sokoban/3d models/box.mesh")
    print(mesh)

if __name__ == '__main__':
    profiler = Profiler()
    profiler.start()

    main()

    profiler.stop()
    print(profiler.output_text(unicode=True, color=True))