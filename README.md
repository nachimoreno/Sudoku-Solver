# Sudoku Solver

A Python Sudoku solver with an interactive Flask web UI and a step-by-step demo mode for exploring human-style solving techniques.

## Overview

This project models a Sudoku board, generates candidate lists for unsolved cells, and applies a growing set of solving strategies to place values or eliminate candidates. It is currently designed around built-in debug puzzles rather than free-form puzzle input.

## Features

- Interactive local web app for running individual solving techniques
- Step-by-step solver feedback showing placements and candidate eliminations
- HTML board rendering with candidate display and move highlighting
- CLI demo flow for walking through solver progress in the browser
- Multiple built-in Sudoku test patterns for debugging and experimentation

## Implemented Techniques

### Placers

- Naked Singles
- Hidden Singles

### Eliminators

- Pointing Pairs / Pointing Triples
- Naked Pairs
- Naked Triples
- Hidden Pairs
- Hidden Triples
- Naked Quads
- Box/Line Reduction
- X-Wing
- Simple Coloring
- Skyscraper
- Swordfish
- XY-Wing
- XYZ-Wing
- Unique Rectangle

## Project Structure

```text
.
|-- app.py                 # Flask web app
|-- demo.py                # Step-by-step demo runner
|-- requirements.txt
|-- templates/
|   `-- board.html         # Web UI template
`-- src/
    |-- sudoku.py          # Board and cell models
    |-- solver.py          # Solver strategies
    |-- loop.py            # Demo solve loop
    |-- visualizer.py      # HTML board renderer
    `-- patterns.py        # Built-in debug puzzles
```

## Installation

1. Clone the repository.
2. Create and activate a virtual environment.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Run the web app

Start the interactive solver UI with one of the built-in debug patterns:

```bash
python3 app.py --pattern 1
```

Available patterns are currently defined in [`src/patterns.py`](src/patterns.py).

The app starts a local Flask server at `http://127.0.0.1:5000` and attempts to open it in your browser automatically.

### Run the demo script

The demo script runs the solve loop using the configured strategies and opens rendered board states in the browser:

```bash
python3 demo.py
```

The demo writes HTML snapshots under `outputs/`, so create that folder first if it does not already exist:

```bash
mkdir -p outputs
```

## How It Works

1. A built-in puzzle pattern is loaded into the `Sudoku` board model.
2. Initial candidates are populated for every empty cell.
3. Solver strategies are applied to either:
   - place a value directly, or
   - eliminate impossible candidates
4. The board state is re-rendered after each move or solving step.

## Current Limitations

- Puzzle input is currently limited to the predefined patterns in [`src/patterns.py`](src/patterns.py).
- `Sudoku.initialize(mode="production")` is not implemented yet.
- The project currently focuses on local usage and experimentation rather than packaging or deployment.

## Roadmap

- Add support for custom puzzle input
- Expand validation and automated tests
- Improve solver coverage and technique explanations
- Add exportable solve traces or statistics
