from __future__ import annotations

import math
import random
import turtle
from dataclasses import dataclass
from typing import Tuple

from fractal.config import TreeConfig
from fractal.palette import get_palette


def _clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


@dataclass
class BBox:
    minx: float
    miny: float
    maxx: float
    maxy: float

    def expand(self, x: float, y: float) -> None:
        self.minx = min(self.minx, x)
        self.miny = min(self.miny, y)
        self.maxx = max(self.maxx, x)
        self.maxy = max(self.maxy, y)

    def pad(self, p: float) -> "BBox":
        return BBox(self.minx - p, self.miny - p, self.maxx + p, self.maxy + p)

    @property
    def w(self) -> float:
        return max(1e-9, self.maxx - self.minx)

    @property
    def h(self) -> float:
        return max(1e-9, self.maxy - self.miny)


def estimate_tree_bbox(cfg: TreeConfig) -> BBox:
    """
    Считает bbox дерева в “математических” координатах (в тех же, в которых будем рисовать),
    чтобы затем подогнать worldcoordinates под canvas и гарантировать, что всё влезет.
    """
    rnd = random.Random(cfg.seed)

    # старт: (0,0), смотрим вверх (90°)
    x, y = 0.0, 0.0
    heading = 90.0

    bbox = BBox(x, y, x, y)

    def jitter_params(length: float) -> Tuple[float, float, float]:
        jitter_angle = cfg.randomness * 10.0  # градусов
        jitter_len = cfg.randomness * 0.15    # доля длины
        actual_len = length * (1.0 + rnd.uniform(-jitter_len, jitter_len))
        actual_len = max(1.0, actual_len)
        left = cfg.angle_deg + rnd.uniform(-jitter_angle, jitter_angle)
        right = cfg.angle_deg + rnd.uniform(-jitter_angle, jitter_angle)
        return actual_len, left, right

    def branch(depth: int, length: float, thickness: float, x: float, y: float, heading: float) -> Tuple[float, float]:
        # Для square режима учитываем “размер квадрата” вокруг точки stamp.
        # Базовый размер shape “square” у turtle = 20px. Мы масштабируем shapesize по thickness.
        # half_side ≈ 10 * scale
        scale = max(0.15, thickness / 10.0)
        half_side = 10.0 * scale if cfg.draw_mode == "square" else 0.0

        # обновим bbox по текущей позиции (с учетом квадрата)
        bbox.expand(x - half_side, y - half_side)
        bbox.expand(x + half_side, y + half_side)

        if depth <= 0 or length < 2:
            # лист: forward/backward в линии или stamp в квадратах.
            # Для bbox достаточно учесть конечную точку forward.
            lx = x + math.cos(math.radians(heading)) * max(1.0, length)
            ly = y + math.sin(math.radians(heading)) * max(1.0, length)
            bbox.expand(lx - half_side, ly - half_side)
            bbox.expand(lx + half_side, ly + half_side)
            return x, y  # возвращаемся назад

        actual_len, left, right = jitter_params(length)

        nx = x + math.cos(math.radians(heading)) * actual_len
        ny = y + math.sin(math.radians(heading)) * actual_len

        # bbox конечной точки (и квадратов по пути мы здесь не моделируем детально,
        # но конечная точка + старт обычно достаточно; запас дадим padding’ом в UI)
        bbox.expand(nx - half_side, ny - half_side)
        bbox.expand(nx + half_side, ny + half_side)

        next_len = actual_len * cfg.shrink
        next_th = _clamp(thickness * cfg.thickness_decay, 0.5, 50)

        # левая
        branch(depth - 1, next_len, next_th, nx, ny, heading + left)
        # правая
        branch(depth - 1, next_len, next_th, nx, ny, heading - right)

        return x, y

    branch(cfg.depth, cfg.trunk_length, cfg.thickness, x, y, heading)
    return bbox


class FractalTreeRenderer:
    """
    Рисует фрактальное дерево на переданном turtle.Turtle
    """

    def __init__(self, t: turtle.Turtle) -> None:
        self.t = t

    def draw(self, cfg: TreeConfig) -> None:
        palette = get_palette(cfg.palette_name)

        try:
            scr = self.t.getscreen()
            scr.bgcolor(palette.background)
        except Exception:
            pass

        rnd = random.Random(cfg.seed)

        self.t.hideturtle()
        self.t.speed(0)

        # стартовая позиция — (0,0), вверх
        self.t.penup()
        self.t.goto(0, 0)
        self.t.setheading(90)

        if cfg.draw_mode == "square":
            self.t.shape("square")
            self.t.penup()  # stamps, без линии
        else:
            self.t.pendown()

        self._branch(
            depth=cfg.depth,
            length=cfg.trunk_length,
            thickness=cfg.thickness,
            cfg=cfg,
            rnd=rnd,
            trunk_color=palette.trunk_color,
        )

    def _stamp_square(self, thickness: float) -> None:
        # turtle square базовый 20x20; масштабируем под толщину
        scale = max(0.15, thickness / 10.0)
        self.t.shapesize(stretch_wid=scale, stretch_len=scale, outline=1)

        # штамп в текущей точке
        self.t.stamp()

    def _forward_with_squares(self, dist: float, thickness: float) -> None:
        """
        Двигаемся вперёд, оставляя квадраты вдоль ветви.
        """
        step = max(4.0, thickness * 0.9)
        remaining = dist

        # stamp в начале
        self._stamp_square(thickness)

        while remaining > 0:
            d = min(step, remaining)
            self.t.forward(d)
            self._stamp_square(thickness)
            remaining -= d

    def _branch(
        self,
        depth: int,
        length: float,
        thickness: float,
        cfg: TreeConfig,
        rnd: random.Random,
        trunk_color: str,
    ) -> None:
        palette = get_palette(cfg.palette_name)

        # случайность
        jitter_angle = cfg.randomness * 10.0
        jitter_len = cfg.randomness * 0.15

        actual_len = length * (1.0 + rnd.uniform(-jitter_len, jitter_len))
        actual_len = max(1.0, actual_len)

        base_angle = cfg.angle_deg
        left = base_angle + rnd.uniform(-jitter_angle, jitter_angle)
        right = base_angle + rnd.uniform(-jitter_angle, jitter_angle)

        # листья
        if depth <= 0 or length < 2:
            self.t.pencolor(rnd.choice(palette.leaf_colors))
            if cfg.draw_mode == "square":
                self._forward_with_squares(max(1.0, actual_len), max(1.0, thickness * 0.7))
                # вернуться назад
                self.t.backward(max(1.0, actual_len))
            else:
                self.t.pensize(max(1.0, thickness))
                self.t.pendown()
                self.t.forward(max(1.0, actual_len))
                self.t.backward(max(1.0, actual_len))
            return

        # ствол/ветка
        self.t.pencolor(trunk_color)

        if cfg.draw_mode == "square":
            self._forward_with_squares(actual_len, thickness)
        else:
            self.t.pensize(max(1.0, thickness))
            self.t.pendown()
            self.t.forward(actual_len)

        next_len = actual_len * cfg.shrink
        next_th = _clamp(thickness * cfg.thickness_decay, 0.5, 50)

        # левая ветвь
        self.t.left(left)
        self._branch(depth - 1, next_len, next_th, cfg, rnd, trunk_color)
        self.t.right(left)

        # правая ветвь
        self.t.right(right)
        self._branch(depth - 1, next_len, next_th, cfg, rnd, trunk_color)
        self.t.left(right)

        # назад
        self.t.backward(actual_len)
