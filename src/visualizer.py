from . import sudoku as sk
from pathlib import Path


class BoardVisualizer:
    def __init__(self, sudoku: sk.Sudoku) -> None:
        self.sudoku = sudoku

    def render(self, path: str = "board.html") -> None:
        Path(path).write_text(self._build_html(), encoding="utf-8")

    def _cell_html(self, cell: sk.Cell) -> str:
        if cell.value != 0:
            css_class = "given" if cell.given else "solved"
            return f'<span class="{css_class}">{cell.value}</span>'

        spans = []
        for digit in range(1, 10):
            text = str(digit) if digit in cell.candidates else ""
            spans.append(f"<span>{text}</span>")
        return f'<div class="candidates">{"".join(spans)}</div>'

    def _build_html(self) -> str:
        rows_html = []
        for row in range(9):
            cells_html = []
            for col in range(9):
                cell = self.sudoku.board[row][col]
                td_classes = []
                if col == 2 or col == 5:
                    td_classes.append("box-right")
                if row == 2 or row == 5:
                    td_classes.append("box-bottom")
                class_attr = f' class="{" ".join(td_classes)}"' if td_classes else ""
                cells_html.append(f"<td{class_attr}>{self._cell_html(cell)}</td>")
            rows_html.append(f'<tr>{"".join(cells_html)}</tr>')

        table_body = "\n      ".join(rows_html)

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Sudoku Board</title>
  <style>
    body {{
      font-family: Arial, sans-serif;
      display: flex;
      justify-content: center;
      padding: 40px;
      background: #f0f0f0;
    }}
    table {{
      border-collapse: collapse;
      border: 3px solid #1a1a1a;
    }}
    td {{
      width: 60px;
      height: 60px;
      border: 1px solid #bbb;
      text-align: center;
      vertical-align: middle;
      padding: 0;
    }}
    td.box-right {{ border-right: 3px solid #1a1a1a; }}
    td.box-bottom {{ border-bottom: 3px solid #1a1a1a; }}
    .given {{
      font-size: 32px;
      font-weight: bold;
      color: #1a1a1a;
    }}
    .solved {{
      font-size: 32px;
      font-weight: bold;
      color: #2563eb;
    }}
    .candidates {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      grid-template-rows: repeat(3, 1fr);
      width: 100%;
      height: 100%;
      box-sizing: border-box;
      padding: 2px;
    }}
    .candidates span {{
      font-size: 11px;
      color: #7c7c7c;
      display: flex;
      align-items: center;
      justify-content: center;
      line-height: 1;
    }}
  </style>
</head>
<body>
  <table>
    <tbody>
      {table_body}
    </tbody>
  </table>
</body>
</html>"""
