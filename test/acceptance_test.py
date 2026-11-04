#!/usr/bin/env python3
"""MazePress acceptance test.

Proof-output method: build a real book (2 mazes per difficulty), then
re-verify every maze with a checker written independently of the
engine: it rebuilds the passage graph from the printed wall data and
uses UNION-FIND to prove the graph is a tree (cells-1 passages, one
component) -- in a tree the entrance-to-exit route is unique. It also
recomputes the route by its own BFS and compares it to the printed
solution path, cell by cell. Tamper cases: opening one extra internal
wall must break the tree property (a cycle appears); closing one
passage on the solution path must disconnect entrance from exit.
Plus PDF geometry, timing, determinism.
"""
import os
import sys
import time
from collections import deque

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from maze_press import run_mazepress  # noqa: E402

OUT = os.path.join(os.path.dirname(__file__), "out")
results = []


def check(name, ok, detail=""):
    results.append((name, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name} {detail}")


class DSU:
    def __init__(self, n):
        self.par = list(range(n))

    def find(self, x):
        while self.par[x] != x:
            self.par[x] = self.par[self.par[x]]
            x = self.par[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        self.par[ra] = rb
        return True


def edges_of(open_e, open_s, w, h):
    edges = []
    for r in range(h):
        for c in range(w - 1):
            if open_e[r][c]:
                edges.append(((r, c), (r, c + 1)))
    for r in range(h - 1):
        for c in range(w):
            if open_s[r][c]:
                edges.append(((r, c), (r + 1, c)))
    return edges


def is_tree(open_e, open_s, w, h):
    edges = edges_of(open_e, open_s, w, h)
    if len(edges) != w * h - 1:
        return False
    dsu = DSU(w * h)
    for (r1, c1), (r2, c2) in edges:
        if not dsu.union(r1 * w + c1, r2 * w + c2):
            return False
    return len({dsu.find(i) for i in range(w * h)}) == 1


def bfs_path(open_e, open_s, w, h):
    prev = {(0, 0): None}
    q = deque([(0, 0)])
    while q:
        r, c = q.popleft()
        if (r, c) == (h - 1, w - 1):
            break
        nbrs = []
        if c + 1 < w and open_e[r][c]:
            nbrs.append((r, c + 1))
        if c > 0 and open_e[r][c - 1]:
            nbrs.append((r, c - 1))
        if r + 1 < h and open_s[r][c]:
            nbrs.append((r + 1, c))
        if r > 0 and open_s[r - 1][c]:
            nbrs.append((r - 1, c))
        for nb in nbrs:
            if nb not in prev:
                prev[nb] = (r, c)
                q.append(nb)
    if (h - 1, w - 1) not in prev:
        return None
    path, cur = [], (h - 1, w - 1)
    while cur is not None:
        path.append(cur)
        cur = prev[cur]
    return path[::-1]


def main():
    t0 = time.time()
    s = run_mazepress(6, OUT, seed=42, difficulty="Mixed")
    dt = time.time() - t0
    ps = s["puzzles"]
    check("counts: 6 mazes, Easy/Medium/Hard rotating",
          len(ps) == 6 and [p["difficulty"] for p in ps] ==
          ["Easy", "Medium", "Hard", "Easy", "Medium", "Hard"],
          f"({[(p['w'], p['h']) for p in ps]})")

    tree_ok, path_ok = True, True
    for p in ps:
        if not is_tree(p["open_e"], p["open_s"], p["w"], p["h"]):
            tree_ok = False
        if bfs_path(p["open_e"], p["open_s"], p["w"], p["h"]) != p["path"]:
            path_ok = False
    check("every maze is a tree by union-find (cells-1 passages, one "
          "component) -- so the route is unique", tree_ok,
          f"(path lengths: {[p['path_len'] for p in ps]})")
    check("independent BFS route equals the printed solution path, "
          "cell by cell", path_ok, "")

    # tamper A: open one extra internal wall -> a cycle must appear
    p0 = ps[0]
    e2 = [row[:] for row in p0["open_e"]]
    s2 = [row[:] for row in p0["open_s"]]
    opened = False
    for r in range(p0["h"]):
        for c in range(p0["w"] - 1):
            if not e2[r][c] and not opened:
                e2[r][c] = True
                opened = True
    check("tamper: one extra opening breaks the tree proof",
          opened and not is_tree(e2, s2, p0["w"], p0["h"]), "")

    # tamper B: close a passage used by the solution path -> disconnect
    e3 = [row[:] for row in p0["open_e"]]
    s3 = [row[:] for row in p0["open_s"]]
    (r1, c1), (r2, c2) = p0["path"][0], p0["path"][1]
    if r1 == r2:
        e3[r1][min(c1, c2)] = False
    else:
        s3[min(r1, r2)][c1] = False
    check("tamper: closing a solution passage disconnects the exit",
          bfs_path(e3, s3, p0["w"], p0["h"]) is None, "")

    with open(s["pdf_path"], "rb") as fh:
        data = fh.read()
    pages = data.count(b"/Type /Page") - data.count(b"/Type /Pages")
    check("PDF 612x792pt, 11 pages", b"612 792" in data and pages == 11,
          f"({pages})")
    check("6-maze mixed book builds in under 180s", dt < 180, f"({dt:.1f}s)")

    s4 = run_mazepress(6, OUT, seed=42, difficulty="Mixed")
    same = [p["open_e"] for p in s4["puzzles"]] == [p["open_e"] for p in ps]
    check("deterministic for fixed seed", same, "")

    npass = sum(1 for _, ok, _ in results if ok)
    print(f"\n{npass}/{len(results)} PASS")
    with open(os.path.join(os.path.dirname(__file__),
                           "acceptance_results.txt"), "w") as fh:
        for name, ok, detail in results:
            fh.write(f"[{'PASS' if ok else 'FAIL'}] {name} {detail}\n")
        fh.write(f"\n{npass}/{len(results)} PASS\n")
    return 0 if npass == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
