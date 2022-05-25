#! /usr/bin/env python3
# Carson Carpenter
# CPSC 386-02
# 2022-04-24
# carson.carpenter7@csu.fullerton.edu
# @carsoncarpenter7
#
# Lab 05-00
#
# This my Pygame game program with of bouncing balls
#

"""Scene objects for making games with PyGame."""

# from random import randint
import pygame
from more_itertools import grouper
from game import rgbcolors
from game.ball import Ball
# from game.animation import Explosion


class Scene:
    """Base class for making PyGame Scenes."""

    def __init__(self, screen, background_color, soundtrack=None):
        """Scene initializer"""
        self._screen = screen
        self._background = pygame.Surface(self._screen.get_size())
        self._background.fill(background_color)
        self._frame_rate = 60
        self._is_valid = True
        self._soundtrack = soundtrack
        self._render_updates = None

    def draw(self):
        """Draw the scene."""
        self._screen.blit(self._background, (0, 0))

    def process_event(self, event):
        """Process a game event by the scene."""
        # This should be commented out or removed since it generates a lot of noise.
        # print(str(event))
        if event.type == pygame.QUIT:
            print("Good Bye!")
            self._is_valid = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            print("Bye bye!")
            self._is_valid = False

    def is_valid(self):
        """Is the scene valid? A valid scene can be used to play a scene."""
        return self._is_valid

    def render_updates(self):
        """Render all sprite updates."""
        return self.render_updates

    def update_scene(self):
        """Update the scene state."""
        return self.update_scene

    def start_scene(self):
        """Start the scene."""
        if self._soundtrack:
            try:
                pygame.mixer.music.load(self._soundtrack)
                pygame.mixer.music.set_volume(0.1)
            except pygame.error as pygame_error:
                print("Cannot open the mixer?")
                raise SystemExit("broken!!") from pygame_error
            pygame.mixer.music.play(-1)

    def end_scene(self):
        """End the scene."""
        if self._soundtrack and pygame.mixer.music.get_busy():
            pygame.mixer.music.fadeout(500)
            pygame.mixer.music.stop()

    def frame_rate(self):
        """Return the frame rate the scene desires."""
        return self._frame_rate


class EmptyPressAnyKeyScene(Scene):
    """Empty scene where it will invalidate when a key is pressed."""

    # def __init__(self, screen, background_color, soundtrack=None):
    #     super().__init__(screen, background_color, soundtrack)

    # def draw(self):
    #     """Draw the scene."""
    #     super().draw()

    def process_event(self, event):
        """Process game events."""
        super().process_event(event)
        if event.type == pygame.KEYDOWN:
            self._is_valid = False


