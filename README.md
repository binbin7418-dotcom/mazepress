# MazePress

Build print-ready **maze puzzle books for Amazon KDP** where every maze is a *perfect maze* — its solution route is unique by construction, and re-proven before printing.

## Why

Most maze generators can only promise "a solution exists". MazePress promises the stronger thing maze books actually need: **exactly one route** from entrance to exit, and it can prove it —

1. Passages are carved by randomized depth-first search, producing a **spanning tree** over all cells (a perfect maze): connected, with exactly *cells − 1* passages.
2. In a tree there is exactly one path between any two cells — so the entrance-to-exit route is unique by graph theory, not by solver luck.
3. Before printing, every maze is re-verified: passage count equals cells − 1, the passage graph is one connected component, and the solution path printed at the back is the route a fresh breadth-first search finds.

Difficulty is size: Easy 12×10, Medium 18×14, Hard 24×18 — bigger grids, longer true paths, more dead ends. In the acceptance book the Hard mazes' solution paths ran 144–200 steps.

## Use

**App (Windows):** launch `MazePress.exe`, choose the maze count, difficulty (Easy / Medium / Hard, or Mixed rotating all three) and a seed, click **Build the book**. Output: `maze_book.pdf` in a `mazepress_out` folder — title page, one maze per page (entrance top-left, exit bottom-right, with the solution-path length and dead-end count printed as difficulty data), then solution pages with the route drawn in. 8.5×11in (612×792pt).

**Command line:** `python maze_press.py out/ --puzzles=50 --difficulty=Mixed --seed=42`

A 6-maze sample book is included (`sample_book.pdf`).

## Verified

Acceptance test (8/8 PASS, `test/acceptance_results.txt`): a 6-maze mixed book re-verified by an independent checker using **union-find** — every maze is a tree (cells−1 passages, one component), an independent BFS route equals the printed solution path cell by cell, opening one extra internal wall breaks the tree proof (a cycle appears), and closing one passage on the solution path disconnects the exit. PDF exactly 11 pages at 612×792pt; whole book in about 0.2 seconds; deterministic for a fixed seed.

## Scope

Rectangular perfect mazes on three sizes — a public-domain puzzle form. No braided/loop mazes (loops are exactly what the uniqueness proof forbids). 100% local — no uploads, no accounts, no per-book fees. Deterministic seeds make series production repeatable.

## Build from source

`pip install pyinstaller reportlab`, then `pyinstaller mazepress.spec`. Or push to GitHub and let the included Actions workflow build the Windows package.
