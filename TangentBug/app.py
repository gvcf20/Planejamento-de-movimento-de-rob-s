from flask import Flask, render_template, request, jsonify, send_from_directory
import time
import traceback
import threading
import sys
import io
import math
import os
import re

app = Flask(__name__)

BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
ALG_DIR   = os.path.join(BASE_DIR, "algorithms")
DOCS_DIR  = os.path.join(BASE_DIR, "docs")
os.makedirs(ALG_DIR, exist_ok=True)

_SAFE_NAME = re.compile(r'^[\w\-. ]+\.py$')


def execute_user_algorithm(code: str, grid: list, start: tuple, goal: tuple, timeout: int = 10):
    result = {"path": None, "error": None, "output": ""}
    namespace = {"__builtins__": __builtins__}

    def run():
        captured = io.StringIO()
        old_stdout = sys.stdout
        try:
            sys.stdout = captured
            exec(code, namespace) 
            sys.stdout = old_stdout
            result["output"] = captured.getvalue()

            if "plan" not in namespace:
                result["error"] = (
                    'Função "plan(grid, start, goal)" não encontrada.\n'
                    "Defina a função plan() no seu código."
                )
                return

            path = namespace["plan"](grid, start, goal)
            result["path"] = path

        except Exception:
            sys.stdout = old_stdout
            result["error"] = traceback.format_exc()
        finally:
            result["output"] = captured.getvalue()
            sys.stdout = old_stdout

    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    thread.join(timeout)

    if thread.is_alive():
        result["error"] = f"Timeout: o algoritmo excedeu {timeout} segundos de execução."

    return result


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/run", methods=["POST"])
def run_algorithm():
    data = request.get_json(force=True)
    code = data.get("code", "")
    grid = data.get("grid", [])
    start = data.get("start")
    goal = data.get("goal")

    if not grid or start is None or goal is None:
        return jsonify({"error": "Campos obrigatórios ausentes: grid, start, goal"}), 400

    start_t = tuple(start)
    goal_t = tuple(goal)

    t0 = time.perf_counter()
    res = execute_user_algorithm(code, grid, start_t, goal_t)
    elapsed = time.perf_counter() - t0

    if res["error"]:
        return jsonify({"error": res["error"], "output": res["output"]}), 400

    path = res["path"]

    if path is None:
        return jsonify({"error": "plan() retornou None. Retorne uma lista de posições (col, row)."}), 400

    try:
        path = [list(p) for p in path]
    except (TypeError, ValueError) as exc:
        return jsonify({"error": f"Formato inválido do caminho: {exc}"}), 400

    rows = len(grid)
    cols = len(grid[0]) if rows else 0
    warnings = []

    if not path:
        warnings.append("Caminho vazio — nenhuma posição retornada.")
    else:
        if list(path[0]) != list(start):
            warnings.append(f"Caminho começa em {path[0]}, não em {list(start)}.")
        if list(path[-1]) != list(goal):
            warnings.append(f"Caminho termina em {path[-1]}, não em {list(goal)}.")

        for pos in path:
            c, r = pos[0], pos[1]
            if not (0 <= r < rows and 0 <= c < cols):
                warnings.append(f"Posição {pos} está fora dos limites da grade.")
                break
            if grid[r][c] == 1:
                warnings.append(f"Caminho colide com obstáculo na posição {pos}.")
                break

    dist = 0.0
    for i in range(1, len(path)):
        dx = path[i][0] - path[i - 1][0]
        dy = path[i][1] - path[i - 1][1]
        dist += math.sqrt(dx * dx + dy * dy)

    return jsonify(
        {
            "path": path,
            "output": res["output"],
            "metrics": {
                "tempo_ms": round(elapsed * 1000, 2),
                "passos": len(path),
                "distancia": round(dist, 2),
                "chegou": bool(path and list(path[-1]) == list(goal)),
            },
            "warnings": warnings,
        }
    )


# ── File management ──────────────────────────────────────────────────────────

@app.route("/files", methods=["GET"])
def list_files():
    files = sorted(
        f for f in os.listdir(ALG_DIR)
        if f.endswith(".py") and os.path.isfile(os.path.join(ALG_DIR, f))
    )
    return jsonify({"files": files})


@app.route("/files/<filename>", methods=["GET"])
def read_file(filename):
    if not _SAFE_NAME.match(filename):
        return jsonify({"error": "Nome de arquivo inválido."}), 400
    path = os.path.join(ALG_DIR, filename)
    if not os.path.isfile(path):
        return jsonify({"error": "Arquivo não encontrado."}), 404
    with open(path, "r", encoding="utf-8") as f:
        return jsonify({"filename": filename, "content": f.read()})


@app.route("/files/<filename>", methods=["POST"])
def save_file(filename):
    if not _SAFE_NAME.match(filename):
        return jsonify({"error": "Nome de arquivo inválido. Use apenas letras, números, hífens e underscores."}), 400
    content = request.get_json(force=True).get("content", "")
    path = os.path.join(ALG_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return jsonify({"ok": True, "filename": filename})


@app.route("/files/<filename>", methods=["DELETE"])
def delete_file(filename):
    if not _SAFE_NAME.match(filename):
        return jsonify({"error": "Nome de arquivo inválido."}), 400
    path = os.path.join(ALG_DIR, filename)
    if not os.path.isfile(path):
        return jsonify({"error": "Arquivo não encontrado."}), 404
    os.remove(path)
    return jsonify({"ok": True})


# ── Documentation ─────────────────────────────────────────────────────────────

@app.route("/docs/guia.md")
def serve_docs():
    return send_from_directory(DOCS_DIR, "guia.md", mimetype="text/plain; charset=utf-8")


# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True, port=5000)