class SplashScene(EmptyPressAnyKeyScene):
    """A splash screen with a message."""

    def __init__(self, screen, message, soundtrack=None):
        """Init the splash screen."""
        super().__init__(screen, rgbcolors.snow, soundtrack)
        self._message = message
        self._words_per_line = 5

    def _split_message(self):
        """Given a message, split it up according to how many words per line."""
        lines = [
            " ".join(x).rstrip()
            for x in grouper(self._message.split(), self._words_per_line, "")
        ]
        for line in lines:
            yield line

    def draw(self):
        super().draw()
        (x_axis, y_axis) = self._screen.get_size()
        press_any_key_font = pygame.font.Font(pygame.font.get_default_font(), 18)
        press_any_key = press_any_key_font.render(
            "Press any key.", True, rgbcolors.black
        )
        press_any_key_pos = press_any_key.get_rect(center=(x_axis / 2, y_axis - 50))

        font = pygame.font.Font(pygame.font.get_default_font(), 25)
        start_pos = (y_axis / 2) - (
            (len(self._message.split()) // self._words_per_line) * 30
        )
        offset = 0
        for line in self._split_message():
            line = font.render(line, True, rgbcolors.black)
            line_pos = line.get_rect(center=(x_axis / 2, start_pos + offset))
            offset += 30
            self._screen.blit(line, line_pos)
        self._screen.blit(press_any_key, press_any_key_pos)


class BlinkingTitle(EmptyPressAnyKeyScene):
    """A scene with blinking text."""

    def __init__(self, screen, message, color, size, background_color, soundtrack=None):
        super().__init__(screen, background_color, soundtrack)
        self._message_color = color
        self._message_complement_color = (
            255 - color[0],
            255 - color[1],
            255 - color[2],
        )
        self._size = size
        self._message = message
        self._t = 0.0
        self._delta_t = 0.01

    def _interpolate(self):
        # This can be done with pygame.Color.lerp
        self._t += self._delta_t
        if self._t > 1.0 or self._t < 0.0:
            self._delta_t *= -1
        colors = rgbcolors.sum_color(
            rgbcolors.mult_color((1.0 - self._t), self._message_complement_color),
            rgbcolors.mult_color(self._t, self._message_color),
        )
        return colors

    def draw(self):
        super().draw()
        presskey_font = pygame.font.Font(pygame.font.get_default_font(), self._size)
        presskey = presskey_font.render(self._message, True, self._interpolate())
        (x_axis, y_axis) = self._screen.get_size()
        presskey_pos = presskey.get_rect(center=(x_axis / 2, y_axis / 2))
        press_any_key_font = pygame.font.Font(pygame.font.get_default_font(), 18)
        press_any_key = press_any_key_font.render(
            "Press any key.", True, rgbcolors.black
        )
        (x_axis, y_axis) = self._screen.get_size()
        press_any_key_pos = press_any_key.get_rect(center=(x_axis / 2, y_axis - 50))
        self._screen.blit(presskey, presskey_pos)
        self._screen.blit(press_any_key, press_any_key_pos)


class BouncingBallsScene(Scene):
    """Bounding balls demo."""

    def __init__(
            self, num_balls, screen, background_color, frame_rate, soundtrack=None
    ):
        super().__init__(screen, background_color, soundtrack)
        self._pause_game = False
        self._balls = []
        self._boundary_rect = self._screen.get_rect()

        self._num_balls = num_balls
        self._frame_rate = frame_rate
        self._screen = screen
        self._render_updates = None

    def start_scene(self):
        super().start_scene()
        # create random balls
        (x_axis, y_axis) = self._screen.get_size()
        # Debugging
        for i in range(4):
            self._balls.append(Ball(str(i), x_axis / 2, y_axis / 2, sound_on=False))
            # self._balls.append(Ball(i, x_axis/2, y_axis/2, sound_on=False))
        # self._balls.append(str(i), x_axis/2, y_axis/2, sound_on=False)

        # self._balls[0]._circle._center = pygame.Vector2(40, y_axis/2)
        self._balls[0]._circle.center.y -= 50
        # self._balls[0]._circle.center.y -= 100
        self._balls[0]._color = rgbcolors.red
        # Testing Different Bounces
        self._balls[0].set_velocity(0, 5)  # move balls up and down
        # self._balls[0].set_velocity(5,0) # move balls side to side

        # Testing Different Bounces
        # self._balls[1]._circle._center = pygame.Vector2(100, y_axis/2)
        self._balls[1]._circle.center.y -= 100
        # self._balls[1]._circle.center.y -= 100
        self._balls[1]._color = rgbcolors.green
        self._balls[1].set_velocity(0, -10)  # move balls up and down
        # self._balls[1].set_velocity(-5,0) # move balls side to side
        # self._balls[1]._circle.center.y -= 40

        # Testing more balls
        self._balls[2]._color = rgbcolors.blue
        self._balls[2].set_velocity(3, -5)

        # Image Drawing
        # not working
        # self._render_updates = pygame.sprite.RenderUpdates

    def end_scene(self):
        super().end_scene()
        # self

    def _draw_boundaries(self):
        (x_axis, y_axis) = self._screen.get_size()
        pygame.draw.rect(
            self._screen, rgbcolors.yellow, self._boundary_rect, (x_axis // 100), (x_axis // 200)
        )

    def process_event(self, event):
        super().process_event(event)

        if event.type == pygame.KEYDOWN and event.key == pygame.K_t:
            if self._soundtrack and pygame.mixer.music.get_busy():
                pygame.mixer.music.fadeout(500)
                pygame.mixer.music.stop()
            else:
                if self._soundtrack:
                    try:
                        pygame.mixer.music.load(self._soundtrack)
                    except pygame.error as pygame_error:
                        print("Cannot open the mixer?")
                        raise SystemExit("broken!!") from pygame_error
                    pygame.mixer.music.play(-1)

    def render_updates(self):
        if self._render_updates:
            self._render_updates.clear(self._screen, self._background)
            self._render_updates.update()
            dirty = self._render_updates.draw(self._screen)

    def draw(self):
        super().draw()
        for ball in self._balls:
            ball.draw(self._screen)
        self._draw_boundaries()

    def update_scene(self):
        rect = self._screen.get_size()
        if not self._pause_game:
            super().update_scene()
            # Update ball position on screen
            for ball in self._balls:
                ball.update()
            for ball in self._balls:
                # change this to rect not hardcoded
                ball.wall_reflect(0, 700, 0, 700)
                # ball.wall_reflect(rect.left, rect.right, rect.top, rect.bottom)
            for index, ball in enumerate(self._balls):
                # Enumerate not working properly
                # print(f"Testing {ball.name} against {other_ball.name}")
                for other_ball in self._balls[index + 1 :]:
                    # print(f"Testing {ball.name} against {other_ball.name}")
                    if ball.collide_with(other_ball):
                        # print(f'Ball {ball.name} collides against {other_ball.name}')
                        # print("test")
                        ball.separate_from(other_ball, pygame.Rect(0, 0, 0, 0))
                        ball.bounce(other_ball)
                        other_ball.bounce(ball)
                        # is alive not added yet
                        # if not ball.is_alive:
                        #     Explosion(ball)
                        # if not other_ball.is_alive:
                        #     Explosion(other_ball)
