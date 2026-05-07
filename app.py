import argparse
import threading
import webbrowser
import os

from flask import Flask, render_template, jsonify, request, redirect
from werkzeug.utils import secure_filename

from src.sudoku import Sudoku
from src import patterns
from src.nyt_screenshot_ingestion import ingest_screenshot
from src.solver import (
    Solver, NakedSingleSolver, HiddenSingleSolver,
    PointingPairsSolver, NakedPairSolver, NakedTripleSolver,
    HiddenPairSolver, HiddenTripleSolver, NakedQuadSolver,
    BoxLineReductionSolver, XWingSolver, SimpleColoringSolver,
    SkyscraperSolver, SwordfishSolver, XYWingSolver,
    XYZWingSolver, UniqueRectangleSolver,
)

app = Flask(__name__)

PLACERS = [
    {"key": "NakedSingleSolver",  "label": "Naked Singles"},
    {"key": "HiddenSingleSolver", "label": "Hidden Singles"},
]
ELIMINATORS = [
    {"key": "PointingPairsSolver",    "label": "Pointing Pairs"},
    {"key": "NakedPairSolver",        "label": "Naked Pairs"},
    {"key": "NakedTripleSolver",      "label": "Naked Triples"},
    {"key": "HiddenPairSolver",       "label": "Hidden Pairs"},
    {"key": "HiddenTripleSolver",     "label": "Hidden Triples"},
    {"key": "NakedQuadSolver",        "label": "Naked Quads"},
    {"key": "BoxLineReductionSolver", "label": "Box/Line Reduction"},
    {"key": "XWingSolver",            "label": "X-Wing"},
    {"key": "SimpleColoringSolver",   "label": "Simple Coloring"},
    {"key": "SkyscraperSolver",       "label": "Skyscraper"},
    {"key": "SwordfishSolver",        "label": "Swordfish"},
    {"key": "XYWingSolver",           "label": "XY-Wing"},
    {"key": "XYZWingSolver",          "label": "XYZ-Wing"},
    {"key": "UniqueRectangleSolver",  "label": "Unique Rectangle"},
]

_pattern_number: int = None
game: Sudoku = None
_solvers: dict = {}
_manual_eliminations: set = set()  # (row, col, digit) triples removed by the user


def _apply_manual_eliminations() -> None:
    for r, c, d in _manual_eliminations:
        if d in game.board[r][c].candidates:
            game.board[r][c].candidates.remove(d)


def _init_board(mode="debug", pattern_number=None, board_data=None) -> None:
    global game, _solvers, _manual_eliminations, _pattern_number
    _manual_eliminations = set()
    _pattern_number = pattern_number
    game = Sudoku()
    
    if mode == "debug":
        game.initialize(mode="debug", pattern_number=pattern_number)
        Solver(game).populate_candidates()
    elif mode == "custom":
        game.initialize(mode="custom", board_data=board_data)
        # We do NOT automatically populate candidates here per user request.
        
    _solvers = {
        "NakedSingleSolver":      NakedSingleSolver(game),
        "HiddenSingleSolver":     HiddenSingleSolver(game),
        "PointingPairsSolver":    PointingPairsSolver(game),
        "NakedPairSolver":        NakedPairSolver(game),
        "NakedTripleSolver":      NakedTripleSolver(game),
        "HiddenPairSolver":       HiddenPairSolver(game),
        "HiddenTripleSolver":     HiddenTripleSolver(game),
        "NakedQuadSolver":        NakedQuadSolver(game),
        "BoxLineReductionSolver": BoxLineReductionSolver(game),
        "XWingSolver":            XWingSolver(game),
        "SimpleColoringSolver":   SimpleColoringSolver(game),
        "SkyscraperSolver":       SkyscraperSolver(game),
        "SwordfishSolver":        SwordfishSolver(game),
        "XYWingSolver":           XYWingSolver(game),
        "XYZWingSolver":          XYZWingSolver(game),
        "UniqueRectangleSolver":  UniqueRectangleSolver(game),
    }


def _board_to_json() -> list:
    return [
        [{"value": cell.value, "given": cell.given, "candidates": list(cell.candidates)}
         for cell in row]
        for row in game.board
    ]


def _snapshot() -> list:
    return [
        [{"value": cell.value, "candidates": list(cell.candidates)}
         for cell in row]
        for row in game.board
    ]


