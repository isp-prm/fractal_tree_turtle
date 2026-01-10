from __future__ import annotations

import random
import turtle
from typing import Optional

from fractal.config import TreeConfig
from fractal.palette import get_palette


def _clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


class FractalTreeRenderer:
    # """
    # Рисует фрактальное дерево на переданном turtle.Turtle
    # """

    def __init__(self, t: turtle.Turtle) -> None:
        self.t = t

    def draw(self, cfg: TreeConfig) -> None:
        palette = get_palette(cfg.palette_name)

        # фон задаётся на уровне screen в UI, но если кто-то вызовет отдельно — ок
        # (screen может отсутствовать, тогда просто пропустим)
        try:
            scr = self.t.getscreen()
            scr.bgcolor(palette.background)
        except Exception:
            pass

        rnd = random.Random(cfg.seed)

        self.t.hideturtle()
        self.t.speed(0)
        self.t.penup()
        self.t.goto(0, -260)
        self.t.setheading(90)
        self.t.pendown()

        self._branch(
            depth=cfg.depth,
            length=cfg.trunk_length,
            thickness=cfg.thickness,
            cfg=cfg,
            rnd=rnd,
            trunk_color=palette.trunk_color,
        )

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

        # настройка пера
        self.t.pensize(max(1.0, thickness))

        # если дошли до листьев — рисуем "листья" другим цветом и останавливаем
        if depth <= 0 or length < 2:
            self.t.pencolor(rnd.choice(palette.leaf_colors))
            self.t.forward(max(1.0, length))
            self.t.backward(max(1.0, length))
            return

        # ствол/ветка
        self.t.pencolor(trunk_color)

        # случайность (angle/length jitter)
        # randomness=0 -> детерминировано
        jitter_angle = cfg.randomness * 10.0  # градусов
        jitter_len = cfg.randomness * 0.15    # доля длины

        actual_len = length * (1.0 + rnd.uniform(-jitter_len, jitter_len))
        actual_len = max(1.0, actual_len)

        self.t.forward(actual_len)

        base_angle = cfg.angle_deg
        left = base_angle + rnd.uniform(-jitter_angle, jitter_angle)
        right = base_angle + rnd.uniform(-jitter_angle, jitter_angle)

        next_len = actual_len * cfg.shrink
        next_th = thickness * cfg.thickness_decay
        next_th = _clamp(next_th, 0.5, 50)

        # левая ветвь
        self.t.left(left)
        self._branch(depth - 1, next_len, next_th, cfg, rnd, trunk_color)
        self.t.right(left)

        # правая ветвь
        self.t.right(right)
        self._branch(depth - 1, next_len, next_th, cfg, rnd, trunk_color)
        self.t.left(right)

        self.t.backward(actual_len)
