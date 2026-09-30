import random

import glfw

from engine.camera import Camera2D
from engine.collision import intersects
from engine.ecs.component_registry import ComponentRegistry
from engine.ecs.components.quad_renderable import QuadRenderable
from engine.ecs.components.transform import Transform
from engine.ecs.components.velocity import Velocity
from engine.key import Key
from engine.scene_loader import SceneLoader
from engine.vector2 import Vector2

from .components import BallSpawnTag, LeftPlayerTag, RightPlayerTag


# UP/DOWN already exist in the engine's key enum; Pong supplies their window
# mapping locally so no engine source file has to be changed.
from engine.window import KEY_MAP
KEY_MAP[Key.UP] = glfw.KEY_UP
KEY_MAP[Key.DOWN] = glfw.KEY_DOWN


class Game:
    PADDLE_SPEED = 360.0
    BALL_SPEED = 330.0
    WINNING_SCORE = 5

    def __init__(self, width, height):
        self.viewport_width = width
        self.viewport_height = height
        self.world_width = width
        self.world_height = height
        self.left_score = 0
        self.right_score = 0
        self.game_over = False
        self.winner = None
        self.round_started = False
        self._raw_previous = set()
        self._dynamic_ui = []

        registry = ComponentRegistry()
        registry.register("LeftPlayer", lambda data: LeftPlayerTag())
        registry.register("RightPlayer", lambda data: RightPlayerTag())
        registry.register("BallSpawn", lambda data: BallSpawnTag())
        self.scene_loader = SceneLoader(registry)
        self.scene = self.scene_loader.load("game/pong/assets/scenes/main.json")
        self.world = self.scene.world
        self.camera = Camera2D()

        self.left = list(self.world.query(LeftPlayerTag, Transform))[0][2]
        self.right = list(self.world.query(RightPlayerTag, Transform))[0][2]
        _, _, self.ball, self.ball_velocity = list(self.world.query(BallSpawnTag, Transform, Velocity))[0]
        self._build_static_ui()
        self._refresh_ui()

    def update(self, dt, input):
        raw_keys = self._raw_keys(input)
        just_pressed = raw_keys - self._raw_previous
        self._raw_previous = raw_keys

        if self.game_over:
            if "R" in just_pressed:
                self._restart_match()
            elif "ESC" in just_pressed or "Q" in just_pressed:
                self._quit(input)
            return

        self._move_paddles(dt, input)
        if not self.round_started:
            if input.was_key_pressed(Key.SPACE):
                self._launch_ball()
            return
        self._move_ball(min(dt, 0.05))

    def render(self, renderer, resources):
        from engine.ecs.systems.quad_render import quad_render_system
        quad_render_system(self.world, renderer, resources)

    def _move_paddles(self, dt, input):
        left_direction = (1 if input.is_key_down(Key.S) else 0) - (1 if input.is_key_down(Key.W) else 0)
        right_direction = (1 if input.is_key_down(Key.DOWN) else 0) - (1 if input.is_key_down(Key.UP) else 0)
        self.left.position.y += left_direction * self.PADDLE_SPEED * dt
        self.right.position.y += right_direction * self.PADDLE_SPEED * dt
        self._clamp_paddle(self.left)
        self._clamp_paddle(self.right)

    def _clamp_paddle(self, paddle):
        half = paddle.scale.y * 0.5
        paddle.position.y = max(half, min(self.world_height - half, paddle.position.y))

    def _launch_ball(self):
        direction = Vector2(random.choice((-1.0, 1.0)), random.uniform(-0.75, 0.75)).normalized()
        self.ball_velocity.value = direction * self.BALL_SPEED
        self.round_started = True

    def _move_ball(self, dt):
        velocity = self.ball_velocity.value
        self.ball.position.x += velocity.x * dt
        self.ball.position.y += velocity.y * dt
        half = self.ball.scale.y * 0.5
        if self.ball.position.y <= half:
            self.ball.position.y = half
            velocity.y = abs(velocity.y)
        elif self.ball.position.y >= self.world_height - half:
            self.ball.position.y = self.world_height - half
            velocity.y = -abs(velocity.y)

        if velocity.x < 0 and intersects(self.ball, self.left):
            self.ball.position.x = self.left.position.x + self.left.scale.x * 0.5 + self.ball.scale.x * 0.5
            velocity.x = abs(velocity.x)
            self._add_spin(self.left)
        elif velocity.x > 0 and intersects(self.ball, self.right):
            self.ball.position.x = self.right.position.x - self.right.scale.x * 0.5 - self.ball.scale.x * 0.5
            velocity.x = -abs(velocity.x)
            self._add_spin(self.right)

        if self.ball.position.x < -self.ball.scale.x:
            self._score(right=True)
        elif self.ball.position.x > self.world_width + self.ball.scale.x:
            self._score(right=False)

    def _add_spin(self, paddle):
        offset = (self.ball.position.y - paddle.position.y) / (paddle.scale.y * 0.5)
        self.ball_velocity.value.y += offset * 70.0
        self.ball_velocity.value = self.ball_velocity.value.normalized() * self.BALL_SPEED

    def _score(self, right):
        if right:
            self.right_score += 1
        else:
            self.left_score += 1
        self._reset_round()
        if self.left_score >= self.WINNING_SCORE or self.right_score >= self.WINNING_SCORE:
            self.game_over = True
            self.winner = "LINKS" if self.left_score > self.right_score else "RECHTS"
        self._refresh_ui()

    def _reset_round(self):
        self.ball.position = Vector2(self.world_width * 0.5, self.world_height * 0.5)
        self.ball_velocity.value = Vector2()
        self.round_started = False

    def _restart_match(self):
        self.left_score = self.right_score = 0
        self.game_over = False
        self.winner = None
        self._reset_round()
        self._refresh_ui()

    def _raw_keys(self, input):
        window = getattr(getattr(input, "window", None), "window", None)
        if window is None:
            return set()
        keys = {"R": glfw.KEY_R, "Q": glfw.KEY_Q, "ESC": glfw.KEY_ESCAPE}
        return {name for name, key in keys.items() if glfw.get_key(window, key) == glfw.PRESS}

    def _quit(self, input):
        window = getattr(getattr(input, "window", None), "window", None)
        if window is not None:
            glfw.set_window_should_close(window, True)

    def _new_quad(self, position, scale, color, z_index=0):
        entity = self.world.create_entity()
        self.world.add_component(entity, Transform(position=Vector2(*position), scale=Vector2(*scale)))
        self.world.add_component(entity, QuadRenderable(color=color, z_index=z_index))
        return entity

    def _build_static_ui(self):
        for y in range(35, self.world_height - 35, 34):
            self._new_quad((self.world_width * 0.5, y), (4, 18), (0.35, 0.42, 0.48, 1), -1)
        for x in range(0, int(self.world_width), 32):
            self._new_quad((x + 16, 15), (18, 3), (0.2, 0.28, 0.34, 1), -1)
            self._new_quad((x + 16, self.world_height - 15), (18, 3), (0.2, 0.28, 0.34, 1), -1)

    def _refresh_ui(self):
        for entity in self._dynamic_ui:
            self.world.destroy_entity(entity)
        self._dynamic_ui = []
        self._draw_digit(self.left_score, self.world_width * 0.5 - 90, 62)
        self._draw_digit(self.right_score, self.world_width * 0.5 + 90, 62)
        if self.game_over:
            self._draw_text(self.winner, self.world_width * 0.5, 250, 5, (1.0, 0.85, 0.25, 1))
            self._draw_text("R NEUSTART", self.world_width * 0.5, 335, 3, (0.85, 0.92, 1.0, 1))
            self._draw_text("ESC BEENDEN", self.world_width * 0.5, 375, 3, (0.85, 0.92, 1.0, 1))
        elif not self.round_started and self.left_score == 0 and self.right_score == 0:
            self._draw_text("SPACE START", self.world_width * 0.5, self.world_height - 45, 3, (0.55, 0.7, 0.8, 1))

    def _draw_digit(self, digit, center_x, top):
        segments = {0: "abcdef", 1: "bc", 2: "abdeg", 3: "abcdg", 4: "bcfg", 5: "acdfg", 6: "acdefg", 7: "abc", 8: "abcdefg", 9: "abcdfg"}[digit]
        positions = {"a": (0, 0, 24, 5), "b": (19, 5, 5, 24), "c": (19, 34, 5, 24), "d": (0, 58, 24, 5), "e": (0, 34, 5, 24), "f": (0, 5, 5, 24), "g": (0, 29, 24, 5)}
        for segment in segments:
            x, y, w, h = positions[segment]
            self._dynamic_ui.append(self._new_quad((center_x - 12 + x, top + y), (w, h), (0.3, 0.9, 1.0, 1), 2))

    def _draw_text(self, text, center_x, top, scale, color):
        patterns = {
            "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"], "C": ["01111", "10000", "10000", "10000", "10000", "10000", "01111"], "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"], "H": ["10001", "10001", "10001", "11111", "10001", "10001", "10001"], "D": ["11110", "10001", "10001", "10001", "10001", "10001", "11110"], "N": ["10001", "11001", "10101", "10011", "10001", "10001", "10001"], "R": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"], "T": ["11111", "00100", "00100", "00100", "00100", "00100", "00100"], "U": ["10001", "10001", "10001", "10001", "10001", "10001", "01110"], "S": ["01111", "10000", "10000", "01110", "00001", "00001", "11110"], "L": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"], "K": ["10001", "10010", "10100", "11000", "10100", "10010", "10001"], "I": ["11111", "00100", "00100", "00100", "00100", "00100", "11111"], "P": ["11110", "10001", "10001", "11110", "10000", "10000", "10000"], " ": ["000", "000", "000", "000", "000", "000", "000"]}
        spacing = scale * 2
        width = sum((5 if char != " " else 3) * scale + spacing for char in text) - spacing
        cursor = center_x - width * 0.5
        for char in text:
            pattern = patterns.get(char, patterns[" "])
            for row, line in enumerate(pattern):
                for col, pixel in enumerate(line):
                    if pixel == "1":
                        self._dynamic_ui.append(self._new_quad((cursor + col * scale, top + row * scale), (scale, scale), color, 3))
            cursor += (5 if char != " " else 3) * scale + spacing