def _diff(before: list) -> list:
    changes = []
    for r in range(9):
        for c in range(9):
            b = before[r][c]
            cell = game.board[r][c]
            if b["value"] == 0 and cell.value != 0:
                changes.append({"type": "placed", "value": cell.value, "row": r, "col": c})
            elif b["value"] == 0:
                for v in b["candidates"]:
                    if v not in cell.candidates:
                        changes.append({"type": "eliminated", "value": v, "row": r, "col": c})
    return changes


@app.route("/")
def index():
    return render_template(
        "index.html",
        patterns=list(patterns.patterns.keys())
    )

@app.route("/load", methods=["POST"])
def load_board():
    pattern = request.form.get("pattern")
    file = request.files.get("screenshot")
    
    if file and file.filename != '':
        os.makedirs("inputs", exist_ok=True)
        filepath = os.path.join("inputs", "temp_upload.png")
        file.save(filepath)
        board_data = ingest_screenshot(filepath)
        _init_board(mode="custom", board_data=board_data)
    elif pattern:
        _init_board(mode="debug", pattern_number=int(pattern))
    else:
        return redirect("/")
        
    return redirect("/solve")

@app.route("/solve")
def solve():
    if game is None:
        return redirect("/")
    return render_template(
        "board.html",
        board_json=_board_to_json(),
        placers=PLACERS,
        eliminators=ELIMINATORS,
        pattern=_pattern_number,
    )


@app.route("/run/<solver_name>", methods=["POST"])
def run_solver(solver_name: str):
    if solver_name not in _solvers:
        return jsonify({"error": f"Unknown solver: {solver_name}"}), 400
    before = _snapshot()
    _solvers[solver_name].run()
    changes = _diff(before)
    placed     = sum(1 for c in changes if c["type"] == "placed")
    eliminated = sum(1 for c in changes if c["type"] == "eliminated")
    return jsonify({
        "board":    _board_to_json(),
        "changes":  changes,
        "placed":   placed,
        "eliminated": eliminated,
        "solver":   solver_name,
        "is_solved": game.is_solved(),
    })


@app.route("/set_value", methods=["POST"])
def set_value():
    global _manual_eliminations
    data = request.get_json()
    row, col, value = data.get("row"), data.get("col"), data.get("value")
    if not (isinstance(row, int) and isinstance(col, int) and isinstance(value, int)):
        return jsonify({"error": "Invalid input"}), 400
    if not (0 <= row <= 8 and 0 <= col <= 8 and 1 <= value <= 9):
        return jsonify({"error": "Out of range"}), 400
    cell = game.board[row][col]
    if cell.given:
        return jsonify({"error": "Cannot modify a given cell"}), 400
    cell.value = value
    cell.given = False
    cell.candidates = []
    _manual_eliminations = {e for e in _manual_eliminations if not (e[0] == row and e[1] == col)}
    Solver(game).populate_candidates()
    _apply_manual_eliminations()
    return jsonify({"board": _board_to_json()})


@app.route("/toggle_candidate", methods=["POST"])
def toggle_candidate():
    data = request.get_json()
    row, col, digit = data.get("row"), data.get("col"), data.get("digit")
    if not (isinstance(row, int) and isinstance(col, int) and isinstance(digit, int)):
        return jsonify({"error": "Invalid input"}), 400
    if not (0 <= row <= 8 and 0 <= col <= 8 and 1 <= digit <= 9):
        return jsonify({"error": "Out of range"}), 400
    cell = game.board[row][col]
    if cell.given or cell.value != 0:
        return jsonify({"error": "Cell is not editable"}), 400
    if digit in cell.candidates:
        cell.candidates.remove(digit)
        _manual_eliminations.add((row, col, digit))
    else:
        cell.candidates.append(digit)
        cell.candidates.sort()
        _manual_eliminations.discard((row, col, digit))
    return jsonify({"board": _board_to_json()})


@app.route("/populate_candidates", methods=["POST"])
def populate_candidates():
    if game is None:
        return jsonify({"error": "No game loaded"}), 400
    Solver(game).populate_candidates()
    return jsonify({"board": _board_to_json()})


if __name__ == "__main__":
    threading.Timer(0.6, lambda: webbrowser.open("http://127.0.0.1:5000")).start()
    app.run(host="127.0.0.1", port=5000, debug=False)
