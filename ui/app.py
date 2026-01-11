from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import turtle

from fractal.config import TreeConfig
from fractal.tree import FractalTreeRenderer, estimate_tree_bbox
from fractal.palette import list_palette_names, get_palette


class FractalTreeApp:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Fractal Tree — turtle")
        self.root.geometry("980x640")
        self.root.minsize(900, 600)

        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)

        self.controls = ttk.Frame(self.root, padding=(14, 14))
        self.controls.grid(row=0, column=0, sticky="ns")

        self.canvas_frame = ttk.Frame(self.root, padding=(10, 10))
        self.canvas_frame.grid(row=0, column=1, sticky="nsew")
        self.canvas_frame.rowconfigure(0, weight=1)
        self.canvas_frame.columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(self.canvas_frame, highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        self.screen = turtle.TurtleScreen(self.canvas)
        self.screen.tracer(0, 0)
        self.t = turtle.RawTurtle(self.screen)

        self.renderer = FractalTreeRenderer(self.t)

        self._build_controls()
        self._apply_theme()

        pal = get_palette(self.palette_var.get())
        self.screen.bgcolor(pal.background)

        self.root.bind("<Return>", lambda e: self.on_draw())
        self.root.bind("<Escape>", lambda e: self.on_clear())

    def run(self) -> None:
        self.root.mainloop()

    # ---------------- UI ----------------

    def _build_controls(self) -> None:
        ttk.Label(self.controls, text="Fractal Tree", font=("Helvetica", 16, "bold")).grid(
            row=0, column=0, sticky="w", pady=(0, 10)
        )

        self.depth_var = tk.IntVar(value=10)
        self.angle_var = tk.DoubleVar(value=25.0)
        self.length_var = tk.DoubleVar(value=120.0)
        self.shrink_var = tk.DoubleVar(value=0.72)

        self.thickness_var = tk.DoubleVar(value=10.0)
        self.th_decay_var = tk.DoubleVar(value=0.75)

        self.random_var = tk.DoubleVar(value=0.0)
        self.seed_var = tk.IntVar(value=0)

        self.palette_var = tk.StringVar(value="Classic")

        # NEW: режим рисования
        self.draw_mode_var = tk.StringVar(value="line")  # "line" | "square"

        row = 1
        row = self._add_spin(self.controls, "Depth", self.depth_var, 1, 16, row)
        row = self._add_scale(self.controls, "Angle", self.angle_var, 5, 60, row, step=1)
        row = self._add_scale(self.controls, "Length", self.length_var, 40, 220, row, step=1)
        row = self._add_scale(self.controls, "Shrink", self.shrink_var, 0.55, 0.85, row, step=0.01)

        ttk.Separator(self.controls).grid(row=row, column=0, sticky="ew", pady=10)
        row += 1

        row = self._add_scale(self.controls, "Thickness", self.thickness_var, 1, 20, row, step=1)
        row = self._add_scale(self.controls, "Th. decay", self.th_decay_var, 0.55, 0.9, row, step=0.01)

        ttk.Separator(self.controls).grid(row=row, column=0, sticky="ew", pady=10)
        row += 1

        row = self._add_scale(self.controls, "Randomness", self.random_var, 0.0, 1.0, row, step=0.05)
        row = self._add_spin(self.controls, "Seed", self.seed_var, 0, 999999, row)

        # NEW: Radiobutton выбор фигуры
        ttk.Label(self.controls, text="Stroke").grid(row=row, column=0, sticky="w")
        row += 1
        rb = ttk.Frame(self.controls)
        rb.grid(row=row, column=0, sticky="w", pady=(2, 10))

        ttk.Radiobutton(rb, text="Line", value="line", variable=self.draw_mode_var).grid(row=0, column=0, padx=(0, 10))
        ttk.Radiobutton(rb, text="Squares", value="square", variable=self.draw_mode_var).grid(row=0, column=1)
        row += 1

        ttk.Label(self.controls, text="Palette").grid(row=row, column=0, sticky="w")
        row += 1
        self.palette_combo = ttk.Combobox(
            self.controls,
            textvariable=self.palette_var,
            values=list_palette_names(),
            state="readonly",
            width=18,
        )
        self.palette_combo.grid(row=row, column=0, sticky="ew", pady=(2, 10))
        self.palette_combo.bind("<<ComboboxSelected>>", lambda e: self._on_palette_change())
        row += 1

        btns = ttk.Frame(self.controls)
        btns.grid(row=row, column=0, sticky="ew")
        btns.columnconfigure(0, weight=1)
        btns.columnconfigure(1, weight=1)

        ttk.Button(btns, text="Draw", command=self.on_draw).grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ttk.Button(btns, text="Clear", command=self.on_clear).grid(row=0, column=1, sticky="ew", padx=(6, 0))

        row += 1
        ttk.Button(self.controls, text="Save PostScript", command=self.on_save_ps).grid(
            row=row, column=0, sticky="ew", pady=(10, 0)
        )

        row += 1
        hint = (
            "Enter — Draw\n"
            "Esc — Clear\n\n"

        )
        ttk.Label(self.controls, text=hint, justify="left").grid(row=row, column=0, sticky="w", pady=(14, 0))

        for i in range(row + 1):
            self.controls.rowconfigure(i, pad=2)

    def _apply_theme(self) -> None:
        style = ttk.Style()
        try:
            style.theme_use("aqua")
        except Exception:
            pass

    def _add_scale(
        self,
        parent: ttk.Frame,
        label: str,
        var: tk.DoubleVar,
        frm: float,
        to: float,
        row: int,
        step: float,
    ) -> int:
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w")
        row += 1

        line = ttk.Frame(parent)
        line.grid(row=row, column=0, sticky="ew")
        line.columnconfigure(0, weight=1)

        scale = ttk.Scale(line, variable=var, from_=frm, to=to, orient="horizontal")
        scale.grid(row=0, column=0, sticky="ew")

        val = ttk.Label(line, width=7, anchor="e")
        val.grid(row=0, column=1, padx=(8, 0))

        def update_label(*_):
            v = float(var.get())
            if step >= 1:
                v = round(v)
            else:
                v = round(v / step) * step
                v = round(v, 2)
            val.configure(text=str(v))
        var.trace_add("write", update_label)
        update_label()

        row += 1
        return row

    def _add_spin(
        self,
        parent: ttk.Frame,
        label: str,
        var: tk.IntVar,
        frm: int,
        to: int,
        row: int,
    ) -> int:
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w")
        row += 1
        spin = ttk.Spinbox(parent, textvariable=var, from_=frm, to=to, width=8)
        spin.grid(row=row, column=0, sticky="w", pady=(2, 10))
        row += 1
        return row

    # ---------------- helpers ----------------

    def _make_config(self) -> TreeConfig:
        pal = get_palette(self.palette_var.get())
        return TreeConfig(
            depth=int(self.depth_var.get()),
            angle_deg=float(self.angle_var.get()),
            trunk_length=float(self.length_var.get()),
            shrink=float(self.shrink_var.get()),
            thickness=float(self.thickness_var.get()),
            thickness_decay=float(self.th_decay_var.get()),
            randomness=float(self.random_var.get()),
            seed=int(self.seed_var.get()),
            palette_name=str(self.palette_var.get()),
            background=pal.background,
            draw_mode=str(self.draw_mode_var.get()),
        )

    def _fit_world_to_bbox(self, bbox, margin_px: float = 24.0) -> None:

        # обновим геометрию окна, чтобы winfo_width/height были актуальными
        self.root.update_idletasks()

        cw = max(1, int(self.canvas.winfo_width()))
        ch = max(1, int(self.canvas.winfo_height()))
        canvas_aspect = cw / ch

        # bbox с запасом
        padded = bbox.pad(margin_px)

        # приводим bbox к аспекту canvas: расширяем по нужной оси, чтобы не обрезало
        bb_aspect = padded.w / padded.h
        cx = (padded.minx + padded.maxx) / 2.0
        cy = (padded.miny + padded.maxy) / 2.0

        if bb_aspect > canvas_aspect:
            # bbox “шире”, расширяем по высоте
            new_h = padded.w / canvas_aspect
            half_h = new_h / 2.0
            llx, urx = padded.minx, padded.maxx
            lly, ury = cy - half_h, cy + half_h
        else:
            # bbox “выше”, расширяем по ширине
            new_w = padded.h * canvas_aspect
            half_w = new_w / 2.0
            lly, ury = padded.miny, padded.maxy
            llx, urx = cx - half_w, cx + half_w

        self.screen.setworldcoordinates(llx, lly, urx, ury)

    # ---------------- actions ----------------

    def on_draw(self) -> None:
        cfg = self._make_config()

        if cfg.depth < 0 or cfg.depth > 18:
            messagebox.showerror("Invalid depth", "Depth должен быть в пределах 0..18")
            return
        if not (0.3 <= cfg.shrink <= 0.95):
            messagebox.showerror("Invalid shrink", "Shrink должен быть в пределах 0.3..0.95")
            return

        pal = get_palette(cfg.palette_name)
        self.screen.bgcolor(pal.background)

        # NEW: считаем bbox и подгоняем worldcoordinates => дерево всегда влезает и центрируется
        bbox = estimate_tree_bbox(cfg)
        self._fit_world_to_bbox(bbox, margin_px=30.0)

        self.t.clear()
        self.t.penup()
        self.t.home()
        self.t.pendown()

        self.renderer.draw(cfg)
        self.screen.update()

    def on_clear(self) -> None:
        self.t.clear()
        self.screen.update()

    def _on_palette_change(self) -> None:
        pal = get_palette(self.palette_var.get())
        self.screen.bgcolor(pal.background)
        self.screen.update()

    def on_save_ps(self) -> None:
        path = filedialog.asksaveasfilename(
            defaultextension=".ps",
            filetypes=[("PostScript", "*.ps")],
            title="Save as PostScript",
        )
        if not path:
            return
        try:
            self.canvas.postscript(file=path, colormode="color")
            messagebox.showinfo("Saved", f"Saved:\n{path}\n\nМожно открыть в Preview и экспортировать в PNG.")
        except Exception as e:
            messagebox.showerror("Save error", str(e))
