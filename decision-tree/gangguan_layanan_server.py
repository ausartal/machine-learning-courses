"""Decision Tree ID3 untuk mendeteksi gangguan layanan/server jaringan."""

from collections import Counter
import csv
import io
from math import log2
from contextlib import redirect_stdout
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

FITUR = ["waktu", "paket", "frekuensi", "prioritas"]
TARGET = "status"
DATA_MENTAH = [
    ("pendek", "besar", "sedang", "rendah", "gangguan"),
    ("pendek", "kecil", "rendah", "tinggi", "gangguan"),
    ("panjang", "besar", "sedang", "tinggi", "normal"),
    ("panjang", "kecil", "tinggi", "rendah", "normal"),
    ("pendek", "besar", "tinggi", "tinggi", "gangguan"),
    ("panjang", "kecil", "rendah", "tinggi", "gangguan"),
    ("panjang", "kecil", "tinggi", "rendah", "gangguan"),
    ("panjang", "kecil", "sedang", "rendah", "normal"),
    ("panjang", "besar", "tinggi", "tinggi", "normal"),
    ("panjang", "kecil", "sedang", "rendah", "gangguan"),
    ("pendek", "besar", "sedang", "tinggi", "normal"),
    ("panjang", "besar", "rendah", "tinggi", "normal"),
]
DATA = [dict(zip(FITUR + [TARGET], row)) for row in DATA_MENTAH]


def entropy(rows):
    counts = Counter(r[TARGET] for r in rows)
    return -sum((n / len(rows)) * log2(n / len(rows)) for n in counts.values())


def majority(rows):
    counts = Counter(r[TARGET] for r in rows)
    top = max(counts.values())
    candidates = [k for k, v in counts.items() if v == top]
    return "normal" if "normal" in candidates else sorted(candidates)[0]


def gain(rows, feature):
    remainder = sum(
        len(subset) / len(rows) * entropy(subset)
        for value in {r[feature] for r in rows}
        for subset in [[r for r in rows if r[feature] == value]]
    )
    return entropy(rows) - remainder, remainder


def build_tree(rows, features):
    if len({r[TARGET] for r in rows}) == 1:
        return rows[0][TARGET]
    if not features:
        return majority(rows)
    best = max(features, key=lambda f: gain(rows, f)[0])
    node = {"fitur": best, "default": majority(rows), "cabang": {}}
    for value in sorted({r[best] for r in rows}):
        subset = [r for r in rows if r[best] == value]
        node["cabang"][value] = build_tree(subset, [f for f in features if f != best])
    return node


def predict(tree, row):
    if isinstance(tree, str):
        return tree
    child = tree["cabang"].get(row[tree["fitur"]])
    return tree["default"] if child is None else predict(child, row)


def errors(tree, rows):
    return sum(predict(tree, r) != r[TARGET] for r in rows)


def prune(tree, rows):
    if isinstance(tree, str):
        return tree
    feature = tree["fitur"]
    for value, child in list(tree["cabang"].items()):
        subset = [r for r in rows if r[feature] == value]
        tree["cabang"][value] = prune(child, subset)
    label = majority(rows)
    leaf_error = sum(r[TARGET] != label for r in rows)
    return label if leaf_error <= errors(tree, rows) else tree


def print_tree(tree, indent=""):
    if isinstance(tree, str):
        print(indent + "=> " + tree.upper())
    else:
        print(indent + "[" + tree["fitur"].upper() + "]")
        for value, child in tree["cabang"].items():
            print(indent + f"  {tree['fitur']} = {value}")
            print_tree(child, indent + "    ")


def rules(tree, path=None):
    path = path or []
    if isinstance(tree, str):
        return [(path, tree)]
    result = []
    for value, child in tree["cabang"].items():
        result += rules(child, path + [f"{tree['fitur']}={value}"])
    return result


def report(title, tree):
    print(f"\n{title}")
    print_tree(tree)
    print("Rules:")
    for i, (path, label) in enumerate(rules(tree), 1):
        print(f"R{i}: IF {' AND '.join(path)} THEN {TARGET}={label}")
    e = errors(tree, DATA)
    print(f"Error = {e}/{len(DATA)} = {100*e/len(DATA):.2f}%")


def main():
    print("DECISION TREE: GANGGUAN LAYANAN SERVER")
    print(f"Entropy(S) = {entropy(DATA):.4f}")
    for feature in FITUR:
        g, rem = gain(DATA, feature)
        print(f"- {feature:10s}: entropy tertimbang={rem:.4f}, gain={g:.4f}")
    tree = build_tree(DATA, FITUR)
    report("POHON TANPA PRUNING", tree)
    report("POHON DENGAN PRUNING", prune(build_tree(DATA, FITUR), DATA))


def launch_gui():
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        main()
    tree = build_tree(DATA, FITUR)
    pruned = prune(build_tree(DATA, FITUR), DATA)

    root = tk.Tk()
    root.title("Decision Tree - Gangguan Layanan Server")
    root.geometry("920x650")
    root.minsize(720, 480)
    header = ttk.Frame(root, padding=12)
    header.pack(fill="x")
    ttk.Label(header, text="Decision Tree: Gangguan Layanan Server",
              font=("Segoe UI", 18, "bold")).pack(side="left")

    def export_csv():
        path = filedialog.asksaveasfilename(
            title="Simpan hasil prediksi", defaultextension=".csv",
            initialfile="hasil_gangguan_server.csv", filetypes=[("CSV", "*.csv")]
        )
        if not path:
            return
        fields = FITUR + [TARGET, "prediksi_tanpa_pruning", "prediksi_pruning", "hasil_pruning"]
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
