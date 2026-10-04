"""Latihan Decision Tree ID3: diagnosis hipertensi (materi Minggu 4)."""

from collections import Counter
import csv
import io
from math import log2
from contextlib import redirect_stdout
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

FITUR = ["usia", "berat", "kelamin"]
TARGET = "hipertensi"
DATA = [
    {"nama": "Ali", "usia": "muda", "berat": "overweight", "kelamin": "pria", "hipertensi": "ya"},
    {"nama": "Edi", "usia": "muda", "berat": "underweight", "kelamin": "pria", "hipertensi": "tidak"},
    {"nama": "Annie", "usia": "muda", "berat": "average", "kelamin": "wanita", "hipertensi": "tidak"},
    {"nama": "Budiman", "usia": "tua", "berat": "overweight", "kelamin": "pria", "hipertensi": "tidak"},
    {"nama": "Herman", "usia": "tua", "berat": "overweight", "kelamin": "pria", "hipertensi": "ya"},
    {"nama": "Didi", "usia": "muda", "berat": "underweight", "kelamin": "pria", "hipertensi": "tidak"},
    {"nama": "Rina", "usia": "tua", "berat": "overweight", "kelamin": "wanita", "hipertensi": "ya"},
    {"nama": "Gatot", "usia": "tua", "berat": "average", "kelamin": "pria", "hipertensi": "tidak"},
]


def entropy(rows):
    counts = Counter(r[TARGET] for r in rows)
    return -sum((n / len(rows)) * log2(n / len(rows)) for n in counts.values())


def majority(rows):
    counts = Counter(r[TARGET] for r in rows)
    terbesar = max(counts.values())
    kandidat = [label for label, n in counts.items() if n == terbesar]
    return "tidak" if "tidak" in kandidat else sorted(kandidat)[0]


def gain(rows, feature):
    sisa = 0.0
    for value in {r[feature] for r in rows}:
        subset = [r for r in rows if r[feature] == value]
        sisa += len(subset) / len(rows) * entropy(subset)
    return entropy(rows) - sisa, sisa


def build_tree(rows, features):
    labels = {r[TARGET] for r in rows}
    if len(labels) == 1:
        return next(iter(labels))
    if not features:
        return majority(rows)
    best = max(features, key=lambda f: gain(rows, f)[0])
    tree = {"fitur": best, "default": majority(rows), "cabang": {}}
    for value in sorted({r[best] for r in rows}):
        subset = [r for r in rows if r[best] == value]
        tree["cabang"][value] = build_tree(subset, [f for f in features if f != best])
    return tree


def predict(tree, row):
    if isinstance(tree, str):
        return tree
    branch = tree["cabang"].get(row[tree["fitur"]])
    return tree["default"] if branch is None else predict(branch, row)


def print_tree(tree, indent=""):
    if isinstance(tree, str):
        print(indent + "=> " + tree.upper())
        return
    print(indent + "[" + tree["fitur"].upper() + "]")
    for value, branch in tree["cabang"].items():
        print(indent + f"  {tree['fitur']} = {value}")
        print_tree(branch, indent + "    ")


def rules(tree, conditions=None):
    conditions = conditions or []
    if isinstance(tree, str):
        return [(conditions, tree)]
    result = []
    for value, branch in tree["cabang"].items():
        result += rules(branch, conditions + [f"{tree['fitur']}={value}"])
    return result


def errors(tree, rows):
    return sum(predict(tree, r) != r[TARGET] for r in rows)


def prune(tree, rows):
    """Reduced-error pruning memakai data latihan; tie memilih pohon lebih sederhana."""
    if isinstance(tree, str):
        return tree
    feature = tree["fitur"]
    for value, branch in list(tree["cabang"].items()):
        subset = [r for r in rows if r[feature] == value]
        tree["cabang"][value] = prune(branch, subset)
    leaf = majority(rows)
    leaf_error = sum(r[TARGET] != leaf for r in rows)
    return leaf if leaf_error <= errors(tree, rows) else tree


def main():
    print("LATIHAN DECISION TREE: HIPERTENSI")
    print(f"Entropy(S) = {entropy(DATA):.4f}")
    print("\nEvaluasi calon node akar:")
    for feature in FITUR:
        g, remainder = gain(DATA, feature)
        print(f"- {feature:8s}: entropy tertimbang={remainder:.4f}, gain={g:.4f}")

    tree = build_tree(DATA, FITUR)
    print("\nPohon sebelum pruning:")
    print_tree(tree)
    print("\nRules:")
    for i, (conds, answer) in enumerate(rules(tree), 1):
        print(f"R{i}: IF {' AND '.join(conds)} THEN {TARGET}={answer}")
    e = errors(tree, DATA)
    print(f"\nError tanpa pruning = {e}/{len(DATA)} = {100*e/len(DATA):.2f}%")

    pruned = prune(build_tree(DATA, FITUR), DATA)
    print("\nPohon setelah pruning:")
    print_tree(pruned)
    ep = errors(pruned, DATA)
    print(f"Error dengan pruning = {ep}/{len(DATA)} = {100*ep/len(DATA):.2f}%")


def launch_gui():
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        main()
    tree = build_tree(DATA, FITUR)
    pruned = prune(build_tree(DATA, FITUR), DATA)

    root = tk.Tk()
    root.title("Decision Tree - Hipertensi")
    root.geometry("920x650")
    root.minsize(720, 480)

    header = ttk.Frame(root, padding=12)
    header.pack(fill="x")
    ttk.Label(header, text="Decision Tree: Hipertensi", font=("Segoe UI", 18, "bold")).pack(side="left")

    def export_csv():
        path = filedialog.asksaveasfilename(
            title="Simpan hasil prediksi", defaultextension=".csv",
            initialfile="hasil_hipertensi.csv", filetypes=[("CSV", "*.csv")]
        )
        if not path:
            return
        fields = ["nama"] + FITUR + [TARGET, "prediksi_tanpa_pruning", "prediksi_pruning", "hasil_pruning"]
        with open(path, "w", newline="", encoding="utf-8-sig") as file:
            writer = csv.DictWriter(file, fieldnames=fields)
            writer.writeheader()
            for row in DATA:
                before, after = predict(tree, row), predict(pruned, row)
                writer.writerow({**row, "prediksi_tanpa_pruning": before,
                                 "prediksi_pruning": after,
                                 "hasil_pruning": "BENAR" if after == row[TARGET] else "SALAH"})
        messagebox.showinfo("Berhasil", f"CSV berhasil disimpan:\n{path}")

    ttk.Button(header, text="Export CSV", command=export_csv).pack(side="right")
    text = tk.Text(root, wrap="none", font=("Consolas", 10), padx=12, pady=12)
    ybar = ttk.Scrollbar(root, orient="vertical", command=text.yview)
    xbar = ttk.Scrollbar(root, orient="horizontal", command=text.xview)
    text.configure(yscrollcommand=ybar.set, xscrollcommand=xbar.set)
    ybar.pack(side="right", fill="y")
    xbar.pack(side="bottom", fill="x")
    text.pack(fill="both", expand=True)
    text.insert("1.0", buffer.getvalue())
    text.configure(state="disabled")
    root.mainloop()


if __name__ == "__main__":
    launch_gui()
