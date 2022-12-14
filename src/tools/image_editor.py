#! usr/bin/env python3
import os
import shutil
import pygame
import pyperclip as pc
import numpy as np
from typing import List, Tuple, Dict
from src.utility_image import ImageUtil


class ImageEditor:
    CAPTION: str = "Image Editor"
    FLAGS: int = pygame.DOUBLEBUF | pygame.HWSURFACE
    SCREEN_WIDTH: int = 720
    SCREEN_HEIGHT: int = 480
    DEFAULT_WIDTH: int = 32
    DEFAULT_HEIGHT: int = 32
    PIXEL_WIDTH: int = 8
    PIXEL_HEIGHT: int = 8
    WIDGET_BUFFER: int = 8
    PALETTE_WIDTH: int = 32
    PALETTE_HEIGHT: int = 16
    HISTORY: int = 50
    NUM_CANVASES: int = 6
    FONT_SIZE: Tuple[int, int] = 8, 8

    __slots__ = [
        "background",
        "display",
        "clock",
        "num_canvases",
        "working_images",
        "working_palettes",
        "working_transparencies",
        "palette_indices",
        "canvas_index",
        "cursor",
        "palettes",
        "clipboards",
        "histories",
        "redos",
        "font",
        "cut_buffer",
        "pixel_grid",
        "multi_preview",
        "load_file"
    ]

    def __init__(
          self,
          w: int = DEFAULT_WIDTH,
          h: int = DEFAULT_HEIGHT,
          num_canvases: int = NUM_CANVASES,
          *,
          multi_preview: List[int] = [0, 0],
          load_file: str = str()
    ):
        # Pygame stuff
        self.display, self.background = self.init_pygame()
        self.clock = pygame.time.Clock()

        # Load persistent data (if any)
        buffer = dict()
        palette_buffer = dict()
        transparencies_buffer = dict()
        if load_file:
            try:
                with open(load_file, "r") as f:
                    for line in f.readlines():
                        a, b = line.split(">>")
                        a = a.strip().split("_")
                        b = b.strip()
                        if a[0] == "canvas":
                            if a[1] == "w":
                                w = int(b)
                            elif a[1] == "h":
                                h = int(b)
                            else:
                                n = int(a[1])
                                buffer[n] = b
                        elif a[0] == "num":
                            if a[1] == "canvases":
                                num_canvases = int(b)
                        elif a[0] == "multipreview":
                            if a[1] == "x":
                                multi_preview[0] = int(b)
                            elif a[1] == "y":
                                multi_preview[1] = int(b)
                        elif a[0] == "palette":
                            n = int(a[1])
                            palette_buffer[n] = int(b)
                        elif a[0] == "transparencies":
                            a1 = int(a[1])
                            a2 = int(a[2])
                            if a1 not in transparencies_buffer:
                                transparencies_buffer[a1] = dict()
                            transparencies_buffer[a1][a2] = int(b)
            except FileNotFoundError:
                pass

        self.load_file = load_file

        # Main variables
        assert bool(num_canvases)

        self.pixel_grid: bool = True
        self.num_canvases: int = num_canvases
        self.canvas_index: int = int()
        self.palette_indices: List[int] = [int() for _ in range(num_canvases)]
        self.working_transparencies: Dict[int, Dict[int, int]] = dict()
        self.cursor: List[int] = [0, 0, 1, 1]
        self.multi_preview: List[int] = multi_preview
        self.histories: List[List[str]] = [list() for _ in range(num_canvases)]
        self.redos: List[List[str]] = [list() for _ in range(num_canvases)]
        self.cut_buffer: Tuple[np.ndarray, int, int] = tuple()
        self.palettes: Dict[int, Dict[int, List[int]]] = dict()
        self.font: Dict[str, pygame.Surface] = dict()
        self.clipboards: List[str] = list()

        # Create canvases
        self.working_palettes: List[int] = [int() for _ in range(num_canvases)]
        for k, v in palette_buffer.items():
            self.working_palettes[k] = v

        self.working_images: List[np.ndarray] = [ImageEditor.new_image(h, w) for _ in range(num_canvases)]
        for k, v in buffer.items():
            image = ImageUtil.hydrate(v)
            image = ImageUtil.deserialize(image, self.working_image_w, self.working_image_h)
            self.working_images[k] = image

        # Finish up initialization
        self.init_canvases(buffer)
        self.init_clipboards()
        self.init_palette(transparencies_buffer)
        self.init_font()

    @property
    def palette_index(self) -> int:
        return self.palette_indices[self.canvas_index]

    @palette_index.setter
    def palette_index(self, value):
        self.palette_indices[self.canvas_index] = value

    @property
    def history(self) -> List[str]:
        return self.histories[self.canvas_index]

    @history.setter
    def history(self, value):
        self.histories[self.canvas_index] = value

    @property
    def redo(self) -> List[str]:
        return self.redos[self.canvas_index]

    @redo.setter
    def redo(self, value):
        self.redos[self.canvas_index] = value

    @property
    def canvas_offset_x(self) -> int:
        return 0

    @property
    def canvas_offset_y(self) -> int:
        return 0

    @property
    def canvas_offset(self) -> Tuple[int, int]:
        return self.canvas_offset_x, self.canvas_offset_y

    @property
    def clipboard(self) -> str:
        return self.clipboards[self.canvas_index]

    @clipboard.setter
    def clipboard(self, value):
        self.clipboards[self.canvas_index] = value

    @property
    def working_palette(self) -> int:
        return self.working_palettes[self.canvas_index]

    @working_palette.setter
    def working_palette(self, value):
        if value < 0:
            value = len(self.palettes) - 1
        if value >= len(self.palettes):
            value = 0
        self.working_palettes[self.canvas_index] = value

    @property
    def working_image(self) -> np.ndarray:
        return self.working_images[self.canvas_index]

    @working_image.setter
    def working_image(self, value):
        self.working_images[self.canvas_index] = value

    @property
    def working_image_h(self) -> int:
        return self.working_image.shape[0]

    @property
    def working_image_w(self) -> int:
        return self.working_image.shape[1]

    @property
    def preview_offset_x(self) -> int:
        return ImageEditor.WIDGET_BUFFER

    @property
    def preview_offset_y(self) -> int:
        return self.working_image_h * ImageEditor.PIXEL_HEIGHT + ImageEditor.WIDGET_BUFFER

    @property
    def preview_offset(self) -> Tuple[int, int]:
        return self.preview_offset_x, self.preview_offset_y

    @property
    def multi_preview_offset_x(self) -> int:
        return self.display.get_width() - (self.multi_preview[0] * self.working_image_w + ImageEditor.WIDGET_BUFFER)

    @property
    def multi_preview_offset_y(self) -> int:
        return ImageEditor.WIDGET_BUFFER

    @property
    def multi_preview_offset(self) -> Tuple[int, int]:
        return self.multi_preview_offset_x, self.multi_preview_offset_y

    @property
    def palette_offset_x(self) -> int:
        return self.working_image_w * ImageEditor.PIXEL_WIDTH + ImageEditor.WIDGET_BUFFER

    @property
    def palette_offset_y(self) -> int:
        return ImageEditor.WIDGET_BUFFER

    @property
    def palette_offset(self) -> Tuple[int, int]:
        return self.palette_offset_x, self.palette_offset_y

    @property
    def clipboard_offset_x(self) -> int:
        return ImageEditor.WIDGET_BUFFER

    @property
    def clipboard_offset_y(self) -> int:
        return self.preview_offset_y + self.working_image_h + ImageEditor.WIDGET_BUFFER

    @property
    def clipboard_offset(self) -> Tuple[int, int]:
        return self.clipboard_offset_x, self.clipboard_offset_y

    @staticmethod
    def new_image(x: int, y: int) -> np.ndarray:
        return np.zeros((x, y), dtype=np.int8)

    @staticmethod
    def init_pygame():
        """ Initializes pygame for rendering.
        """
        pygame.init()
        pygame.display.set_caption(ImageEditor.CAPTION)
        display = pygame.display.set_mode((ImageEditor.SCREEN_WIDTH, ImageEditor.SCREEN_HEIGHT), ImageEditor.FLAGS, 32)

        # Gray gradient background generation
        def gray(im):
            im = 255 * (im / im.max())
            w, h = im.shape
            ret = np.empty((w, h, 3), dtype=np.uint8)
            ret[:, :, 2] = ret[:, :, 1] = ret[:, :, 0] = im
            return ret

        x = np.arange(0, ImageEditor.SCREEN_WIDTH)
        y = np.arange(0, ImageEditor.SCREEN_HEIGHT)
        xx, yy = np.meshgrid(x, y)
        z = xx + yy
        z = 255 * z / z.max()
        z = gray(z)
        s = pygame.surfarray.make_surface(z)
        s = pygame.transform.smoothscale(s, (ImageEditor.SCREEN_WIDTH, ImageEditor.SCREEN_HEIGHT))  # TODO

        #s = pygame.Surface((ImageEditor.SCREEN_WIDTH, ImageEditor.SCREEN_HEIGHT))
        #s.fill((0, 0, 0))

        return display, s

    def init_canvases(self, buffer: Dict[int, str]):
        """ Initializes canvases with persistent data (if any).
        """
        for k, v in buffer.items():
            image = ImageUtil.hydrate(v)
            image = ImageUtil.deserialize(image, self.working_image_w, self.working_image_h)
            self.working_images[k] = image

    def init_clipboards(self):
        """ Initializes clipboards for each canvas.
        """
        self.clipboards = [self.export_nth_image(_) for _ in range(self.num_canvases)]

    def init_palette(self, buffer: dict):
        """ Initializes default palette.
        """
        self.palettes[0] = ImageUtil.new_palette(ImageUtil.PALETTE_A_0, ImageUtil.PALETTE_A_1, ImageUtil.PALETTE_A_2, ImageUtil.PALETTE_A_3)
        self.palettes[1] = ImageUtil.new_palette(ImageUtil.PALETTE_B_0, ImageUtil.PALETTE_B_1, ImageUtil.PALETTE_B_2, ImageUtil.PALETTE_B_3)
        self.palettes[2] = ImageUtil.new_palette(ImageUtil.PALETTE_C_0, ImageUtil.PALETTE_C_1, ImageUtil.PALETTE_C_2, ImageUtil.PALETTE_C_3)
        self.palettes[3] = ImageUtil.new_palette(ImageUtil.PALETTE_D_0, ImageUtil.PALETTE_D_1, ImageUtil.PALETTE_D_2, ImageUtil.PALETTE_D_3)
        self.palettes[4] = ImageUtil.new_palette(ImageUtil.PALETTE_E_0, ImageUtil.PALETTE_E_1, ImageUtil.PALETTE_E_2, ImageUtil.PALETTE_E_3)
        self.palettes[5] = ImageUtil.new_palette(ImageUtil.PALETTE_F_0, ImageUtil.PALETTE_F_1, ImageUtil.PALETTE_F_2, ImageUtil.PALETTE_F_3)
        self.palettes[6] = ImageUtil.new_palette(ImageUtil.PALETTE_G_0, ImageUtil.PALETTE_G_1, ImageUtil.PALETTE_G_2, ImageUtil.PALETTE_G_3)
        self.palettes[7] = ImageUtil.new_palette(ImageUtil.PALETTE_H_0, ImageUtil.PALETTE_H_1, ImageUtil.PALETTE_H_2, ImageUtil.PALETTE_H_3)
        self.palettes[8] = ImageUtil.new_palette(ImageUtil.PALETTE_I_0, ImageUtil.PALETTE_I_1, ImageUtil.PALETTE_I_2, ImageUtil.PALETTE_I_3)

        for canvas_index in range(self.num_canvases):
            self.working_transparencies[canvas_index] = dict()
            for x in self.palettes:
                try:
                    self.working_transparencies[canvas_index][x] = buffer[canvas_index][x]
                except KeyError:
                    self.working_transparencies[canvas_index][x] = -1

    def init_font(self):
        """ Initializes default font.
        """
        iuci = lambda _: ImageUtil.convert_image(_, self.palettes[0], *ImageEditor.FONT_SIZE)
        self.font = {
            "0": iuci("fc(f0,2)xjfc3fj3c30f03XXf"),
            "1": iuci("fcXf3c(0f,2)0jXxjXX"),
            "2": iuci("fcXfj3xcJu3xjXX"),
            "3": iuci("(fcx,2)jfcxj3u3f03XXf"),
            "4": iuci("xfcf0xfc3fux(0f,2)0c3XXf"),
            "5": iuci("(f0,2)fc(xJ,2)3cf03XXf"),
            "6": iuci("x(f0,2)xc3uxj3fcx03XXf"),
            "7": iuci("f0Xxjfcf0fj03XXXf"),
            "8": iuci("fcf3f0xjuxj3u3f03XXf"),
            "9": iuci("fcf3Xjuxj3u0f03XXf"),
            "a": iuci("XfcXJjx3c30jXX"),
            "b": iuci("(f0,3)f3(xj,2)x3cf03XXf"),
            "c": iuci("xfcf0X(jx,3)jXX"),
            "d": iuci("xfcf0Xjxjf030f0jXX"),
            "e": iuci("xfcf0XJjx3cj3XXf"),
            "f": iuci("XXxuXc30c0(f3,2)fcXf"),
            "g": iuci("xfcf3XjUx3(0c,2)3XX"),
            "h": iuci("(f0,3)f3xc3Xx3cf0f3XX"),
            "i": iuci("XXfj0f0jXx3XXf"),
            "j": iuci("Xxf3Xxufj0f0c3XX"),
            "k": iuci("(f0,3)f(3Xc,2)3cx3XX"),
            "l": iuci("XX3(0f,2)0jXx3XXf"),
            "m": iuci("x(f0,2)f3x3(0f,2)3x3cf0f3XX"),
            "n": iuci("x(f0,2)f3xjXx3cf0f3XX"),
            "o": iuci("xfcf0X(jx,2)3cf03XXf"),
            "p": iuci("x(f0,3)xjuX3u3XXx"),
            "q": iuci("xfcf3XjuX30c0f0XX"),
            "r": iuci("x(f0,2)f3xc3Xx3cXXX"),
            "s": iuci("xfcxf3xJjxj3c3XXf"),
            "t": iuci("XXxjX0f030(x3,2)xf3f"),
            "u": iuci("x(f0,2)XXjx(f0,2)jXX"),
            "v": iuci("xf0f3Xxcx3xf0c3XXx"),
            "w": iuci("x(f0,2)Xfcf03X0f03XXf"),
            "x": iuci("(xf3,2)xcfc3Xc3cx3XX"),
            "y": iuci("xf0f3XxUxf(0c,2)3XX"),
            "z": iuci("(xf3,2)xjcj3x03xjXX"),
            "A": iuci("x(f0,2)f3c3xjxcx030f3XX"),
            "B": iuci("(f0,3)fj3uxj3u3f03XXf"),
            "C": iuci("fc(f0,2)xjXj3cxfc3XXf"),
            "D": iuci("(f0,3)fj3Xjcx0c3XXx"),
            "E": iuci("(f0,3)fj3uxJcxfjXX"),
            "F": iuci("(f0,3)fj3uXjcXXXf"),
            "G": iuci("fc(f0,2)xjfcxJuf0jXX"),
            "H": iuci("(f0,3)f3xuXf0c(0f,2)3XX"),
            "I": iuci("XX3(0f,2)0j3Xf3XXf"),
            "J": iuci("Xfcxf3Xj030f0XXxf"),
            "K": iuci("(f0,3)f3xc3f(3xc,2)x3XX"),
            "L": iuci("(f0,3)f3(Xxj,2)XX"),
            "M": iuci("(f0,3)f3cx3Xc(0f,3)3XX"),
            "N": iuci("(f0,3)f3cx3Xf0c(0f,2)3XX"),
            "O": iuci("fc(f0,2)xjXj3c(f0,2)3XXf"),
            "P": iuci("(f0,3)fj3uX3u3XXX"),
            "Q": iuci("fc(f0,2)xjxfJcf0c3f3XX"),
            "R": iuci("(f0,3)fj3uf3x3u3cx3XX"),
            "S": iuci("fcf3fcxjuxj3ux03XXf"),
            "T": iuci("f3Xx3(0f,3)j3XXXx"),
            "U": iuci("(f0,3)XXj(f0,3)3XXf"),
            "V": iuci("f0f3Xx(cf3,2)f0cjXXxf"),
            "W": iuci("(0f,2)3cf3fujXf(cf3,2)(0f,2)3xf"),
            "X": iuci("f0xfcf3x3c3X03f3cf3XX"),
            "Y": iuci("f0XX3cf0f3f03XXXf"),
            "Z": iuci("f3xfcfj3fc3fj303xfjXX"),
            "(": iuci("XXfc0f3cx3Xf3XXf"),
            ")": iuci("XX3cxfc3xf0f3XXxf"),
            ",": iuci("XXXxfcXu03XX"),
            ".": iuci("XXXuj(XX,2)"),
            " ": iuci("(XX,4)"),
            "+": iuci("xfcXfu0f0XuXXX"),
            "-": iuci("xfc(Xxu,2)XXX"),
            "!": iuci("XX(f0,2)(f3,2)(XX,2)"),
            "\"": iuci("f0f3Xf0f3(XX,2)X"),
            "#": iuci("x(f3,2)x0f030j(f0,2)30jXXf"),
            "$": iuci("xf3fcx(c0,3)f3ucfc3XXx"),
            ":": iuci("XXxf3fc(XX,2)x"),
            ";": iuci("XXxf3fu3(XX,2)"),
            "<": iuci("XXxc3f(3xc,2)x3XX"),
            "=": iuci("x(f3,2)(XJ,2)XXx"),
            ">": iuci("f3Xf3cx3c3XcXXXf"),
            "?": iuci("fcXxjxf3fju3XXX"),
            "@": iuci("xf0f3xc3fuxjc303fjXX"),
            "[": iuci("XX03(0f,2)j3Xf3XXf"),
            "]": iuci("X(Xj,2)(0f,3)3XXf"),
            "^": iuci("xf3Xc3Xxcx3XXX"),
            "_": iuci("(Xxj,3)Xx3f"),
            "`": iuci("XX3c(XX,2)Xx"),
            "/": iuci("Xxf(3Xc,3)Xxf")
        }

        for ii in self.font.values():
            ii.set_colorkey((0, 0, 0))

    def save(self):
        save_file = self.load_file or "persist-temp.txt"
        with open(save_file, "w") as f:
            f.write(f"canvas_w>>{self.working_image_w}\n")
            f.write(f"canvas_h>>{self.working_image_h}\n")
            f.write(f"num_canvases>>{self.num_canvases}\n")
            for n in range(self.num_canvases):
                f.write(f"canvas_{n}>>{self.export_nth_image(n)}\n")
            for n in range(self.num_canvases):
                f.write(f"palette_{n}>>{self.working_palettes[n]}\n")
            for n in self.working_transparencies:
                for x in self.working_transparencies[n]:
                    f.write(f"transparencies_{n}_{x}>>{self.working_transparencies[n][x]}\n")
            f.write(f"multipreview_x>>{self.multi_preview[0]}\n")
            f.write(f"multipreview_y>>{self.multi_preview[1]}\n")

    def quit(self):
        """ Safely quits pygame.
        """
        self.save()
        pygame.quit()
        raise SystemExit

    @staticmethod
    def get_pixel(image: np.ndarray, y: int, x: int) -> int:
        """ Returns the pixel (palette index) at the given coordinate.
        """
        return int(image[y, x])

    @staticmethod
    def draw_dotted_line(dest: pygame.Surface, p1: Tuple[int, int], p2: Tuple[int, int]):
        """ Renders a dotted line for the UI.
        """
        x1, y1 = p1
        x2, y2 = p2
        dx = x2 - x1
        dy = y2 - y1
        if dx:
            for x in range(x1, x2, ImageEditor.PIXEL_WIDTH):
                pygame.draw.circle(dest, (64, 64, 64), (x, int(y1)), 1)
                y1 += dy * x / dx
        elif dy:
            for y in range(y1, y2, ImageEditor.PIXEL_HEIGHT):
                pygame.draw.circle(dest, (64, 64, 64), (int(x1), y), 1)
                x1 += dx * y / dy

    def export_nth_image(self, n: int) -> str:
        """ Converts an arbitrary canvas to an image string.
        """
        working_image = self.working_images[n]
        return ImageUtil.numpy_image_to_string(working_image)

    def export_image(self) -> str:
        """ Converts the current working image to an image string.
        """
        return self.export_nth_image(self.canvas_index)

    def import_image(self, hexstring: str):
        """ Overwrites the current working image to be a copy of the given string.
        """
        try:
            image = ImageUtil.hydrate(hexstring)
            image = ImageUtil.deserialize(image, self.working_image_w, self.working_image_h)
            self.working_image = image
        except Exception as e:
            print(e)

    def set_pixel(self, value: int, y: int, x: int):
        """ Sets a pixel on the current canvas.
        """
        self.working_image[y:y+self.cursor[3], x:x+self.cursor[2]] = value

    def draw_canvas(self, dest: pygame.Surface, x: int, y: int, do_scale: bool = True):
        """ Renders canvas of the current working image to screen.
        """
        return self.draw_nth_canvas(self.canvas_index, dest, x, y, do_scale)

    def draw_nth_canvas(self, index: int, dest: pygame.Surface, x: int, y: int, do_scale: bool = True):
        """ Renders an arbitrary canvas to screen.
        """
        scale_x = ImageEditor.PIXEL_WIDTH if do_scale else 1
        scale_y = ImageEditor.PIXEL_HEIGHT if do_scale else 1
        working_image = self.working_images[index]
        working_palette = self.working_palettes[index]
        for m in range(working_image.shape[0]):
            for n in range(working_image.shape[1]):
                palette_enum = self.get_pixel(working_image, m, n)
                if palette_enum != self.working_transparencies[index][working_palette]:
                    color = self.palettes[working_palette][palette_enum]
                    pygame.draw.rect(dest, color, (x + m * scale_x, y + n * scale_y, scale_x, scale_y))
        return scale_x * working_image.shape[1], scale_y * working_image.shape[0]

    def draw_palette(self, dest: pygame.Surface) -> Tuple[int, int]:
        """ Renders the palette bar.
        """
        spacing_x: int = ImageEditor.PALETTE_WIDTH + ImageEditor.WIDGET_BUFFER
        spacing_y: int = ImageEditor.PALETTE_HEIGHT + ImageEditor.WIDGET_BUFFER
        dx: int = 0
        dy: int = 0

        for m, palette in self.palettes.items():
            for n, color in palette.items():
                dx = self.palette_offset_x + m * spacing_x
                dy = self.palette_offset_y + n * spacing_y
                rect = (dx, dy, ImageEditor.PALETTE_WIDTH, ImageEditor.PALETTE_HEIGHT)
                pygame.draw.rect(dest, (0, 0, 0), rect, 5)
                pygame.draw.rect(dest, (255, 255, 255), rect, 3)
                pygame.draw.rect(dest, color, rect)

                if n == self.working_transparencies[self.canvas_index][m]:
                    inv_color = (255 - color[0], 255 - color[1], 255 - color[2])
                    pygame.draw.line(dest, inv_color, (dx, dy), (dx + ImageEditor.PALETTE_WIDTH, dy + ImageEditor.PALETTE_HEIGHT), 2)
                    pygame.draw.line(dest, inv_color, (dx + ImageEditor.PALETTE_WIDTH, dy), (dx, dy + ImageEditor.PALETTE_HEIGHT), 2)

                # Highlight the current color
                if m == self.working_palette and n == self.palette_index:
                    pygame.draw.rect(dest, (0, 0, 0), rect, 5)
                    pygame.draw.rect(dest, (255, 255, 255), rect, 3)

        return dx + spacing_x, dy + spacing_y

    def draw_cursor(self, dest: pygame.Surface, x: int, y: int):
        """ Renders the brush cursor.
        """
        cx = self.cursor[1]
        cy = self.cursor[0]
        cw = self.cursor[3]
        ch = self.cursor[2]

        edge1 = cx == self.working_image_w - 1 or cx == 0
        edge2 = cy == self.working_image_h - 1 or cy == 0
        edge3 = cx + cw == self.working_image_w
        edge4 = cy + ch == self.working_image_h

        color1 = (255, 255, 255)
        color2 = (0, 0, 0)
        if edge1 or edge2 or edge3 or edge4:
            color1 = (255, 255, 0)
            color2 = (255, 0, 0)

        pygame.draw.rect(
              dest,
              color1, (
                  cx * ImageEditor.PIXEL_WIDTH + x - 1,
                  cy * ImageEditor.PIXEL_HEIGHT + y - 1,
                  self.cursor[3] * ImageEditor.PIXEL_WIDTH + 2,
                  self.cursor[2] * ImageEditor.PIXEL_HEIGHT + 2
              ), 3
        )
        pygame.draw.rect(
              dest,
              color2, (
                  cx * ImageEditor.PIXEL_WIDTH + x,
                  cy * ImageEditor.PIXEL_HEIGHT + y,
                  self.cursor[3] * ImageEditor.PIXEL_WIDTH,
                  self.cursor[2] * ImageEditor.PIXEL_HEIGHT
              ), 1
        )

    def draw_text(self, dest: pygame.Surface, string: str, x: int, y: int) -> tuple[int, int]:
        """ Renders some text.
        """
        dx: int = 0
        dy: int = 0
        w: int = 0
        h: int = 0
        for ch in string:
            if ch == "\n":
                dx = 0
                dy += h
            else:
                glyph = self.font.get(ch)
                if glyph:
                    w = glyph.get_width()
                    h = glyph.get_height()
                    if (x + dx + w) > ImageEditor.SCREEN_WIDTH:
                        dx = 0
                        dy += h
                    dest.blit(glyph, (x + dx, y + dy))
                    dx += w
        return x + dx + w, y + dy + h

    def draw_pixel_grid(self, start_x: int, start_y: int):
        """ Draws pixel grid guidelines.
        """
        self.display.lock()
        for x in range(self.working_image_w + 1):
            p1 = (x * ImageEditor.PIXEL_WIDTH, start_y)
            p2 = (x * ImageEditor.PIXEL_WIDTH, start_y + self.working_image_h * ImageEditor.PIXEL_HEIGHT)
            self.draw_dotted_line(self.display, p1, p2)
        for y in range(self.working_image_h + 1):
            p1 = (start_x, y * ImageEditor.PIXEL_HEIGHT)
            p2 = (start_x + self.working_image_w * ImageEditor.PIXEL_WIDTH, y * ImageEditor.PIXEL_HEIGHT)
            self.draw_dotted_line(self.display, p1, p2)
        self.display.unlock()

    def draw_bg_grid(self):
        """ Draws pixel grid guidelines.
        """
        w = ImageEditor.SCREEN_WIDTH // ImageEditor.PIXEL_WIDTH
        h = ImageEditor.SCREEN_HEIGHT // ImageEditor.PIXEL_HEIGHT

        self.display.lock()
        for x in range(w + 1):
            p1 = (x * ImageEditor.PIXEL_WIDTH, 0)
            p2 = (x * ImageEditor.PIXEL_WIDTH, h * ImageEditor.PIXEL_HEIGHT)
            self.draw_dotted_line(self.display, p1, p2)
        for y in range(h + 1):
            p1 = (0, y * ImageEditor.PIXEL_HEIGHT)
            p2 = (w * ImageEditor.PIXEL_WIDTH, y * ImageEditor.PIXEL_HEIGHT)
            self.draw_dotted_line(self.display, p1, p2)
        self.display.unlock()

    def render(self):
        """ Toplevel rendering method.
        """
        self.display.blit(self.background, (0, 0))
        self.draw_bg_grid()

        # Editing canvas
        dx, dy = self.canvas_offset
        dxc, dyc = self.draw_canvas(self.display, dx, dy)
        self.draw_cursor(self.display, dx, dy)
        if self.pixel_grid:
            self.draw_pixel_grid(dx, dy)

        # Multi-composite preview
        dx, dy = self.multi_preview_offset
        nx, ny = self.multi_preview
        if nx > 0 and ny > 0:
            for y in range(ny):
                for x in range(nx):
                    n = x + y * nx
                    try:
                        tx = dx + x * self.working_image_w
                        ty = dy + y * self.working_image_h
                        self.draw_nth_canvas(n, self.display, tx, ty, False)
                    except IndexError:
                        pass

        # Palette bar
        dx, dy = self.draw_palette(self.display)

        # Multiple 1:1 scale previews
        dx2, dy2 = self.preview_offset
        tx2 = dx2
        ty2 = max(dyc, dy) + ImageEditor.WIDGET_BUFFER
        # tw2 = 0
        th2 = 0
        for n in range(self.num_canvases):
            canvas = self.working_images[n]
            th2 = canvas.shape[0]
            tw2 = canvas.shape[1]
            if tx2 >= ImageEditor.SCREEN_WIDTH - ImageEditor.WIDGET_BUFFER:
                tx2 = dx2
                ty2 += ImageEditor.WIDGET_BUFFER + th2
            self.draw_nth_canvas(n, self.display, tx2, ty2, False)
            if n != self.canvas_index:
                # Dim the ones that aren't in focus
                self.display.fill(
                    (100, 100, 100),
                    (tx2, ty2, tw2, th2),
                    special_flags=pygame.BLEND_MULT
                )
            tx2 += tw2 + ImageEditor.WIDGET_BUFFER

        # Selection size
        self.draw_text(self.display, f"x {self.cursor[1]}", dx, ImageEditor.WIDGET_BUFFER + ImageEditor.FONT_SIZE[0] * 0)
        self.draw_text(self.display, f"y {self.cursor[0]}", dx, ImageEditor.WIDGET_BUFFER + ImageEditor.FONT_SIZE[0] * 2)
        self.draw_text(self.display, f"w {self.cursor[3]}", dx, ImageEditor.WIDGET_BUFFER + ImageEditor.FONT_SIZE[0] * 4)
        self.draw_text(self.display, f"h {self.cursor[2]}", dx, ImageEditor.WIDGET_BUFFER + ImageEditor.FONT_SIZE[0] * 6)
        self.draw_text(
              self.display,
              f"{self.working_image_w},{self.working_image_h}",
              dx, ImageEditor.WIDGET_BUFFER + ImageEditor.FONT_SIZE[0] * 8
        )

        # String preview
        self.strings_below(ty2, th2)

        pygame.display.flip()

    def strings_below(self, ty2, th2):
        dx0, dy0 = self.clipboard_offset
        dx1, dy1 = self.draw_text(self.display, self.clipboard, dx0, ty2 + th2 + ImageEditor.WIDGET_BUFFER)
        self.draw_text(
            self.display,
            "UP/DOWN/LEFT/RIGHT: Move cursor\n"
            "X:                  Paint\n"
            "N:                  Copy (string) to clipboard\n"
            "M:                  Paste (string) from clipboard\n"
            "A:                  Maximize\n"
            "S:                  Minimize\n"
            "T:                  Set current color as transparent\n"
            "SPACE:              Next canvas\n"
            "SHIFT+SPACE:        Previous canvas\n"
            "SHIFT+UP:           Cursor height -\n"
            "SHIFT+DOWN:         Cursor height +\n"
            "SHIFT+LEFT:         Cursor width -\n"
            "SHIFT+RIGHT:        Cursor width +\n"
            "ALT+UP/DOWN:        Cycle color\n"
            "ALT+LEFT/RIGHT:     Cycle palette\n"
            "SHIFT+X:            Cut\n"
            "SHIFT+C:            Copy\n"
            "SHIFT+V:            Paste\n"
            "SHIFT+Z:            Undo\n"
            "SHIFT+R:            Redo\n"
            "SHIFT+G:            Toggle grid\n"
            "SHIFT+E:            Export all to PNG\n"
            "SHIFT+S:            Save"
            ,
            dx0, dy1 + ImageEditor.WIDGET_BUFFER
        )

    def snapshot(self) -> str:
        """ Returns a string representation of the current image.
        """
        im: str = self.export_image()
        self.clipboard = im
        return im

    def swap(self, a: List[str], b: List[str]):
        """ Things to take care of when undoing and redoing.
        """
        im: str = self.snapshot()
        if a:
            # If 'a'=='undo', 'b'=='redo', and vice versa
            b.append(im)
            restore: str = a.pop()
            self.import_image(restore)
            self.snapshot()

    def cut(self, preserve: bool = False):
        """ Cuts a portion of the screen.
        """
        x = self.cursor[0]
        y = self.cursor[1]
        cutted: np.ndarray = np.copy(self.working_image[y:y + self.cursor[3], x:x + self.cursor[2]])
        self.cut_buffer = (cutted, self.cursor[2], self.cursor[3])
        if not preserve:
            self.working_image[y:y + self.cursor[3], x:x + self.cursor[2]] = self.working_image[y, x]

    def paste(self):
        """ Pastes a portion of the screen.
        """
        if self.cut_buffer:
            x = self.cursor[0]
            y = self.cursor[1]
            w = self.cut_buffer[1]
            h = self.cut_buffer[2]
            im = self.cut_buffer[0]
            ww = self.working_image_w
            if (x + w) > ww:
                im = im[:, :ww - x]
            hh = self.working_image_h
            if (y + h) > hh:
                im = im[:hh - y, :]
            www = self.cursor[2]
            if w > www:
                im = im[:, :www]
                w = www
            hhh = self.cursor[3]
            if h > hhh:
                im = im[:hhh, :]
                h = hhh
            self.working_image[y:y + h, x:x + w] = im
            # self.cut_buffer = tuple()

    def prewrite(self):
        """ Things to take care of before writing to the canvas.
        """
        im: str = self.snapshot()
        self.history.append(im)
        self.redo = list()

    def export_all(self):
        savname: str = os.path.splitext(self.load_file)[0] or "persist"
        dirname: str = f"{savname}_export"
        try:
            os.makedirs(dirname)
        except FileExistsError:
            shutil.rmtree(dirname)
            os.makedirs(dirname)

        padding = len(str(len(self.working_images)))
        namefmt = "{{0:s}}_{{1:0{}}}.png".format(padding)

        for nn, numpy_image in enumerate(self.working_images):
            working_palette = self.working_palettes[nn]
            w = numpy_image.shape[1]
            h = numpy_image.shape[0]
            outs = pygame.Surface((w, h), pygame.SRCALPHA, 32).convert_alpha()
            for m in range(h):
                for n in range(w):
                    palette_enum = self.get_pixel(numpy_image, m, n)
                    if palette_enum != self.working_transparencies[nn][working_palette]:
                        color = self.palettes[working_palette][palette_enum]
                        pygame.draw.rect(outs, color, (m, n, 1, 1))  # Pygame ver
            pygame.image.save(outs, os.path.join(dirname, namefmt.format(savname, nn)))  # Pygame ver

    def update(self):
        """ Accept user input.
        """
        self.clock.tick(60)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                # Quit pygame
                self.quit()
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    # Quit pygame
                    self.quit()
                elif e.key == pygame.K_SPACE:
                    # Swap canvas
                    if e.mod & pygame.KMOD_LSHIFT:
                        self.canvas_index -= 1
                        if self.canvas_index < 0:
                            self.canvas_index = self.num_canvases - 1
                    else:
                        self.canvas_index += 1
                        if self.canvas_index >= self.num_canvases:
                            self.canvas_index = 0
                elif e.key == pygame.K_UP:
                    if e.mod & pygame.KMOD_LSHIFT:
                        # Change brush size
                        self.cursor[2] -= 1
                        if self.cursor[2] < 1:
                            self.cursor[2] = 1
                            self.cursor[0] -= 1
                            if self.cursor[0] < 0:
                                self.cursor[0] = 0
                    elif e.mod & pygame.KMOD_ALT:
                        # Cycle palette
                        self.palette_index -= 1
                        if self.palette_index < 0:
                            self.palette_index = 3
                    else:
                        # Move brush
                        self.cursor[0] -= 1
                        if self.cursor[0] < 0:
                            self.cursor[0] = 0
                elif e.key == pygame.K_DOWN:
                    if e.mod & pygame.KMOD_LSHIFT:
                        # Change brush size
                        self.cursor[2] += 1
                        if self.cursor[0] + self.cursor[2] > self.working_image_h:
                            self.cursor[2] = self.working_image_h - self.cursor[0]
                    elif e.mod & pygame.KMOD_ALT:
                        # Cycle palette
                        self.palette_index += 1
                        if self.palette_index > 3:
                            self.palette_index = 0
                    else:
                        # Move brush
                        self.cursor[0] += 1
                        if self.cursor[0] + self.cursor[2] > self.working_image_h:
                            self.cursor[0] = self.working_image_h - self.cursor[2]
                elif e.key == pygame.K_LEFT:
                    if e.mod & pygame.KMOD_LSHIFT:
                        # Change brush size
                        self.cursor[3] -= 1
                        if self.cursor[3] < 1:
                            self.cursor[3] = 1
                            self.cursor[1] -= 1
                            if self.cursor[1] <= 0:
                                self.cursor[1] = 0
                    elif e.mod & pygame.KMOD_ALT:
                        self.working_palette -= 1
                    else:
                        # Move brush
                        self.cursor[1] -= 1
                        if self.cursor[1] <= 0:
                            self.cursor[1] = 0
                elif e.key == pygame.K_RIGHT:
                    if e.mod & pygame.KMOD_LSHIFT:
                        # Change brush size
                        self.cursor[3] += 1
                        if self.cursor[1] + self.cursor[3] > self.working_image_w:
                            self.cursor[3] = self.working_image_w - self.cursor[1]
                    elif e.mod & pygame.KMOD_ALT:
                        self.working_palette += 1
                    else:
                        # Move brush
                        self.cursor[1] += 1
                        if self.cursor[1] + self.cursor[3] > self.working_image_w:
                            self.cursor[1] = self.working_image_w - self.cursor[3]
                elif e.key == pygame.K_x:
                    if e.mod & pygame.KMOD_LSHIFT:
                        # Cut
                        self.prewrite()
                        self.cut()
                        self.snapshot()
                    else:
                        # Draw
                        if len(self.history) >= ImageEditor.HISTORY:
                            self.history = self.history[::-1][:ImageEditor.HISTORY-1][::-1]
                        self.prewrite()
                        self.set_pixel(self.palette_index, self.cursor[1], self.cursor[0])
                        self.snapshot()
                elif e.key == pygame.K_c:
                    if e.mod & pygame.KMOD_LSHIFT:
                        # Copy
                        self.cut(preserve=True)
                elif e.key == pygame.K_v:
                    if e.mod & pygame.KMOD_LSHIFT:
                        # Paste
                        self.prewrite()
                        self.paste()
                        self.snapshot()
                elif e.key == pygame.K_z:
                    if e.mod & pygame.KMOD_LSHIFT:
                        # Undo
                        self.swap(self.history, self.redo)
                elif e.key == pygame.K_e:
                    if e.mod & pygame.KMOD_LSHIFT:
                        self.export_all()
                elif e.key == pygame.K_r:
                    if e.mod & pygame.KMOD_LSHIFT:
                        # Redo
                        self.swap(self.redo, self.history)
                elif e.key == pygame.K_n:
                    # Copy
                    pc.copy(self.snapshot())
                elif e.key == pygame.K_m:
                    # Paste
                    self.prewrite()
                    self.import_image(pc.paste())
                    self.snapshot()
                elif e.key == pygame.K_a:
                    # Maximize brush
                    self.cursor[0] = 0
                    self.cursor[1] = 0
                    self.cursor[2] = self.working_image_h
                    self.cursor[3] = self.working_image_w
                elif e.key == pygame.K_s:
                    if e.mod & pygame.KMOD_LSHIFT:
                        # Save
                        self.save()
                    else:
                        # Minimize brush
                        self.cursor[2] = 1
                        self.cursor[3] = 1
                elif e.key == pygame.K_g:
                    if e.mod & pygame.KMOD_LSHIFT:
                        # Toggle pixel grid display
                        self.pixel_grid = not self.pixel_grid
                elif e.key == pygame.K_t:
                    palette = self.working_palettes[self.canvas_index]
                    xx = self.working_transparencies[self.canvas_index][palette]
                    if xx != self.palette_index:
                        self.working_transparencies[self.canvas_index][palette] = self.palette_index
                    else:
                        self.working_transparencies[self.canvas_index][palette] = -1


def main():
    #ie = ImageEditor(16, 16, 16, multi_preview=[4, 4])
    #ie = ImageEditor(8, 8, 16, multi_preview=[4, 4])
    ie = ImageEditor(16, 16, 49, multi_preview=[7, 7], load_file="persist2.txt")
    #ie = ImageEditor(8, 8, 49, multi_preview=[7, 7], load_file="persist1.txt")
    #ie = ImageEditor(0, 0, 0)
    while True:
        ie.update()
        ie.render()



if __name__ == "__main__":
    main()
