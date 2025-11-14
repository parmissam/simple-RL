from __future__ import annotations

import json
import random
from typing import Dict, Literal


actions: tuple[
    Literal["up", "down", "left", "right", "left up", "right up", "left down", "right down"],
    ...
] = ("up", "down", "left", "right", "left up", "right up", "left down", "right down")


def get_state(
        player_pos: list[int], 
        grid_size: int , 
        cell_size: int
) -> int:
    x = player_pos[0] // cell_size
    y = player_pos[1] // cell_size
    return int(y) * grid_size + int(x)


def choose_action(
    state: int,
    q_table: Dict[int, Dict[str, float]],
    epsilon: float,
) -> Literal["up", "down", "left", "right", "left up", "right up", "left down", "right down"]:
    if state not in q_table:  
        q_table[state] = {a: 0.0 for a in actions}
    if epsilon > random.random():
        return random.choice(list(actions))
    return max(q_table[state], key=q_table[state].get) 


def load_q_table(filename: str) -> Dict[int, Dict[str, float]]:

    try:
        with open(filename, "r", encoding="utf-8") as f:
            raw = json.load(f)
    except FileNotFoundError:
        return {}
    fixed: Dict[int, Dict[str, float]] = {}
    for k, v in raw.items():
        try:
            ik = int(k)
        except (TypeError, ValueError):
            continue
        fixed[ik] = {str(a): float(vv) for a, vv in v.items()}
    return fixed


def save_q_table(q_table: Dict[int, Dict[str, float]], filename: str = "q_table.json") -> None:
    serializable = {str(k): v for k, v in q_table.items()}
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(serializable, f, ensure_ascii=False, indent=2)
