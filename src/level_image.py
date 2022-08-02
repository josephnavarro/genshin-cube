#! usr/bin/env python3
import pygame
from uuid import uuid4
from typing import Dict, List
from src.utility_image import ImageUtil


class LevelImage:
    __slots__ = [
        "image_entity",
        "image_index",
        "image_value",
        "image_key",
        "image_dims",
        "image_cache",
        "palette",
        "font",
        "font_cache"
    ]

    def __init__(self):
        self.image_key: Dict[str, str] = {}
        self.image_entity: Dict[str, str] = {}
        self.image_index: Dict[str, Dict[int, str]] = {}
        self.image_value: Dict[str, str] = {}
        self.image_dims: Dict[str, List[int, int]] = {}
        self.image_cache: Dict[str, pygame.Surface] = {}
        self.palette: Dict[int, List[int]] = ImageUtil.new_palette(
              ImageUtil.DEFAULT_PALETTE_0,
              ImageUtil.DEFAULT_PALETTE_1,
              ImageUtil.DEFAULT_PALETTE_2,
              ImageUtil.DEFAULT_PALETTE_3
        )
        self.font: Dict[str, str] = {}
        self.font_cache: Dict[str, pygame.Surface] = {}

    def clear(self):
        """ Clears all local fields.
        """
        self.image_key.clear()
        self.image_entity.clear()
        self.image_index.clear()
        self.image_value.clear()
        self.image_dims.clear()
        self.image_cache.clear()
        self.font.clear()
        self.font_cache.clear()

    def image_add(self, s_label: str):
        """ Adds an image to the interface.
        """
        s_image: str = str(uuid4())
        self.image_entity[s_label] = s_image

    def image_add_key(self, s_label: str):
        """ Adds an image key.
        """
        s_key: str = str(uuid4())
        self.image_key[s_label] = s_key

    def image_get_dims(self, s_label: str) -> List[int]:
        """ Returns width and height associated with an image.
        """
        s_key: str = self.image_entity.get(s_label)
        return self.image_dims.get(s_key)

    def image_get_key(self, s_label: str) -> str:
        """ Returns an image key.
        """
        return self.image_key.get(s_label)

    def image_get_label(self, s_key: str, i_index: int) -> str:
        """ Returns the label mapped to an image key and index.
        """
        return self.image_index.get(s_key).get(i_index)

    def image_get_value(self, s_label: str) -> str:
        """ Returns an image string given its label.
        """
        s_image: str = self.image_entity.get(s_label)
        return self.image_value.get(s_image)

    def image_set_index(self, s_label: str, i_index: int, s_imagelabel: str):
        """ Maps an image string to an index.
        """
        s_key: str = self.image_key.get(s_label)
        try:
            d_index: Dict[int, str] = self.image_index[s_key]
            d_index[i_index] = s_imagelabel
        except KeyError:
            self.image_index[s_key] = {i_index: s_imagelabel}

    def image_set_value(self, s_label: str, s_value: str, i_w: int, i_h: int):
        """ Sets an image's value within this interface.
        """
        s_image: str = self.image_entity[s_label]
        self.image_value[s_image] = s_value
        self.image_dims[s_image] = [i_w, i_h]

    def image_get(self, s_label: str, i_index: int) -> pygame.Surface:
        """ Returns a string image given its key and index.
        """
        s_key: str = self.image_get_key(s_label)
        s_imglabel: str = self.image_get_label(s_key, i_index)
        try:
            return self.image_cache[s_imglabel]
        except KeyError:
            i_w, i_h = self.image_get_dims(s_imglabel)
            s_image: str = self.image_get_value(s_imglabel)
            self.image_cache[s_imglabel] = ImageUtil.convert_image(s_image, self.palette, i_w, i_h)
            return self.image_cache[s_imglabel]
