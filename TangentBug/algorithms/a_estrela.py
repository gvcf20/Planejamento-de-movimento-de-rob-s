"""
A* (A-estrela)
==============
Busca informada com heurística euclidiana.
Garante o caminho de menor custo (distância euclidiana acumulada).
"""

import heapq
import math


def plan(grid, start, goal):
    rows, cols = len(grid), len(grid[0])

    if grid[start[1]][start[0]] or grid[goal[1]][goal[0]]:
        print("Início ou destino está sobre um obstáculo.")
        return []

    # 8 direções com custo real (diagonais custam √2)
    DIRS = [(1, 0, 1.0), (-1, 0, 1.0), (0, 1, 1.0), (0, -1, 1.0),
            (1, 1, 1.414), (1, -1, 1.414), (-1, 1, 1.414), (-1, -1, 1.414)]

    def h(pos):
        return math.hypot(pos[0] - goal[0], pos[1] - goal[1])

    # Heap: (f, g, posição, caminho)
    heap    = [(h(start), 0.0, start, [start])]
    custo   = {start: 0.0}

    while heap:
        f, g, pos, caminho = heapq.heappop(heap)
        col, row = pos

        if pos == goal:
            print(f"A* encontrou caminho: {len(caminho)} passos, "
                  f"custo {g:.2f}.")
            return caminho

        if g > custo.get(pos, float('inf')):
            continue   # versão desatualizada no heap

        for dc, dr, custo_passo in DIRS:
            nc, nr = col + dc, row + dr
            if not (0 <= nc < cols and 0 <= nr < rows) or grid[nr][nc]:
                continue
            ng  = g + custo_passo
            viz = (nc, nr)
            if ng < custo.get(viz, float('inf')):
                custo[viz] = ng
                heapq.heappush(heap, (ng + h(viz), ng, viz, caminho + [viz]))

    print("Nenhum caminho encontrado.")
    return []
