import argparse
import threading
import webbrowser

from flask import Flask, render_template, jsonify

from src.sudoku import Sudoku
from src.solver import (
    Solver, NakedSingleSolver, HiddenSingleSolver,
    PointingPairsSolver, NakedPairSolver, NakedTripleSolver,
)

app = Flask(__name__)

PLACERS = [
    {"key": "NakedSingleSolver",  "label": "Naked Singles"},
    {"key": "HiddenSingleSolver", "label": "Hidden Singles"},
]
ELIMINATORS = [
    {"key": "PointingPairsSolver", "label": "Pointing Pairs"},
    {"key": "NakedPairSolver",     "label": "Naked Pairs"},
    {"key": "NakedTripleSolver",   "label": "Naked Triples"},
]

_pattern_number: int = None
game: Sudoku = None
_solvers: dict = {}


def _init_board() -> None:
    global game, _solvers
    game = Sudoku()
    game.initialize(mode="debug", pattern_number=_pattern_number)
    Solver(game).populate_candidates()
    _solvers = {
        "NakedSingleSolver":   NakedSingleSolver(game),
        "HiddenSingleSolver":  HiddenSingleSolver(game),
        "PointingPairsSolver": PointingPairsSolver(game),
        "NakedPairSolver":     NakedPairSolver(game),
        "NakedTripleSolver":   NakedTripleSolver(game),
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


@app.route("/reset", methods=["POST"])
def reset():
    _init_board()
    return jsonify({
        "board":    _board_to_json(),
        "changes":  [],
        "placed":   0,
        "eliminated": 0,
        "solver":   None,
        "is_solved": False,
    })


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sudoku Solver — interactive web UI")
    parser.add_argument("--pattern", type=int, required=True, help="Debug pattern number to load")
    args, _ = parser.parse_known_args()
    _pattern_number = args.pattern
    _init_board()
    threading.Timer(0.6, lambda: webbrowser.open("http://127.0.0.1:5000")).start()
    app.run(host="127.0.0.1", port=5000, debug=False)
