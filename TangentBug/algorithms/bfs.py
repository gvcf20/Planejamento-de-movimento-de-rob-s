"""
BFS — Busca em Largura (Breadth-First Search)
=============================================
Garante o caminho com menor número de passos (ótimo em passos,
não necessariamente em distância euclidiana).
"""

from collections import deque


def plan(grid, start, goal):
    rows, cols = len(grid), len(grid[0])

    if grid[start[1]][start[0]] or grid[goal[1]][goal[0]]:
        print("Início ou destino está sobre um obstáculo.")
        return []

    # 8 direções
    DIRS = [(1, 0), (-1, 0), (0, 1), (0, -1),
            (1, 1), (1, -1), (-1, 1), (-1, -1)]

    queue   = deque([(start, [start])])
    visited = {start}

    while queue:
        (col, row), caminho = queue.popleft()

        if (col, row) == goal:
            print(f"Caminho encontrado: {len(caminho)} passos.")
            return caminho

        for dc, dr in DIRS:
            nc, nr = col + dc, row + dr
            pos = (nc, nr)
            if (0 <= nc < cols and 0 <= nr < rows
                    and grid[nr][nc] == 0
                    and pos not in visited):
                visited.add(pos)
                queue.append((pos, caminho + [pos]))

    print("Nenhum caminho encontrado.")
    return []
