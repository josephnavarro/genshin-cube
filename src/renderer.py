#! usr/bin/env python3
import pygame
from typing import Dict, List, Tuple
from src.render_context import RenderContext
from src.utility_image import ImageUtil


class Renderer:
    """ Stores images, updates them, and in general is responsible for
        executing actual in-game rendering routines. Requires an existing
        RenderContext first.
    """

    __slots__ = [
        "_rects",
        "_images",
        "context",
        "palette",
        "cursor"
    ]

    def __init__(self, context: RenderContext):
        self.context: RenderContext = context
        self._rects: Dict[str, pygame.Rect] = {}
        self._images: Dict[str, pygame.Surface] = {}
        self.palette: Dict[int, List[int]] = ImageUtil.new_palette(
            ImageUtil.DEFAULT_PALETTE_0,
            ImageUtil.DEFAULT_PALETTE_1,
            ImageUtil.DEFAULT_PALETTE_2,
            ImageUtil.DEFAULT_PALETTE_3
        )

        pygame.mouse.set_visible(False)

        s_image = "a8b2fafbXX8eG2(0a,3)2xwg01(05,3)abxef08hMmtXqhMmtXqhMmtX8sb(af,3)b(XX,2)xf"
        i_image = ImageUtil.convert_image(s_image, self.palette, 16, 16)
        i_image.set_colorkey(ImageUtil.DEFAULT_PALETTE_3)
        self.cursor = i_image

    @property
    def internal(self) -> pygame.Surface:
        """ Rendering context's internal display.
        """
        return self.context.internal

    @property
    def external(self) -> pygame.Surface:
        """ Rendering context's external display.
        """
        return self.context.external

    @property
    def scale_x(self) -> float:
        """ Rendering context's horizontal scaling factor.
        """
        return self.context.scale_x

    @scale_x.setter
    def scale_x(self, value: float):
        self.context.scale_x = value

    @property
    def scale_y(self) -> float:
        """ Rendering context's vertical scaling factorl.
        """
        return self.context.scale_y

    @scale_y.setter
    def scale_y(self, value: float):
        self.context.scale_y = value

    @property
    def window_size(self) -> Tuple[int, int]:
        return self.context.window_size

    @property
    def screen_size(self) -> Tuple[int, int]:
        return self.context.screen_size

    @staticmethod
    def quit():
        """ Safely quits pygame.
        """
        pygame.quit()
        raise SystemExit

    def draw_center(self, dest: pygame.Surface, key: str, x: int, y: int):
        """ Renders an image to a destination, centered at the given (x,y) pos.
        """
        image: pygame.Surface = self.get_image(key)
        rect: pygame.Rect = self.get_rect(key)
        rect.center = x, y
        dest.blit(image, rect)

    def draw_topright(self, dest: pygame.Surface, key: str, x: int, y: int):
        """ Renders an image to a destination, with its topright set to (x,y)
        """
        image: pygame.Surface = self.get_image(key)
        rect: pygame.Rect = self.get_rect(key)
        rect.topright = x, y
        dest.blit(image, rect)

    def draw_midright(self, dest: pygame.Surface, key: str, x: int, y: int):
        """ Renders an image to a destination, with its midright set to (x,y)
        """
        image: pygame.Surface = self.get_image(key)
        rect: pygame.Rect = self.get_rect(key)
        rect.midright = x, y
        dest.blit(image, rect)

    def draw_bottomright(self, dest: pygame.Surface, key: str, x: int, y: int):
        """ Renders an image to a destination, with its bottomright set to (x,y)
        """
        image: pygame.Surface = self.get_image(key)
        rect: pygame.Rect = self.get_rect(key)
        rect.bottomright = x, y
        dest.blit(image, rect)

    def draw_midbottom(self, dest: pygame.Surface, key: str, x: int, y: int):
        """ Renders an image to a destination, with its midbottom set to (x,y)
        """
        image: pygame.Surface = self.get_image(key)
        rect: pygame.Rect = self.get_rect(key)
        rect.midbottom = x, y
        dest.blit(image, rect)

    def draw_bottomleft(self, dest: pygame.Surface, key: str, x: int, y: int):
        """ Renders an image to a destination, with its bottomleft set to (x,y)
        """
        image: pygame.Surface = self.get_image(key)
        rect: pygame.Rect = self.get_rect(key)
        rect.bottomleft = x, y
        dest.blit(image, rect)

    def draw_midleft(self, dest: pygame.Surface, key: str, x: int, y: int):
        """ Renders an image to a destination, with its midleft set to (x,y)
        """
        image: pygame.Surface = self.get_image(key)
        rect: pygame.Rect = self.get_rect(key)
        rect.midleft = x, y
        dest.blit(image, rect)

    def draw_topleft(self, dest: pygame.Surface, key: str, x: int, y: int):
        """ Renders an image to a destination, with its topleft set to (x,y)
        """
        image: pygame.Surface = self.get_image(key)
        rect: pygame.Rect = self.get_rect(key)
        rect.topleft = x, y
        dest.blit(image, rect)

    def draw_midtop(self, dest: pygame.Surface, key: str, x: int, y: int):
        """ Renders an image to a destination, with its midtop set to (x,y)
        """
        image: pygame.Surface = self.get_image(key)
        rect: pygame.Rect = self.get_rect(key)
        rect.midtop = x, y
        dest.blit(image, rect)

    def store(self, key: str, image: pygame.Surface):
        """ Stores an image.
        """
        rect: pygame.Rect = image.get_rect()
        self._rects[key] = rect
        self._images[key] = image

    def delete(self, key: str):
        """ Deletes an image.
        """
        self._rects.pop(key)
        self._images.pop(key)

    def get_image(self, key: str) -> pygame.Surface:
        """ Fetches an image by its key.
        """
        return self._images.get(key)

    def get_rect(self, key: str) -> pygame.Rect:
        """ Fetches a rect by its key.
        """
        return self._rects.get(key)

    def normalize(self, x: int, y: int) -> Tuple[int, int]:
        """ Normalizes (x,y) coordinates to scale.
        """
        return int(round(x * self.context.inv_scale_x)), int(round(y * self.context.inv_scale_y))

    def flip(self):
        """ Refresh screen contents.
        """
        if self.scale_x != 1 or self.scale_y != 1:
            pygame.transform.scale(self.internal, self.window_size, self.external)
        else:
            self.external.blit(self.internal, (0, 0))
        pygame.display.flip()

    def render_cursor(self, dest: pygame.Surface):
        x, y = pygame.mouse.get_pos()
        x, y = self.normalize(x, y)
        dest.blit(self.cursor, self.cursor.get_rect(topleft=(x, y)))

    def update(self, events: list):
        """ Updates local events.
        """
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_h:
                    self.scale_x = 0.5
                    self.scale_y = 0.5
                elif e.key == pygame.K_o:
                    self.scale_x = 1.0
                    self.scale_y = 1.0

    def tick(self) -> float:
        return self.context.tick()
