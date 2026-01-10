from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass(frozen=True)
class Palette:
    name: str
    trunk_color: str
    leaf_colors: List[str]
    background: str


PALETTES: Dict[str, Palette] = {
    "Classic": Palette(
        name="Classic",
        trunk_color="#8b5a2b",
        leaf_colors=["#2ecc71", "#27ae60", "#1abc9c"],
        background="#0b1020",
    ),
    "Sakura": Palette(
        name="Sakura",
        trunk_color="#6d4c41",
        leaf_colors=["#ffb7c5", "#ffd1dc", "#ffc0cb"],
        background="#0f0f14",
    ),
    "Winter": Palette(
        name="Winter",
        trunk_color="#7f8c8d",
        leaf_colors=["#ecf0f1", "#dfe6e9", "#bdc3c7"],
        background="#0b1220",
    ),
    "Neon": Palette(
        name="Neon",
        trunk_color="#9b59b6",
        leaf_colors=["#00f5ff", "#00ff85", "#ffe600"],
        background="#05050a",
    ),
}


def list_palette_names() -> List[str]:
    return list(PALETTES.keys())


def get_palette(name: str) -> Palette:
    return PALETTES.get(name, PALETTES["Classic"])
