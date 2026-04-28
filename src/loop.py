import webbrowser
from pathlib import Path

from . import sudoku as sk
from .visualizer import BoardVisualizer


def _run_eliminators_until_stable(eliminators: list, verbose: bool) -> int:
    """Run all eliminators repeatedly until a full round produces no changes."""
    total = 0
    while True:
        changed = sum(e.run(verbose=verbose) for e in eliminators)
        total += changed
        if changed == 0:
            break
    return total


def _render_and_open(game: sk.Sudoku, prefix: str, label: str) -> None:
    path = Path(f"{prefix}_{label}.html").resolve()
    BoardVisualizer(game).render(str(path))
    webbrowser.open(path.as_uri())


def solve_loop(
    game: sk.Sudoku,
    placers: list,
    eliminators: list,
    output_prefix: str = "board",
    mode: str = "epoch",
    verbose: bool = False
) -> None:
    """
    Runs the solve loop in either step or epoch mode.

    A step is: stable elimination pass -> one placer -> stable elimination pass.
    An epoch is one step per placer in order, followed by a final stable elimination pass.

    In step mode the loop pauses for user input after each step.
    In epoch mode the loop pauses after each full epoch.
    Stuck detection fires at the end of each completed epoch in both modes.

    Args:
        game: The Sudoku board being solved.
        placers: Solver instances whose run() places values on the board.
        eliminators: Solver instances whose run() only eliminates candidates.
        output_prefix: Filename prefix for rendered HTML files.
        mode: 'step' or 'epoch'.
        verbose: Whether to print per-action solver output.
    """
    if mode not in ("step", "epoch"):
        raise ValueError("mode must be 'step' or 'epoch'")

    step_counter = 0
    epoch_counter = 0

    while True:
        epoch_placed = 0
        epoch_eliminated = 0

        for placer in placers:
            step_counter += 1
            solver_name = type(placer).__name__

            print(f"\n{'='*50}")
            print(f"  Step {step_counter}: {solver_name}")
            print(f"{'='*50}")

            pre_eliminated = _run_eliminators_until_stable(eliminators, verbose)
            print(f"  Pre-placer eliminations:  {pre_eliminated}")

            step_placed = placer.run(verbose=verbose)
            print(f"  {solver_name}: {step_placed} cell(s) placed")

            post_eliminated = _run_eliminators_until_stable(eliminators, verbose)
            print(f"  Post-placer eliminations: {post_eliminated}")

            epoch_placed += step_placed
            epoch_eliminated += pre_eliminated + post_eliminated

            if mode == "step":
                _render_and_open(game, output_prefix, f"step_{step_counter}")

                if game.is_solved():
                    print(f"\nSolved in {step_counter} step(s)!")
                    return

                response = input("\nContinue? [Enter / q]: ").strip().lower()
                if response == "q":
                    return

        # Final eliminator pass to close out the epoch cleanly
        final_eliminated = _run_eliminators_until_stable(eliminators, verbose)
        if final_eliminated > 0:
            print(f"\n  Final eliminator pass: {final_eliminated} eliminated")
        epoch_eliminated += final_eliminated

        # Stuck detection at epoch boundary
        if epoch_placed + epoch_eliminated == 0:
            print("\nSolver is stuck — no further progress possible.")
            return

        if mode == "epoch":
            epoch_counter += 1
            _render_and_open(game, output_prefix, f"epoch_{epoch_counter}")

            if game.is_solved():
                print(f"\nSolved in {epoch_counter} epoch(s)!")
                return

            response = input(
                f"\nEpoch {epoch_counter} complete "
                f"({epoch_placed} placed, {epoch_eliminated} eliminated). "
                f"Continue? [Enter / q]: "
            ).strip().lower()
            if response == "q":
                return
