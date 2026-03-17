import math

# ──────────────────────────────────────────────────────
#  TangentBug  (versão simplificada)
#
#  Estratégia:
#   1. Move-se em linha reta ao destino.
#   2. Ao colidir com um obstáculo, percorre o contorno
#      até encontrar um ponto "tangente" do qual seja
#      possível retomar a rota ao destino sem colisão.
#
#  Referência: Kamon, Rimon & Rivlin (1998).
# ──────────────────────────────────────────────────────

def plan(grid, start, goal):
    rows, cols = len(grid), len(grid[0])

    def free(c, r):
        return 0 <= c < cols and 0 <= r < rows and grid[r][c] == 0

    def neighbors8(c, r):
        dirs = [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]
        return [(c+dc, r+dr) for dc,dr in dirs if free(c+dc, r+dr)]

    def line_free(a, b):
        """Verifica se o segmento de a até b não passa por obstáculos (aprox.)."""
        c0, r0 = a; c1, r1 = b
        steps = max(abs(c1-c0), abs(r1-r0)) * 4 + 1
        for i in range(steps + 1):
            t  = i / steps
            c  = round(c0 + (c1 - c0) * t)
            r  = round(r0 + (r1 - r0) * t)
            if not free(c, r):
                return False
        return True

    def bfs_contour(pos, goal, max_steps=2000):
        """
        Percorre o contorno do obstáculo (BFS limitado) buscando
        o ponto de menor distância ao goal com linha livre.
        """
        from collections import deque
        queue   = deque([(pos, [pos])])
        visited = {pos}
        best    = None
        best_d  = float('inf')

        while queue:
            (c, r), path = queue.popleft()
            if len(path) > max_steps:
                break
            d = math.hypot(c - goal[0], r - goal[1])
            if d < best_d and line_free((c, r), goal):
                best_d = d
                best   = path

            for nc, nr in neighbors8(c, r):
                if (nc, nr) not in visited:
                    visited.add((nc, nr))
                    queue.append(((nc, nr), path + [(nc, nr)]))

        return best or [pos]

    # ── Main loop ──
    path    = [start]
    pos     = start
    visited = {start}
    MAX_IT  = rows * cols * 2

    for _ in range(MAX_IT):
        if pos == goal:
            break

        # Tenta mover em linha reta ao goal
        if line_free(pos, goal):
            # Caminha passo a passo até o goal
            c, r = pos
            gc, gr = goal
            steps = max(abs(gc-c), abs(gr-r))
            for s in range(1, steps + 1):
                t  = s / steps
                nc = round(c + (gc - c) * t)
                nr = round(r + (gr - r) * t)
                if (nc, nr) not in visited:
                    visited.add((nc, nr))
                    path.append((nc, nr))
            pos = goal
            break

        # Linha bloqueada: contorna o obstáculo
        contour = bfs_contour(pos, goal)
        for p in contour[1:]:
            if p not in visited:
                visited.add(p)
                path.append(p)
        pos = path[-1]

    return path
