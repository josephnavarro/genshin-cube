#! usr/bin/env python3
import pygame
from typing import Dict, List, Tuple
from uuid import uuid4


class LevelInterface:
    __slots__ = [
        "block_entity",
        "block_image",
        "block_index",
        "block_position",
        "block_node",
        "block_rect",
        "block_label",
        "block_scale_new",
        "block_scale_old",
        "node_block",
        "field_position",
        "mouse_down",
        "mouse_dragging"
    ]

    def __init__(self):
        self.block_entity: Dict[str, str] = {}
        self.block_index: Dict[str, int] = {}
        self.block_image: Dict[str, str] = {}
        self.block_position: Dict[str, List[int, int]] = {}
        self.block_node: Dict[str, str] = {}
        self.block_rect: Dict[str, pygame.Rect] = {}
        self.block_label: Dict[str, str] = {}
        self.block_scale_new: Dict[str, float] = {}
        self.block_scale_old: Dict[str, float] = {}
        self.node_block: Dict[str, str] = {}
        self.field_position: List[int] = [0, 0]
        self.mouse_down: bool = False
        self.mouse_dragging: bool = False

    @property
    def blocks(self) -> List[str]:
        return list(self.block_entity.keys())

    def clear(self):
        """ Clears all local fields.
        """
        self.block_entity.clear()
        self.block_index.clear()
        self.block_image.clear()
        self.block_position.clear()
        self.block_node.clear()
        self.block_rect.clear()
        self.block_label.clear()
        self.block_scale_new.clear()
        self.block_scale_old.clear()
        self.node_block.clear()
        self.field_position = [0, 0]
        self.mouse_down = False
        self.mouse_dragging = False

    def block_create(self, s_label: str):
        """ Adds a newly-labeled block to the interface.
        """
        s_block: str = str(uuid4())
        self.block_entity[s_label] = s_block
        self.block_label[s_block] = s_label
        self.block_position[s_block] = [0, 0]
        self.block_index[s_block] = 0
        self.block_scale_new[s_block] = 1.0
        self.block_scale_old[s_block] = 1.0

    def block_get(self, s_label: str) -> str:
        """ Returns a block ID given its label.
        """
        return self.block_entity.get(s_label)

    def block_set_image(self, s_blocklabel: str, s_imagekey: str):
        """ Sets the image cycle for a given block.
        """
        s_block: str = self.block_entity.get(s_blocklabel)
        self.block_image[s_block] = s_imagekey

    def block_get_image(self, s_blocklabel: str) -> Tuple[str, int]:
        """ Returns the current image of a given block.
        """
        s_block: str = self.block_entity.get(s_blocklabel)
        i_index: int = self.block_index.get(s_block)
        s_keylabel: str = self.block_image.get(s_block)
        return s_keylabel, i_index

    def block_set_index(self, s_blocklabel: str, i_index: int):
        """ Sets the index of a given block.
        """
        s_block: str = self.block_entity.get(s_blocklabel)
        self.block_index[s_block] = i_index

    def block_set_node(self, s_blocklabel: str, s_nodelabel: str):
        """ Sets the system node for a given block.
        """
        s_block: str = self.block_entity.get(s_blocklabel)
        self.block_node[s_block] = s_nodelabel
        self.node_block[s_nodelabel] = s_block

    def block_get_node(self, s_blocklabel: str) -> str:
        """ Returns node label associated with the given block.
        """
        s_block = self.block_entity.get(s_blocklabel)
        return self.block_node.get(s_block)

    def block_set_position(self, s_label: str, i_x: int, i_y: int):
        """ Sets the topleft pixel coordinate of a given block.
        """
        s_block: str = self.block_entity.get(s_label)
        self.block_position[s_block] = [i_x, i_y]

    def block_get_position(self, s_label: str) -> List[int]:
        """ Returns the topleft pixel coordinate of a given block.
        """
        s_block: str = self.block_entity.get(s_label)
        return self.block_position.get(s_block)

    def block_set_rect(self, s_label: str, i_x: int, i_y: int, i_w: int, i_h: int):
        """ Sets the collision bounding box for a given block.
        """
        s_block: str = self.block_entity.get(s_label)
        self.block_rect[s_block] = pygame.Rect([i_x, i_y, i_w, i_h])

    def block_get_rect(self, s_label: str) -> pygame.Rect:
        """ Returns the collision bounding box for a given block.
        """
        s_block: str = self.block_entity.get(s_label)
        return self.block_rect.get(s_block)

    def block_get_label(self, s_key: str) -> str:
        """ Returns label of block given its ID.
        """
        return self.block_label.get(s_key)

    def block_get_scale_old(self, s_label: str) -> float:
        """ Returns the 'old' scaling of a given block.
        """
        s_block: str = self.block_get(s_label)
        return self.block_scale_old[s_block]

    def block_set_scale_old(self, s_label: str, f_scale: float) -> None:
        """ Sets the 'old' scaling of a given block.
        """
        s_block: str = self.block_get(s_label)
        self.block_scale_old[s_block] = f_scale

    def block_get_scale_new(self, s_label: str) -> float:
        """ Returns the 'new' scaling of a given block.
        """
        s_block: str = self.block_get(s_label)
        return self.block_scale_new[s_block]

    def block_set_scale_new(self, s_label: str, f_scale: float) -> None:
        """ Sets the 'new' scaling of a given block.
        """
        s_block: str = self.block_get(s_label)
        self.block_scale_new[s_block] = f_scale

    def node_get_block(self, s_nodelabel: str) -> str:
        """ Returns a block ID given its associated node label.
        """
        return self.node_block[s_nodelabel]
