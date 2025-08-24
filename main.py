from __future__ import annotations

import random
from typing import Dict, Literal

import pygame
from rl_config import get_state, choose_action, save_q_table, load_q_table, actions

Action = Literal["up", "down", "left", "right"]


class Game:
    def __init__(
        self,
        goal: int,
        start: int,
        gui: bool,
        episodes: int,
        q_table: Dict[int, Dict[Action, float]] | None = None,
    ) -> None:
        pygame.init()
        self.gui = gui
        self.goal = goal
        self.start = start
        self.alldistance = [0]
        self.episodes = episodes
        self.q_table: Dict[int, Dict[Action, float]] = q_table if q_table is not None else {}
        self.cell_size = cell_size
        self.grid_size = grid_size
        self.width = self.height = self.grid_size * self.cell_size

        goal_col = self.goal % self.grid_size
        goal_row = self.goal // self.grid_size
        self.goal_pos = [
            goal_col * self.cell_size + self.cell_size // 2,
            goal_row * self.cell_size + self.cell_size // 2,
        ]

        start_col = self.start % self.grid_size
        start_row = self.start // self.grid_size
        self.start_pos = [
            start_col * self.cell_size + self.cell_size // 2,
            start_row * self.cell_size + self.cell_size // 2,
        ]

        self.player_pos = [self.start_pos[0], self.start_pos[1]]
        self.penalty = False

    def initialize_gui(self) -> None:
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("My Game")
        self.clock = pygame.time.Clock()
        self.running = True
        self.bg = (255, 255, 255)
        self.line = (180, 180, 180)

    def draw_grid(self) -> None:
        for x in range(0, self.width + 1, self.cell_size):
            pygame.draw.line(self.screen, self.line, (x, 0), (x, self.height), 1)
        for y in range(0, self.height + 1, self.cell_size):
            pygame.draw.line(self.screen, self.line, (0, y), (self.width, y), 1)

    def move_player(self, action: Action) -> None:
        if action == "up":
            self.player_pos[1] -= self.cell_size
        elif action == "down":
            self.player_pos[1] += self.cell_size
        elif action == "left":
            self.player_pos[0] -= self.cell_size
        elif action == "right":
            self.player_pos[0] += self.cell_size
        elif action == "left up":
            self.player_pos[0] -= self.cell_size
            self.player_pos[1] -= self.cell_size
        elif action == "left down":
            self.player_pos[0] -= self.cell_size
            self.player_pos[1] += self.cell_size
        elif action == "right up":
            self.player_pos[0] += self.cell_size
            self.player_pos[1] -= self.cell_size
        elif action == "right down":
            self.player_pos[0] += self.cell_size
            self.player_pos[1] += self.cell_size

        min_c = self.cell_size // 2
        max_x = self.width - min_c
        max_y = self.height - min_c

        if self.player_pos[0] < min_c:
            self.player_pos[0] = min_c
            self.penalty = True
        if self.player_pos[0] > max_x:
            self.player_pos[0] = max_x
            self.penalty = True
        if self.player_pos[1] < min_c:
            self.player_pos[1] = min_c
            self.penalty = True
        if self.player_pos[1] > max_y:
            self.player_pos[1] = max_y
            self.penalty = True

    def run(self) -> None:
        if self.gui:
            self.initialize_gui()
        for episode in range(self.episodes):
            self.player_pos = [self.start_pos[0], self.start_pos[1]]
            self.alldistance = [10**9]  
            self.penalty = False
            done = False

            while not done:
                if self.gui:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            self.running = False
                            done = True
                            break
                    if not getattr(self, "running", True):  
                        return

                state = get_state(self.player_pos, self.grid_size, self.cell_size)
                if state not in self.q_table:
                    self.q_table[state] = {a: 0.0 for a in actions}
                if episode == episodes - 1:
                    epsilon = 0.0  
                    print(f"Episode {episode}, State: {state}, Action: {action}, Reward: {reward}, numberofsteps:{len(self.alldistance)-1}")
                else:
                    epsilon = 0.2
                action = choose_action(state, self.q_table, epsilon)
                self.move_player(action)

                dx = abs(self.goal_pos[0] - self.player_pos[0])
                dy = abs(self.goal_pos[1] - self.player_pos[1])
                distance = dx + dy
                self.alldistance.append(distance)

                reward = -0.1
                if self.alldistance[-1] < self.alldistance[-2]:
                    reward += 2.0
                else:
                    reward -= 0.1

                if self.penalty:
                    reward = -5.0
                    self.penalty = False

                next_state = get_state(self.player_pos, self.grid_size, self.cell_size)
                if next_state not in self.q_table:
                    self.q_table[next_state] = {a: 0.0 for a in actions}

                if next_state == self.goal:
                    reward = 100.0
                    print("Reached destination!!")
                    done = True

                old_value = self.q_table[state][action]
                next_max = max(self.q_table[next_state].values())
                self.q_table[state][action] = (1 - 0.1) * old_value + 0.1 * (reward + 0.9 * next_max)

                if episode == self.episodes - 1 or self.gui:
                    self.screen.fill(self.bg)
                    self.draw_grid()
                    pygame.draw.circle(self.screen, (0, 0, 255), (self.player_pos[0], self.player_pos[1]), 20)
                    pygame.draw.circle(self.screen, (0, 255, 255), (self.goal_pos[0], self.goal_pos[1]), 10)
                    pygame.draw.circle(self.screen, (255, 0, 0), (self.start_pos[0], self.start_pos[1]), 10)
                    pygame.display.flip()
                    self.clock.tick(10)
                
                if episode == episodes-2:
                    self.initialize_gui()

        pygame.quit()


if __name__ == "__main__":
    grid_size = 16
    cell_size = 50

    goal = random.randint(0, grid_size * grid_size - 1)
    start = random.randint(0, grid_size * grid_size - 1)
    while start == goal:
        start = random.randint(0, grid_size * grid_size - 1)

    episodes = 10
    gui = True

    q_table = load_q_table("q_table.json")

    game = Game(goal, start, gui=gui, episodes=episodes, q_table=q_table)
    game.run()

    save_q_table(game.q_table, "q_table.json")
