#########################################################################################
# Filename    : htmlreport.py
# description : Builds a self contained, spreadsheet style HTML page from a DataFrame
#########################################################################################

import datetime
import html
import re

import pandas as pd

PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__</title>
<style>
  :root {
    --bg: #ffffff; --panel: #f3f3f3; --grid: #d4d4d4; --text: #1f1f1f; --muted: #6b6b6b;
    --head: #e6e6e6; --head-sel: #d3e3fd; --sel: #1a73e8; --sel-bg: #e8f0fe; --hover: #f5f9ff;
  }
  @media (prefers-color-scheme: dark) {
    :root {
      --bg: #1e1e1e; --panel: #2a2a2a; --grid: #444444; --text: #e8e8e8; --muted: #9a9a9a;
      --head: #333333; --head-sel: #2f4a73; --sel: #8ab4f8; --sel-bg: #263a5a; --hover: #26303f;
    }
  }
  * { box-sizing: border-box; }
  html, body { height: 100%; margin: 0; }
  body {
    display: flex; flex-direction: column; background: var(--bg); color: var(--text);
    font: 13px/1.4 -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  }
  .toolbar, .formula, .status {
    display: flex; align-items: center; gap: 10px; padding: 6px 12px;
    background: var(--panel); border-bottom: 1px solid var(--grid);
  }
  .toolbar h1 { margin: 0; font-size: 15px; font-weight: 600; }
  .toolbar .meta { color: var(--muted); }
  .toolbar input {
    margin-left: auto; width: min(320px, 45vw); padding: 5px 8px; font: inherit; color: var(--text);
    background: var(--bg); border: 1px solid var(--grid); border-radius: 4px;
  }
  .formula { padding: 4px 12px; }
  #cellname {
    min-width: 64px; padding: 3px 8px; text-align: center; font-weight: 600;
    background: var(--bg); border: 1px solid var(--grid); border-radius: 3px;
  }
  #cellvalue {
    flex: 1; min-height: 24px; padding: 3px 8px; overflow: hidden; text-overflow: ellipsis;
    white-space: nowrap; background: var(--bg); border: 1px solid var(--grid); border-radius: 3px;
    font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  }
  .sheet { flex: 1; overflow: auto; background: var(--bg); }
  table { border-collapse: separate; border-spacing: 0; counter-reset: row; }
  th, td {
    padding: 3px 8px; border-right: 1px solid var(--grid); border-bottom: 1px solid var(--grid);
    white-space: nowrap; max-width: 420px; overflow: hidden; text-overflow: ellipsis; text-align: left;
  }
  td.num { text-align: right; font-variant-numeric: tabular-nums; }
  thead th {
    position: sticky; top: 0; z-index: 2; background: var(--head); font-weight: 400;
    color: var(--muted); text-align: center; user-select: none;
  }
  thead tr.names th { top: 25px; color: var(--text); font-weight: 600; cursor: pointer; text-align: left; }
  thead tr.names th:hover { background: var(--head-sel); }
  thead th.corner, tbody th.rn { position: sticky; left: 0; z-index: 3; min-width: 46px; text-align: center; }
  tbody th.rn {
    z-index: 1; background: var(--head); color: var(--muted); font-weight: 400;
  }
  tbody tr { counter-increment: row; }
  tbody th.rn::before { content: counter(row); }
  tbody tr:hover td { background: var(--hover); }
  td.selected { outline: 2px solid var(--sel); outline-offset: -2px; background: var(--sel-bg) !important; }
  th .arrow { margin-left: 4px; color: var(--sel); }
  .status { border-top: 1px solid var(--grid); border-bottom: 0; color: var(--muted); }
  .status .tab {
    padding: 2px 14px; color: var(--text); background: var(--bg); border: 1px solid var(--grid);
    border-top: 2px solid var(--sel); border-radius: 0 0 4px 4px; font-weight: 600;
  }
  .status .right { margin-left: auto; }
  tr.hidden { display: none; }
  @media print { .toolbar input, .formula { display: none; } .sheet { overflow: visible; } }
</style>
</head>
<body>
<div class="toolbar">
  <h1>__TITLE__</h1>
  <span class="meta">__ROWS__ rows &times; __COLS__ columns &middot; generated __GENERATED__</span>
  <input id="filter" type="search" placeholder="Filter rows..." aria-label="Filter rows">
</div>
<div class="formula"><div id="cellname">&nbsp;</div><div id="cellvalue"></div></div>
<div class="sheet">
<table id="grid">
<thead>
<tr class="letters"><th class="corner"></th>__LETTERS__</tr>
<tr class="names"><th class="corner"></th>__NAMES__</tr>
</thead>
<tbody>
__BODY__
</tbody>
</table>
</div>
<div class="status">
  <span class="tab">__TITLE__</span>
  <span class="right" id="count"></span>
