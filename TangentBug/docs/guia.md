# Guia de Desenvolvimento de Algoritmos de Planejamento de Movimento

## 1. Visão Geral

A interface permite criar cenários com obstáculos e testar algoritmos de planejamento de movimento de robôs em uma grade 2D. Cada algoritmo é um **arquivo Python** que você cria e gerencia pela própria interface.

O fluxo de trabalho é simples:

1. Monte o cenário (defina início, chegada e obstáculos)
2. Escolha ou crie um arquivo de algoritmo
3. Implemente a função `plan()`
4. Clique em **Executar** e analise as métricas

---

## 2. A Função `plan()`

Todo arquivo de algoritmo deve definir uma função com exatamente esta assinatura:

```python
def plan(grid, start, goal):
    """
    Parâmetros
    ----------
    grid  : list[list[int]]
        Grade 2D. grid[linha][coluna] = 0 (livre) ou 1 (obstáculo).
    start : tuple[int, int]
        Posição inicial do robô no formato (coluna, linha).
    goal  : tuple[int, int]
        Posição de destino no formato (coluna, linha).

    Retorno
    -------
    list[tuple[int, int]]
        Sequência de posições (coluna, linha) do início ao destino,
        inclusive. Retorne [] se não houver caminho.
    """
    ...
    return caminho
```

> **Atenção:** a função **deve** se chamar `plan`. Outros nomes não serão reconhecidos.

---

## 3. Sistema de Coordenadas

A grade tem **40 colunas** (eixo horizontal) e **30 linhas** (eixo vertical).

```
         coluna →
         0   1   2   3  ...  39
linha  ┌───┬───┬───┬───┬───┬───┐
  ↓  0 │   │   │   │   │   │   │
     1 │   │ S │   │   │   │   │   S = start  (col=1, lin=1)
     2 │   │   │ ■ │ ■ │   │   │   ■ = obstáculo
     3 │   │   │ ■ │   │   │   │
     4 │   │   │   │   │ G │   │   G = goal   (col=4, lin=4)
       └───┴───┴───┴───┴───┴───┘
```

- `start = (1, 1)` → coluna 1, linha 1
- `goal  = (4, 4)` → coluna 4, linha 4
- `grid[2][2] = 1` → obstáculo na linha 2, coluna 2

**Movimentos possíveis:** 8 direções (incluindo diagonais).

---

## 4. Acessando o Grid

```python
rows = len(grid)          
cols = len(grid[0])      

def livre(c, r):
    return 0 <= c < cols and 0 <= r < rows and grid[r][c] == 0

viz4 = [(col+1, lin), (col-1, lin), (col, lin+1), (col, lin-1)]

offsets8 = [(1,0),(1,1),(0,1),(-1,1),(-1,0),(-1,-1),(0,-1),(1,-1)]
viz8 = [(col+dc, lin+dr) for dc, dr in offsets8]
```

---

## 5. Algoritmo Bug0

### 5.1 Conceito

**Bug0** é o algoritmo de navegação reativa mais simples da família *Bug*. Ele **não utiliza memória do ambiente** (sem mapa, sem histórico) — apenas a direção ao objetivo e a detecção imediata de obstáculos.

O robô alterna entre dois comportamentos:

| Comportamento | Condição | Ação |
|---|---|---|
| **Movimento livre** | Caminho ao objetivo está desobstruído | Move um passo na direção do objetivo |
| **Contorno** | Obstáculo bloqueia o caminho | Percorre o contorno até a direção ao objetivo ficar livre |

### 5.2 Pseudocódigo

```
Enquanto posição ≠ objetivo:
    Calcule a direção D que mais aproxima do objetivo

    Se a célula em D está livre:
        Mova para D  (modo: movimento livre)
    Senão:
        Gire no sentido horário até encontrar direção livre
        Mova nessa direção  (modo: contorno)
```

### 5.3 Implementação Comentada

