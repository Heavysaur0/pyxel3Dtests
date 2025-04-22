
# (vertex_data, index_data, color_data)


CUBE = (
    tuple((a, b, c) for a in (-1, 1) for b in (-1, 1) for c in (-1, 1)),
    (
        (0, 1, 2), (2, 1, 3), # Bottom face
        (1, 0, 4), (1, 4, 5), # Front face
        (0, 2, 4), (4, 2, 6), # Left face
        (3, 1, 5), (3, 5, 7), # Right face
        (5, 4, 6), (5, 6, 7), # Top face
        (2, 3, 6), (6, 3, 7) # Back face
    )
)