#! usr/bin/env python3
import pygame
import os
from typing import Tuple

os.environ["SDL_VIDEO_CENTERED"] = "1"


class RenderContext:
    """ Simple PyGame rendering context. Just a data class.
        The Renderer is responsible for manipulaing stuff.
    """

    FPS: int = 60
    SCREEN_W: int = 320
    SCREEN_H: int = 240
    WINDOW_W: int = 640
    WINDOW_H: int = 480
    SCALE_X: int = WINDOW_W / SCREEN_W
    SCALE_Y: int = WINDOW_H / SCREEN_H
    CAPTION: str = "Block Game"  # TODO
    FLAGS: int = pygame.DOUBLEBUF | pygame.HWSURFACE

    __slots__ = [
        "_screen_w",
        "_screen_h",
        "_window_w",
        "_window_h",
        "_scale_x",
        "_scale_y",
        "_inv_scale_x",
        "_inv_scale_y",
        "internal",
        "external",
        "clock"
    ]

    def __init__(self):
        pygame.init()
        pygame.display.set_caption(RenderContext.CAPTION)

        self._screen_w: int = RenderContext.SCREEN_W
        self._screen_h: int = RenderContext.SCREEN_H
        self._window_w: int = RenderContext.WINDOW_W
        self._window_h: int = RenderContext.WINDOW_H
        self._scale_x: float = 0.0
        self._scale_y: float = 0.0
        self._inv_scale_x: float = 0.0
        self._inv_scale_y: float = 0.0
        self.external = pygame.display.set_mode(self.window_size, RenderContext.FLAGS, 32)
        self.internal = pygame.Surface(self.screen_size)
        self.clock = pygame.time.Clock()

    @property
    def window_size(self) -> Tuple[int, int]:
        return self.window_w, self.window_h

    @property
    def window_w(self) -> int:
        return self._window_w

    @window_w.setter
    def window_w(self, value: int):
        self._window_w = value
        old_external = self.external
        self.external = pygame.display.set_mode(self.window_size, RenderContext.FLAGS, 32)
        self.external.blit(old_external, (0, 0))
        del old_external
        self._update_scale_x()
        self._update_scale_y()

    @property
    def window_h(self) -> int:
        return self._window_h

    @window_h.setter
    def window_h(self, value: int):
        self._window_h = value
        old_external = self.external
        self.external = pygame.display.set_mode(self.window_size, RenderContext.FLAGS, 32)
        self.external.blit(old_external, (0, 0))
        del old_external
        self._update_scale_y()
        self._update_inv_scale_y()

    @property
    def screen_size(self) -> Tuple[int, int]:
        return self.screen_w, self.screen_h

    @property
    def screen_w(self) -> int:
        return self._screen_w

    @screen_w.setter
    def screen_w(self, value: int):
        self._screen_w = value
        self._update_scale_x()
        self._update_inv_scale_x()

    @property
    def screen_h(self) -> int:
        return self._screen_h

    @screen_h.setter
    def screen_h(self, value: int):
        self._screen_h = value
        self._update_scale_y()
        self._update_inv_scale_y()

    @property
    def scale_x(self) -> float:
        if not self._scale_x:
            self._update_scale_x()
            self._update_inv_scale_x()
        return self._scale_x

    @scale_x.setter
    def scale_x(self, value: float):
        self._update_scale_x(value)

    @property
    def inv_scale_x(self) -> float:
        if not self._inv_scale_x:
            self._update_inv_scale_x()
        return self._inv_scale_x

    @property
    def scale_y(self) -> float:
        if not self._scale_y:
            self._update_scale_y()
            self._update_inv_scale_y()
        return self._scale_y

    @scale_y.setter
    def scale_y(self, value: float):
        self._update_scale_y(value)

    @property
    def inv_scale_y(self) -> float:
        if not self._inv_scale_y:
            self._update_inv_scale_y()
        return self._inv_scale_y

    def _update_scale_x(self, scale_x: float = 0.0):
        if not scale_x:
            scale_x: float = self.window_w / self.screen_w
        else:
            self.window_w = int(round(RenderContext.WINDOW_W * scale_x))
        self._scale_x = scale_x

    def _update_inv_scale_x(self, scale_x: float = 0.0):
        if not scale_x:
            self._inv_scale_x = 1 / self.scale_x
        else:
            self._inv_scale_x = 1 / scale_x

    def _update_scale_y(self, scale_y: float = 0.0):
        if not scale_y:
            scale_y: float = self.window_h / self.screen_h
        else:
            self.window_h = int(round(RenderContext.WINDOW_H * scale_y))
        self._scale_y = scale_y

    def _update_inv_scale_y(self, scale_y: float = 0.0):
        if not scale_y:
            self._inv_scale_y = 1 / self.scale_y
        else:
            self._inv_scale_y = 1 / scale_y

    def tick(self) -> float:
        return self.clock.tick(RenderContext.FPS)
