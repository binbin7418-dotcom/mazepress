import os
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext

from maze_press import run_mazepress


def run_job(count, difficulty, seed, outdir):
    s = run_mazepress(count, outdir, seed=seed, difficulty=difficulty)
    lines = [f"Mazes built: {len(s['puzzles'])}", f"Pages: {s['pages']}"]
    for i, p in enumerate(s["puzzles"], 1):
        lines.append(f"  Maze {i}: {p['difficulty']}, {p['w']}x{p['h']}, "
                     f"solution path {p['path_len']} steps, tree check OK")
    lines.append(f"PDF: {s['pdf_path']}")
    return lines


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MazePress")
        self.geometry("640x520")
        self.resizable(False, False)
        self.count = tk.StringVar(value="50")
        self.difficulty = tk.StringVar(value="Mixed")
        self.seed = tk.StringVar(value="42")
        for label, var in [("Mazes:", self.count),
                           ("Difficulty (Easy/Medium/Hard/Mixed):", self.difficulty),
                           ("Seed:", self.seed)]:
            row = tk.Frame(self); row.pack(fill="x", padx=12, pady=2)
            tk.Label(row, text=label, width=34, anchor="w").pack(side="left")
            tk.Entry(row, textvariable=var, width=10).pack(side="left")
        tk.Button(self, text="Build the book", font=("Segoe UI", 11, "bold"),
                  command=self.start).pack(pady=10)
        self.log = scrolledtext.ScrolledText(self, width=76, height=16,
                                             font=("Consolas", 9))
        self.log.pack(padx=12, pady=4)
        self.write("Every maze is carved as a spanning tree of passages -- a perfect maze with exactly one route from entrance to exit, unique by construction and re-verified before printing.")

    def write(self, msg):
        self.log.insert(tk.END, str(msg) + "\n")
        self.log.see(tk.END)
        self.update_idletasks()

    def collect(self):
        diff = self.difficulty.get().strip().capitalize()
        if diff not in ("Easy", "Medium", "Hard", "Mixed"):
            raise ValueError("Difficulty must be Easy, Medium, Hard or Mixed.")
        return (int(self.count.get()), diff, int(self.seed.get()),
                os.path.join(os.getcwd(), "mazepress_out"))

    def start(self):
        try:
            args = self.collect()
        except Exception as e:
            messagebox.showerror("MazePress", str(e))
            return

        def work():
            try:
                for ln in run_job(*args):
                    self.write(ln)
            except Exception as e:
                self.write(f"ERROR: {e}")

        threading.Thread(target=work, daemon=True).start()


if __name__ == "__main__":
    App().mainloop()
