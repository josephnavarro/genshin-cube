#! usr/bin/env python3
import pygame
import pyperclip as pc
import numpy as np
from typing import List, Tuple, Dict
from src.utility_image import ImageUtil


class ImageEditor:
    CAPTION: str = "Image Editor"
    FLAGS: int = pygame.DOUBLEBUF | pygame.HWSURFACE
    SCREEN_WIDTH: int = 640
    SCREEN_HEIGHT: int = 400
    DEFAULT_WIDTH: int = 32
    DEFAULT_HEIGHT: int = 32
    PIXEL_WIDTH: int = 9
    PIXEL_HEIGHT: int = 9
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
        "canvas_index",
        "cursor",
        "palette",
        "clipboards",
        "palette_index",
        "histories",
        "redos",
        "font",
        "cut_buffer",
        "pixel_grid",
        "multi_preview"
    ]

    def __init__(
          self,
          w: int = DEFAULT_WIDTH,
          h: int = DEFAULT_HEIGHT,
          num_canvases: int = NUM_CANVASES,
          *,
          multi_preview: List[int] = [0, 0],
          load_file: str = ""
    ):
        # Pygame stuff
        self.display, self.background = self.init_pygame()
        self.clock = pygame.time.Clock()

        # Load persistent data (if any)
        buffer = {}
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
            except FileNotFoundError:
                pass

        # Main variables
        self.pixel_grid: bool = False
        self.num_canvases: int = num_canvases
        self.canvas_index: int = 0
        self.palette_index: int = 0
        self.cursor: List[int] = [0, 0, 1, 1]
        self.multi_preview: List[int] = multi_preview
        self.histories: List[List[str]] = [list() for _ in range(num_canvases)]
        self.redos: List[List[str]] = [list() for _ in range(num_canvases)]
        self.cut_buffer: Tuple[np.ndarray, int, int] = tuple()
        self.palette: Dict[int, List[int]] = {}
        self.font: Dict[str, pygame.Surface] = {}
        self.clipboards: List[str] = []

        # Create canvases
        self.working_images: List[np.ndarray] = [ImageEditor.new_image(h, w) for _ in range(num_canvases)]
        for k, v in buffer.items():
            image = ImageUtil.hydrate(v)
            image = ImageUtil.deserialize(image, self.working_image_w, self.working_image_h)
            self.working_images[k] = image

        # Finish up initialization
        self.init_canvases(buffer)
        self.init_clipboards()
        self.init_palette()
        self.init_font()

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
        s = pygame.transform.smoothscale(s, (ImageEditor.SCREEN_WIDTH, ImageEditor.SCREEN_HEIGHT))

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

    def init_palette(self):
        """ Initializes default palette.
        """
        self.palette = ImageUtil.new_palette(
              ImageUtil.DEFAULT_PALETTE_0,
              ImageUtil.DEFAULT_PALETTE_1,
              ImageUtil.DEFAULT_PALETTE_2,
              ImageUtil.DEFAULT_PALETTE_3
        )

    def init_font(self):
        """ Initializes default font.
        """
        self.font = {
            "0": ImageUtil.convert_image("fc(f0,2)f(30,2)fg0cjc03fu0cG03", self.palette, *ImageEditor.FONT_SIZE),
            "1": ImageUtil.convert_image("XXc(0f,2)0cg(f0,3)cXX", self.palette, *ImageEditor.FONT_SIZE),
            "2": ImageUtil.convert_image("fcxf0fg3u0f0cjuxu0c03xg", self.palette, *ImageEditor.FONT_SIZE),
            "3": ImageUtil.convert_image("f3Xfj3fcx0c3g0xu03cfg03", self.palette, *ImageEditor.FONT_SIZE),
            "4": ImageUtil.convert_image("xfcf3xfc0j3x03xjxGG", self.palette, *ImageEditor.FONT_SIZE),
            "5": ImageUtil.convert_image("(f0,2)xf(30,2)cx0cjuxu3fcfg03", self.palette, *ImageEditor.FONT_SIZE),
            "6": ImageUtil.convert_image("fc(f0,2)f(30,2)c0f0cjuxu0ufg03", self.palette, *ImageEditor.FONT_SIZE),
            "7": ImageUtil.convert_image("f0Xx03x(f0,2)jcgf0fg3Xf", self.palette, *ImageEditor.FONT_SIZE),
            "8": ImageUtil.convert_image("fcf3f0f(30,2)c0f0cjuxu0c03g03", self.palette, *ImageEditor.FONT_SIZE),
            "9": ImageUtil.convert_image("fcf0fff3030f330c33ff33cc0c000003", self.palette, *ImageEditor.FONT_SIZE),
            "a": ImageUtil.convert_image("Xxf3xU0cxUuxcfG", self.palette, *ImageEditor.FONT_SIZE),
            "b": ImageUtil.convert_image("(f0,3)fgf0c0f0c(xu,2)xcfg03", self.palette, *ImageEditor.FONT_SIZE),
            "c": ImageUtil.convert_image("Xf0f3xu0f0c(xu,2)xcfj03", self.palette, *ImageEditor.FONT_SIZE),
            "d": ImageUtil.convert_image("Xf0f3xu0f0c(xu,2)GG", self.palette, *ImageEditor.FONT_SIZE),
            "e": ImageUtil.convert_image("Xf0f3xu(0c,2)xUuxcfgcf", self.palette, *ImageEditor.FONT_SIZE),
            "f": ImageUtil.convert_image("XXxf030f0u0f030fcxf3xf", self.palette, *ImageEditor.FONT_SIZE),
            "g": ImageUtil.convert_image("fcf0ffff030f33cc33ff33cc00000003", self.palette, *ImageEditor.FONT_SIZE),
            "h": ImageUtil.convert_image("(f0,3)fgf0c0f0xfuXxcfG", self.palette, *ImageEditor.FONT_SIZE),
            "i": ImageUtil.convert_image("(XX,2)guGXX", self.palette, *ImageEditor.FONT_SIZE),
            "j": ImageUtil.convert_image("Xxf3Xx0cgug03XX", self.palette, *ImageEditor.FONT_SIZE),
            "k": ImageUtil.convert_image("(f0,3)fg(f0,2)c0Xc0j0xcxfcf", self.palette, *ImageEditor.FONT_SIZE),
            "l": ImageUtil.convert_image("XX(f0,3)f3(0f,3)0cXX", self.palette, *ImageEditor.FONT_SIZE),
            "m": ImageUtil.convert_image("xfc(f0,2)xu0f0xfu0f0xfcfG", self.palette, *ImageEditor.FONT_SIZE),
            "n": ImageUtil.convert_image("xfc(f0,2)xu0f0xfuXxcfG", self.palette, *ImageEditor.FONT_SIZE),
            "o": ImageUtil.convert_image("Xf0f3xu0f0c(xu,2)xcfg03", self.palette, *ImageEditor.FONT_SIZE),
            "p": ImageUtil.convert_image("f0f0f0f0030f030f33ff33ff0c003fff", self.palette, *ImageEditor.FONT_SIZE),
            "q": ImageUtil.convert_image("fcf0ffff030f33ff33ff33ff00000000", self.palette, *ImageEditor.FONT_SIZE),
            "r": ImageUtil.convert_image("fffcf0f0ffcf030fffccffffffcfffff", self.palette, *ImageEditor.FONT_SIZE),
            "s": ImageUtil.convert_image("fffff3fcffcc0cccffccccccffcfcf03", self.palette, *ImageEditor.FONT_SIZE),
            "t": ImageUtil.convert_image("fffffffff0c0f0f30f0c0f0cffcfffcf", self.palette, *ImageEditor.FONT_SIZE),
            "u": ImageUtil.convert_image("fffcf0f3ffcf0f0cffffffccffcc0003", self.palette, *ImageEditor.FONT_SIZE),
            "v": ImageUtil.convert_image("fffcf0ffffcf0f30ffffffc0ffcc003f", self.palette, *ImageEditor.FONT_SIZE),
            "w": ImageUtil.convert_image("fffcf0f3ffcf0f0cffcf0f3cffcc0003", self.palette, *ImageEditor.FONT_SIZE),
            "x": ImageUtil.convert_image("fffcfffcffcf3003ffffc0f3ffcc3f0c", self.palette, *ImageEditor.FONT_SIZE),
            "y": ImageUtil.convert_image("f0f0ffff0f0f33ccffff33cc00000003", self.palette, *ImageEditor.FONT_SIZE),
            "z": ImageUtil.convert_image("fffcfffcffccfc00ffcc000cffcc3fcc", self.palette, *ImageEditor.FONT_SIZE),
            "A": ImageUtil.convert_image("fff0f0f0c00f030f30ff33ffcf000000", self.palette, *ImageEditor.FONT_SIZE),
            "B": ImageUtil.convert_image("f0f0f0f0030c0f0c33ccffcc0c030003", self.palette, *ImageEditor.FONT_SIZE),
            "C": ImageUtil.convert_image("fff0f0ffc00f0f3033ffffcc0cffff03", self.palette, *ImageEditor.FONT_SIZE),
            "D": ImageUtil.convert_image("f0f0f0f0030f0f0c30ffffc0cf00003f", self.palette, *ImageEditor.FONT_SIZE),
            "E": ImageUtil.convert_image("f0f0f0f0030c0f0c33ccffcc33ffffcc", self.palette, *ImageEditor.FONT_SIZE),
            "F": ImageUtil.convert_image("f0f0f0f0030c0f0f33ccffff33ffffff", self.palette, *ImageEditor.FONT_SIZE),
            "G": ImageUtil.convert_image("fff0f0ffc00f0f3033ff33cc0cff0000", self.palette, *ImageEditor.FONT_SIZE),
            "H": ImageUtil.convert_image("f0f0f0f00f0c0f0fffccffff00000000", self.palette, *ImageEditor.FONT_SIZE),
            "I": ImageUtil.convert_image("f3fffffc30f0f0c0030f0f0c3fffffcf", self.palette, *ImageEditor.FONT_SIZE),
            "J": ImageUtil.convert_image("fffffcf3f3ffcf0c33ffffcc00000003", self.palette, *ImageEditor.FONT_SIZE),
            "K": ImageUtil.convert_image("f0f0f0f00f0c0f0ffc0330ff03ffcf00", self.palette, *ImageEditor.FONT_SIZE),
            "L": ImageUtil.convert_image("f0f0f0f00f0f0f0cffffffccffffffcf", self.palette, *ImageEditor.FONT_SIZE),
            "M": ImageUtil.convert_image("f0f0f0f0cf000f0fffc03fffc0000000", self.palette, *ImageEditor.FONT_SIZE),
            "N": ImageUtil.convert_image("f0f0f0f0cf000f0fffcf30ff00000030", self.palette, *ImageEditor.FONT_SIZE),
            "O": ImageUtil.convert_image("fcf0f0f3030f0f0c33ffffcc0c000003", self.palette, *ImageEditor.FONT_SIZE),
            "P": ImageUtil.convert_image("f0f0f0f0030c0f0f33ccffff0c03ffff", self.palette, *ImageEditor.FONT_SIZE),
            "Q": ImageUtil.convert_image("fcf0f0f3030f0f0c33ffccc00c00003c", self.palette, *ImageEditor.FONT_SIZE),
            "R": ImageUtil.convert_image("f0f0f0f0030c0f0f33ccffff0c030000", self.palette, *ImageEditor.FONT_SIZE),
            "S": ImageUtil.convert_image("fcf3fff3030cff0c33ccffcc0ccf0003", self.palette, *ImageEditor.FONT_SIZE),
            "T": ImageUtil.convert_image("f3ffffff30f0f0f0030f0f0f3fffffff", self.palette, *ImageEditor.FONT_SIZE),
            "U": ImageUtil.convert_image("f0f0f0f30f0f0f0cffffffcc00000003", self.palette, *ImageEditor.FONT_SIZE),
            "V": ImageUtil.convert_image("f0f0f3ff0f0f0cf3fffffc03000003ff", self.palette, *ImageEditor.FONT_SIZE),
            "W": ImageUtil.convert_image("f0f0f0f30f0f0c030f0f0cf300000003", self.palette, *ImageEditor.FONT_SIZE),
            "X": ImageUtil.convert_image("f0fffcf00f30030fffc0f3ff003f0c00", self.palette, *ImageEditor.FONT_SIZE),
            "Y": ImageUtil.convert_image("f0f3ffff0f0cf0f0fffc00000003ffff", self.palette, *ImageEditor.FONT_SIZE),
            "Z": ImageUtil.convert_image("f3fffff033ffc00c33c03fcc003fffcc", self.palette, *ImageEditor.FONT_SIZE),
            "(": ImageUtil.convert_image("XXfcGf303X0cXX", self.palette, *ImageEditor.FONT_SIZE),
            ")": ImageUtil.convert_image("XX30Xc0cfG3XXf", self.palette, *ImageEditor.FONT_SIZE),
            ",": ImageUtil.convert_image("XXXxfcXu03XX", self.palette, *ImageEditor.FONT_SIZE),
            " ": ImageUtil.convert_image("(XX,4)", self.palette, *ImageEditor.FONT_SIZE)
        }

    def quit(self):
        """ Safely quits pygame.
        """
        with open("persist.txt", "w") as f:
            f.write("canvas_w>>{}\n".format(self.working_image_w))
            f.write("canvas_h>>{}\n".format(self.working_image_h))
            f.write("num_canvases>>{}\n".format(self.num_canvases))
            for n in range(self.num_canvases):
                f.write("canvas_{}>>{}\n".format(n, self.export_nth_image(n)))
            f.write("multipreview_x>>{}\n".format(self.multi_preview[0]))
            f.write("multipreview_y>>{}\n".format(self.multi_preview[1]))

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
        output = ""
        for y in range(0, working_image.shape[0], 2):
            for x in range(0, working_image.shape[1], 2):
                slice2d = working_image[y:y + 2, x:x + 2]
                slice1d = slice2d.ravel(order='C')
                a = int(slice1d[0])
                b = int(slice1d[1])
                c = int(slice1d[2])
                d = int(slice1d[3])
                e = (a << 6) | (b << 4) | (c << 2) | d
                f = e.to_bytes(1, 'big')
                g = f.hex()
                output += g
        output = ImageUtil.dessicate(output)
        return output

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
        for m in range(working_image.shape[0]):
            for n in range(working_image.shape[1]):
                palette_enum = self.get_pixel(working_image, m, n)
                color = self.palette[palette_enum]
                pygame.draw.rect(dest, color, (x + m * scale_x, y + n * scale_y, scale_x, scale_y))
        return scale_x * working_image.shape[1], scale_y * working_image.shape[0]

    def draw_palette(self, dest: pygame.Surface) -> Tuple[int, int]:
        """ Renders the palette bar.
        """
        spacing_x: int = ImageEditor.PALETTE_WIDTH + ImageEditor.WIDGET_BUFFER
        spacing_y: int = ImageEditor.PALETTE_HEIGHT + ImageEditor.WIDGET_BUFFER
        dx: int = 0
        dy: int = 0

        for n, color in self.palette.items():
            dx = self.palette_offset_x
            dy = self.palette_offset_y + n * spacing_y
            rect = (dx, dy, ImageEditor.PALETTE_WIDTH, ImageEditor.PALETTE_HEIGHT)
            pygame.draw.rect(dest, (0, 0, 0), rect, 5)
            pygame.draw.rect(dest, (255, 255, 255), rect, 3)
            pygame.draw.rect(dest, color, rect)

            # Highlight the current color
            if n == self.palette_index:
                pygame.draw.rect(dest, (0, 0, 0), rect, 5)
                pygame.draw.rect(dest, (255, 255, 255), rect, 3)

        return dx + spacing_x, dy + spacing_y

    def draw_cursor(self, dest: pygame.Surface, x: int, y: int):
        """ Renders the brush cursor.
        """
        pygame.draw.rect(
              dest,
              (255, 255, 255), (
                  self.cursor[1] * ImageEditor.PIXEL_WIDTH + x - 1,
                  self.cursor[0] * ImageEditor.PIXEL_HEIGHT + y - 1,
                  self.cursor[3] * ImageEditor.PIXEL_WIDTH + 2,
                  self.cursor[2] * ImageEditor.PIXEL_HEIGHT + 2
              ), 3
        )
        pygame.draw.rect(
              dest,
              (0, 0, 0), (
                  self.cursor[1] * ImageEditor.PIXEL_WIDTH + x,
                  self.cursor[0] * ImageEditor.PIXEL_HEIGHT + y,
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

    def render(self):
        """ Toplevel rendering method.
        """
        self.display.blit(self.background, (0, 0))

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
                    except IndexError as e:
                        pass

        # Palette bar
        dx, dy = self.draw_palette(self.display)

        # 1:1 scale preview
        dx2, dy2 = self.preview_offset
        tx2 = dx2
        ty2 = max(dyc, dy) + ImageEditor.WIDGET_BUFFER
        tw2 = 0
        th2 = 0
        for n in range(self.num_canvases):
            canvas = self.working_images[n]
            th2 = canvas.shape[0]
            tw2 = canvas.shape[1]
            if tx2 >= ImageEditor.SCREEN_WIDTH:
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
        self.draw_text(self.display, "x {}".format(self.cursor[1]), dx, ImageEditor.WIDGET_BUFFER + ImageEditor.FONT_SIZE[0] * 0)
        self.draw_text(self.display, "y {}".format(self.cursor[0]), dx, ImageEditor.WIDGET_BUFFER + ImageEditor.FONT_SIZE[0] * 2)
        self.draw_text(self.display, "w {}".format(self.cursor[3]), dx, ImageEditor.WIDGET_BUFFER + ImageEditor.FONT_SIZE[0] * 4)
        self.draw_text(self.display, "h {}".format(self.cursor[2]), dx, ImageEditor.WIDGET_BUFFER + ImageEditor.FONT_SIZE[0] * 6)
        self.draw_text(
              self.display,
              "{},{}".format(self.working_image_w, self.working_image_h),
              dx, ImageEditor.WIDGET_BUFFER + ImageEditor.FONT_SIZE[0] * 8
        )

        # String preview
        dx0, dy0 = self.clipboard_offset
        dx1, dy1 = self.draw_text(self.display, self.clipboard, dx0, ty2 + th2 + ImageEditor.WIDGET_BUFFER)
        self.draw_text(
            self.display,
            "SPACE: Next canvas\nSHIFT + -SPACE: Previous canvas\nBAZ",
            dx0, dy1 + ImageEditor.WIDGET_BUFFER
        )

        pygame.display.flip()

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
        self.redo = []

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
                    # Minimize brush
                    self.cursor[2] = 1
                    self.cursor[3] = 1
                elif e.key == pygame.K_g:
                    if e.mod & pygame.KMOD_LSHIFT:
                        # Toggle pixel grid display
                        self.pixel_grid = not self.pixel_grid


def main():
    #ie = ImageEditor(16, 16, 16, multi_preview=[4, 4])
    ie = ImageEditor(8, 8, 128)
    # ie = ImageEditor(0, 0, 0, load_file="persist.txt")
    while True:
        ie.update()
        ie.render()



if __name__ == "__main__":
    main()
