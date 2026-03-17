"""
Tangent bug — Algoritmo de Navegação Reativa
======================================
O robô alterna entre dois comportamentos:
  1. Movimento livre: avança na direção do objetivo
  2. Contorno: ao colidir com obstáculo, percorre o contorno
     girando no sentido horário até a direção ao objetivo ficar livre.

Referência: Lumelsky & Stepanov, "Path-planning strategies for a point
mobile automaton moving amidst unknown obstacles" (1987).
"""

import math


def plan(grid, start, goal):
    rows, cols = len(grid), len(grid[0])

    def livre(c, r):
        return 0 <= c < cols and 0 <= r < rows and grid[r][c] == 0

    # 8 direções, sentido horário a partir do leste
    DIRS = [(1, 0), (1, 1), (0, 1), (-1, 1),
            (-1, 0), (-1, -1), (0, -1), (1, -1)]

    def melhor_dir(pos):
        """Índice da direção em DIRS que mais reduz a distância ao objetivo."""
        c, r = pos
        gc, gr = goal
        melhor_i, melhor_d = 0, float('inf')
        for i, (dc, dr) in enumerate(DIRS):
            d = math.hypot((c + dc) - gc, (r + dr) - gr)
            if d < melhor_d:
                melhor_d, melhor_i = d, i
        return melhor_i

    caminho = [start]
    pos = start
    MAX_PASSOS = rows * cols * 10

    for passo in range(MAX_PASSOS):
        if pos == goal:
            break

        idx = melhor_dir(pos)
        dc, dr = DIRS[idx]
        nc, nr = pos[0] + dc, pos[1] + dr

        if livre(nc, nr):
            # --- Modo 1: movimento livre ---------------------------------
            pos = (nc, nr)
            caminho.append(pos)
        else:
            # --- Modo 2: contorno de obstáculo --------------------------
            # Gira no sentido horário até encontrar célula livre
            moveu = False
            for i in range(1, 9):
                novo_idx = (idx + i) % 8
                dc2, dr2 = DIRS[novo_idx]
                nc2, nr2 = pos[0] + dc2, pos[1] + dr2
                if livre(nc2, nr2):
                    pos = (nc2, nr2)
                    caminho.append(pos)
                    moveu = True
                    break
            if not moveu:
                print(f"Robô preso em {pos} após {passo} passos.")
                break

    if pos != goal:
        print(f"Objetivo não alcançado (limite de {MAX_PASSOS} passos).")
    else:
        print(f"Chegou ao objetivo em {len(caminho)} passos.")

    return caminho
