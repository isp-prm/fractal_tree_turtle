from dataclasses import dataclass

@dataclass(frozen=True)
class TreeConfig:
    depth: int = 10

    # геометрия
    angle_deg: float = 25.0
    trunk_length: float = 120.0
    shrink: float = 0.72  # во сколько раз уменьшается длина ветви на каждом уровне

    # стиль линии
    thickness: float = 10.0
    thickness_decay: float = 0.75  # во сколько раз уменьшается толщина на каждом уровне

    # случайность (0..1)
    randomness: float = 0.0
    seed: int = 0

    # палитра
    palette_name: str = "Classic"
    background: str = "#0b1020"
