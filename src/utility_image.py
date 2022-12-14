import pygame
import re
import numpy as np
from typing import Dict, List

class ImageUtil:
    """ Utility methods to transform text-formatted images to pygame/SDL bitmap surfaces.
    """

    DEFAULT_PALETTE_0: List[int] = [255, 255, 255]
    DEFAULT_PALETTE_1: List[int] = [170, 170, 170]
    DEFAULT_PALETTE_2: List[int] = [85, 85, 85]
    DEFAULT_PALETTE_3: List[int] = [0, 0, 0]

    PALETTE_A_0: List[int] = [255, 255, 255]
    PALETTE_A_1: List[int] = [170, 170, 170]
    PALETTE_A_2: List[int] = [85, 85, 85]
    PALETTE_A_3: List[int] = [0, 0, 0]

    PALETTE_B_0: List[int] = [255, 255, 255]
    PALETTE_B_1: List[int] = [248, 152, 80]
    PALETTE_B_2: List[int] = [248, 56, 8]
    PALETTE_B_3: List[int] = [0, 0, 0]

    PALETTE_C_0: List[int] = [255, 255, 255]
    PALETTE_C_1: List[int] = [248, 152, 80]
    PALETTE_C_2: List[int] = [80, 72, 248]
    PALETTE_C_3: List[int] = [0, 0, 0]

    PALETTE_D_0: List[int] = [255, 255, 255]
    PALETTE_D_1: List[int] = [248, 152, 80]
    PALETTE_D_2: List[int] = [56, 184, 24]
    PALETTE_D_3: List[int] = [0, 0, 0]

    PALETTE_E_0: List[int] = [255, 255, 255]
    PALETTE_E_1: List[int] = [248, 152, 80]
    PALETTE_E_2: List[int] = [120, 80, 24]
    PALETTE_E_3: List[int] = [0, 0, 0]

    PALETTE_F_0: List[int] = [255, 255, 255]
    PALETTE_F_1: List[int] = [96, 200, 8]
    PALETTE_F_2: List[int] = [40, 112, 0]
    PALETTE_F_3: List[int] = [56, 56, 56]

    PALETTE_G_0: List[int] = [255, 255, 255]
    PALETTE_G_1: List[int] = [192, 144, 56]
    PALETTE_G_2: List[int] = [160, 120, 24]
    PALETTE_G_3: List[int] = [56, 56, 56]

    PALETTE_H_0: List[int] = [255, 255, 255]
    PALETTE_H_1: List[int] = [64, 104, 152]
    PALETTE_H_2: List[int] = [0, 88, 104]
    PALETTE_H_3: List[int] = [0, 0, 0]

    PALETTE_I_0: List[int] = [255, 255, 255]
    PALETTE_I_1: List[int] = [96, 72, 120]
    PALETTE_I_2: List[int] = [64, 32, 40]
    PALETTE_I_3: List[int] = [0, 0, 0]

    @staticmethod
    def convert_image(inputs: str, palette: Dict[int, List[int]], w: int, h: int) -> pygame.Surface:
        """ Converts a string to a pygame surface.
        """
        image: np.ndarray = ImageUtil.deserialize(inputs, w, h)
        k = np.array(list(palette.keys()))
        v = np.array(list(palette.values()))
        mapping_ar = np.zeros((k.max() + 1, 3), dtype=v.dtype)
        mapping_ar[k] = v
        out = mapping_ar[image]
        return pygame.surfarray.make_surface(out)

    @staticmethod
    def deserialize(inputs: str, w: int, h: int) -> np.ndarray:
        """ Converts an image string to a numpy array.
        """
        hexstring = ImageUtil.hydrate(inputs)
        image: np.ndarray = np.zeros((w, h), dtype=np.int8)
        cursor: int = 0
        for y in range(0, w, 2):
            for x in range(0, h, 2):
                substring = hexstring[cursor:cursor + 2]
                cursor += 2
                f = bytes.fromhex(substring)
                e = int.from_bytes(f, 'big')
                a = (e & 0b11000000) >> 6
                b = (e & 0b00110000) >> 4
                c = (e & 0b00001100) >> 2
                d = (e & 0b00000011)
                g = np.array([[a, b], [c, d]])
                image[y:y + 2, x:x + 2] = g
        return image

    @staticmethod
    def hex_to_rgb(hexstr: str) -> List[int]:
        """ Converts a hexadecimal string to an [R,G,B] color list.
        """
        hexstr = hexstr.lstrip("#")
        if len(hexstr) == 3:
            hexstr = hexstr[0] * 2 + hexstr[1] * 2 + hexstr[2] * 2
        return [int(hexstr[i:i + 2], 16) for i in (0, 2, 4)]

    @staticmethod
    def dessicate(image: str) -> str:
        """ 'Shrinks' an image string.
        """
        # Simple pairwise character compression
        image = image.replace("00", "g")
        image = image.replace("11", "h")
        image = image.replace("22", "i")
        image = image.replace("33", "j")
        image = image.replace("44", "k")
        image = image.replace("55", "m")
        image = image.replace("66", "n")
        image = image.replace("77", "p")
        image = image.replace("88", "q")
        image = image.replace("99", "r")
        image = image.replace("aa", "s")
        image = image.replace("bb", "t")
        image = image.replace("cc", "u")
        image = image.replace("dd", "v")
        image = image.replace("ee", "w")
        image = image.replace("ff", "x")
        image = image.replace("gg", "G")
        image = image.replace("hh", "H")
        image = image.replace("ii", "I")
        image = image.replace("jj", "J")
        image = image.replace("kk", "K")
        image = image.replace("mm", "M")
        image = image.replace("nn", "N")
        image = image.replace("pp", "P")
        image = image.replace("qq", "Q")
        image = image.replace("rr", "R")
        image = image.replace("ss", "S")
        image = image.replace("tt", "T")
        image = image.replace("uu", "U")
        image = image.replace("vv", "V")
        image = image.replace("ww", "W")
        image = image.replace("xx", "X")

        # Collapse repeating sequences
        for n in range(2, 5):
            _re1 = r"({})\1+".format(r"\w" * n)
            for _1 in re.findall(_re1, image):
                _2 = r"({})".format(_1) + "{2,}"
                _3 = re.search(_2, image)
                if _3:
                    image = re.sub(_2, "({},{})".format(_1,((_3.regs[0][1] - _3.regs[0][0]) // n)), image, 1)

        return image

    @staticmethod
    def hydrate(image: str) -> str:
        """ 'Grows' an image string.
        """
        # Expand repeating sequences
        for n in range(4, 1, -1):
            _re1 = r"\(({}),(\d+)\)".format(r"\w" * n)
            for _1 in re.findall(_re1, image):
                _2 = _1[0]
                _3 = int(_1[1])
                image = re.sub(r"\({},{}\)".format(_2, _3), _2 * _3, image, 1)

        # Simple expansion of pairwise characters
        image = image.replace("X", "xx")
        image = image.replace("W", "ww")
        image = image.replace("V", "vv")
        image = image.replace("U", "uu")
        image = image.replace("T", "tt")
        image = image.replace("S", "ss")
        image = image.replace("R", "rr")
        image = image.replace("Q", "qq")
        image = image.replace("P", "pp")
        image = image.replace("N", "nn")
        image = image.replace("M", "mm")
        image = image.replace("K", "kk")
        image = image.replace("J", "jj")
        image = image.replace("I", "ii")
        image = image.replace("H", "hh")
        image = image.replace("G", "gg")
        image = image.replace("x", "ff")
        image = image.replace("w", "ee")
        image = image.replace("v", "dd")
        image = image.replace("u", "cc")
        image = image.replace("t", "bb")
        image = image.replace("s", "aa")
        image = image.replace("r", "99")
        image = image.replace("q", "88")
        image = image.replace("p", "77")
        image = image.replace("n", "66")
        image = image.replace("m", "55")
        image = image.replace("k", "44")
        image = image.replace("j", "33")
        image = image.replace("i", "22")
        image = image.replace("h", "11")
        image = image.replace("g", "00")

        return image

    @staticmethod
    def new_palette(a: List[int], b: List[int], c: List[int], d: List[int]) -> Dict[int, List[int]]:
        """ Creates a new palette from four colors (ordered).
        """
        return {0: a, 1: b, 2: c, 3: d}

    @staticmethod
    def numpy_image_to_string(working_image: np.ndarray) -> str:
        output = str()
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