</div>
<script>
(function () {
  var table = document.getElementById("grid");
  var body = table.tBodies[0];
  var nameBox = document.getElementById("cellname");
  var valueBox = document.getElementById("cellvalue");
  var countBox = document.getElementById("count");
  var filterBox = document.getElementById("filter");
  var selected = null;
  var sortCol = -1, sortDir = 1;

  function letters(n) {
    var s = "";
    for (n += 1; n > 0; n = Math.floor((n - 1) / 26)) s = String.fromCharCode(65 + (n - 1) % 26) + s;
    return s;
  }

  function visibleRows() {
    return Array.prototype.filter.call(body.rows, function (r) { return !r.classList.contains("hidden"); });
  }

  function updateCount() {
    var shown = visibleRows().length;
    countBox.textContent = shown === body.rows.length
      ? shown + " rows"
      : shown + " of " + body.rows.length + " rows";
  }

  function select(td) {
    if (selected) selected.classList.remove("selected");
    selected = td;
    if (!td) { nameBox.innerHTML = "&nbsp;"; valueBox.textContent = ""; return; }
    td.classList.add("selected");
    td.scrollIntoView({ block: "nearest", inline: "nearest" });
    nameBox.textContent = letters(td.cellIndex - 1) + (visibleRows().indexOf(td.parentNode) + 1);
    valueBox.textContent = td.textContent;
  }

  body.addEventListener("click", function (e) {
    var td = e.target.closest("td");
    if (td) select(td);
  });

  document.addEventListener("keydown", function (e) {
    if (!selected || e.target === filterBox) return;
    var rows = visibleRows();
    var r = rows.indexOf(selected.parentNode);
    var c = selected.cellIndex;
    if (e.key === "ArrowDown") r++;
    else if (e.key === "ArrowUp") r--;
    else if (e.key === "ArrowRight") c++;
    else if (e.key === "ArrowLeft") c--;
    else return;
    e.preventDefault();
    r = Math.max(0, Math.min(rows.length - 1, r));
    c = Math.max(1, Math.min(rows[r].cells.length - 1, c));
    select(rows[r].cells[c]);
  });

  filterBox.addEventListener("input", function () {
    var q = filterBox.value.toLowerCase();
    Array.prototype.forEach.call(body.rows, function (r) {
      r.classList.toggle("hidden", q !== "" && r.textContent.toLowerCase().indexOf(q) === -1);
    });
    select(null);
    updateCount();
  });

  function value(row, col) {
    var t = row.cells[col].textContent.trim();
    var n = Number(t.replace(/,/g, ""));
    return t !== "" && isFinite(n) ? n : t.toLowerCase();
  }

  Array.prototype.forEach.call(table.querySelectorAll("tr.names th:not(.corner)"), function (th, i) {
    th.title = "Click to sort";
    th.addEventListener("click", function () {
      var col = i + 1;
      sortDir = sortCol === col ? -sortDir : 1;
      sortCol = col;
      Array.prototype.forEach.call(table.querySelectorAll(".arrow"), function (a) { a.remove(); });
      var arrow = document.createElement("span");
      arrow.className = "arrow";
      arrow.textContent = sortDir === 1 ? "\\u25B2" : "\\u25BC";
      th.appendChild(arrow);
      var rows = Array.prototype.slice.call(body.rows);
      rows.sort(function (a, b) {
        var x = value(a, col), y = value(b, col);
        if (x === "" || y === "") return x === y ? 0 : x === "" ? 1 : -1;
        if (typeof x === typeof y) return (x < y ? -1 : x > y ? 1 : 0) * sortDir;
        return (typeof x === "number" ? -1 : 1) * sortDir;
      });
      rows.forEach(function (r) { body.appendChild(r); });
      select(null);
    });
  });

  updateCount();
})();
</script>
</body>
</html>
"""


def columnLetters(index):
    letters = ""
    index += 1

    while index > 0:
        index, rem = divmod(index - 1, 26)
        letters = chr(65 + rem) + letters

    return letters


def cellText(value):
    if value is None or (not isinstance(value, (list, dict, tuple)) and pd.isna(value)):
        return ""

    return str(value)


def buildHtmlReport(dataFrame, title):
    """Returns the HTML of a page that looks and navigates like a spreadsheet."""

    numeric = [pd.api.types.is_numeric_dtype(dataFrame[col]) for col in dataFrame.columns]

    letters = "".join(
        f"<th>{columnLetters(i)}</th>" for i in range(len(dataFrame.columns))
    )
    names = "".join(f"<th>{html.escape(str(col))}</th>" for col in dataFrame.columns)

    rows = []

    for record in dataFrame.itertuples(index=False, name=None):
        cells = "".join(
            f'<td class="num">{html.escape(cellText(v))}</td>'
            if isNum
            else f"<td>{html.escape(cellText(v))}</td>"
            for v, isNum in zip(record, numeric)
        )
        rows.append(f'<tr><th class="rn"></th>{cells}</tr>')

    values = {
        "LETTERS": letters,
        "NAMES": names,
        "BODY": "\n".join(rows),
        "ROWS": str(len(dataFrame)),
        "COLS": str(len(dataFrame.columns)),
        "GENERATED": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "TITLE": html.escape(title),
    }

    # One pass, so placeholder like text inside the data is never substituted
    return re.sub(r"__([A-Z]+)__", lambda m: values.get(m.group(1), m.group(0)), PAGE_TEMPLATE)