```python
import math

def plan(grid, start, goal):
    rows, cols = len(grid), len(grid[0])

    # ── Função auxiliar: verifica se uma célula está dentro dos
    #    limites da grade e não é um obstáculo
    def livre(c, r):
        return 0 <= c < cols and 0 <= r < rows and grid[r][c] == 0

    # ── 8 direções de movimento (sentido horário a partir do leste)
    #    Índice:  0      1       2      3       4       5       6      7
    DIRS = [(1,0),(1,1),(0,1),(-1,1),(-1,0),(-1,-1),(0,-1),(1,-1)]
    #              L        N      NO       O      SO       S      SE
    #    (L=leste, N=norte, O=oeste, S=sul; grade: linha cresce para baixo)

    def melhor_dir(pos):
        """Retorna o índice em DIRS da direção que mais reduz a
        distância euclidiana ao objetivo."""
        c, r = pos
        gc, gr = goal
        melhor_i, melhor_d = 0, float('inf')
        for i, (dc, dr) in enumerate(DIRS):
            d = math.hypot((c + dc) - gc, (r + dr) - gr)
            if d < melhor_d:
                melhor_d, melhor_i = d, i
        return melhor_i

    # ── Caminho acumulado (começa na posição inicial)
    caminho = [start]
    pos     = start

    # Limite de passos para evitar loop infinito
    # (Bug0 não tem garantia de completude)
    MAX_PASSOS = rows * cols * 10

    for _ in range(MAX_PASSOS):
        if pos == goal:
            break

        # Determina a melhor direção em direção ao objetivo
        idx      = melhor_dir(pos)
        dc, dr   = DIRS[idx]
        nc, nr   = pos[0] + dc, pos[1] + dr

        if livre(nc, nr):
            # ── Modo 1: movimento livre ─────────────────────────
            pos = (nc, nr)
            caminho.append(pos)
        else:
            # ── Modo 2: contorno de obstáculo ───────────────────
            # Gira no sentido horário (incrementa o índice) até
            # encontrar uma célula livre para se mover
            moveu = False
            for i in range(1, 9):             # testa as 8 direções
                novo_idx      = (idx + i) % 8
                dc2, dr2      = DIRS[novo_idx]
                nc2, nr2      = pos[0] + dc2, pos[1] + dr2
                if livre(nc2, nr2):
                    pos = (nc2, nr2)
                    caminho.append(pos)
                    moveu = True
                    break
            if not moveu:
                break   # Robô completamente cercado — sem saída

    return caminho
```

### 5.4 Limitações do Bug0

- **Não é completo**: pode entrar em loop infinito em obstáculos côncavos ou labirintos
- **Não é ótimo**: o caminho não é o mais curto
- **Solução**: algoritmos mais sofisticados como **Bug1**, **Bug2** e **TangentBug** adicionam memória e critérios de saída do contorno para garantir completude

---

## 6. Algoritmos para Referência

| Algoritmo | Completo | Ótimo | Memória | Complexidade |
|---|:---:|:---:|---|---|
| Bug0 | ✗ | ✗ | Nenhuma | O(n) por passo |
| Bug1 | ✓ | ✗ | Ponto de entrada | O(P·n) |
| Bug2 | ✓ | ✗ | Linha M | O(P·n) |
| TangentBug | ✓ | ✗ | Pontos tangentes | O(P·n) |
| BFS | ✓ | ✓* | Grade completa | O(n²) |
| A* | ✓ | ✓ | Grade + heurística | O(n log n) |

*ótimo em número de passos (não em distância euclidiana)

**P** = perímetro dos obstáculos, **n** = número de células

---

## 7. Módulos Python Disponíveis

Você pode importar qualquer módulo da biblioteca padrão. Os mais úteis:

```python
from collections import deque    # fila para BFS
import heapq                     # fila de prioridade para A*, Dijkstra
import math                      # sqrt, hypot, inf, atan2
import random                    # algoritmos probabilísticos (RRT, etc.)
from itertools import product    # combinações de coordenadas
```

---

## 8. Saída de Depuração

Use `print()` normalmente — a saída aparece no painel **"Saída (print)"** após a execução:

```python
def plan(grid, start, goal):
    print(f"Grid: {len(grid)} linhas × {len(grid[0])} colunas")
    print(f"Start: {start}, Goal: {goal}")
    # ... seu algoritmo ...
    print(f"Caminho encontrado com {len(caminho)} passos")
    return caminho
```

---

## 9. Boas Práticas

- **Sempre retorne uma lista**, mesmo que seja `[]` (sem caminho)
- **Verifique os limites** antes de acessar células do grid
- **Evite loops infinitos** — adicione um contador de passos máximo
- **Meça a qualidade** pelo painel de métricas: tempo, passos e distância
- **Compare algoritmos** salvando cada um em um arquivo separado e alternando entre eles
