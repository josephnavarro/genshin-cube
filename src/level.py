#! usr/bin/env python3
import pygame
import numpy as np
from typing import Dict, List, Set, Tuple
from src.block_system import BlockSystem
from src.level_image import LevelImage
from src.level_interface import LevelInterface
from src.renderer import Renderer
from src.render_context import RenderContext
from src.utility import Utility, ScriptParser


class Level:
    """ Synthesizes puzzle logic with external interfaces and everything else basically.
    """

    __slots__ = [
        "renderer",
        "system",
        "interface",
        "images",
        "background",
        "scale_changing",
        "cursor",
        "is_resetting"
    ]

    ANIMATE_SPEED: float = 6.0
    ANIMATE_PAUSE: float = 0.1
    BLOCK_ANCHOR: str = "center"

    def __init__(self, context: RenderContext):
        self.renderer = Renderer(context)
        self.system = BlockSystem()
        self.interface = LevelInterface()
        self.images = LevelImage()

        # TODO: MOVE INTO SOMETHING ELSE
        self.scale_changing: float = 0.0
        self.is_resetting: bool = False

        # TODO: MOVE INTO SOMETHING NICE
        # Gray gradient background generation
        def gray(im):
            im = 255 * (im / im.max())
            w, h = im.shape
            ret = np.empty((w, h, 3), dtype=np.uint8)
            ret[:, :, 2] = ret[:, :, 1] = ret[:, :, 0] = im
            return ret

        sw, sh = self.renderer.screen_size
        x = np.arange(0, sw)
        y = np.arange(0, sh)
        xx, yy = np.meshgrid(x, y)
        z = xx + yy
        z = 255 * z / z.max()
        z = gray(z)
        s = pygame.surfarray.make_surface(z)
        s = pygame.transform.smoothscale(s, (sw, sh))
        self.background = s

    @classmethod
    def from_script(cls, s: BlockSystem, i: LevelInterface, im: LevelImage, filename: str, *, headless=False):
        """ Interprets a level as defined within a script file. In-place.
        """
        s.clear()
        i.clear()
        im.clear()
        d: Dict[int, Tuple[Tuple[str], Tuple[str]]] = ScriptParser.parse(filename)
        l_keys: List[int] = Utility.dict_keys_in_order(d)
        for i_key in l_keys:
            t_statement: Tuple[Tuple[str], Tuple[str]] = d[i_key]
            t_header: Tuple[str] = t_statement[0]
            t_params: Tuple[str] = t_statement[1]
            if "SYSTEM" in t_header:
                if "CYCLE" in t_header:
                    if "ADD" in t_header:
                        s.cycle_add(t_params[0], t_params[1:])
                if "NODE" in t_header:
                    if "CREATE" in t_header:
                        s.node_create(t_params[0])
                    if "SETVALUE" in t_header:
                        s.node_set_value(t_params[0], t_params[1])
                    if "SETCYCLE" in t_header:
                        s.node_set_cycle(t_params[0], t_params[1])
                    if "SETIMMUNE" in t_header:
                        s.node_set_immune(t_params[0], Utility.stob(t_params[1]))
                    if "SETSTATIC" in t_header:
                        s.node_set_static(t_params[0], Utility.stob(t_params[1]))
                    if "SETTARGET" in t_header:
                        s.node_set_target(t_params[0], t_params[1])
                    if "LINKSINGLE" in t_header:
                        s.node_link_single(t_params[0], t_params[1])
                    if "LINKDOUBLE" in t_header:
                        s.node_link_double(t_params[0], t_params[1])
            if "INTERFACE" in t_header:
                if "BLOCK" in t_header:
                    if "CREATE" in t_header:
                        # Label
                        i.block_create(t_params[0])
                    if "SETIMAGE" in t_header:
                        # Label 1 (block), label 2 (image)
                        i.block_set_image(t_params[0], t_params[1])
                    if "SETNODE" in t_header:
                        # Label 1 (block), label 2 (node)
                        i.block_set_node(t_params[0], t_params[1])
                    if "SETPOSITION" in t_header:
                        # Label, x, y
                        i.block_set_position(t_params[0], int(t_params[1]), int(t_params[2]))
                    if "SETRECT" in t_header:
                        # Label, dx, dy, w, h
                        i.block_set_rect(
                              t_params[0],
                              int(t_params[1]),
                              int(t_params[2]),
                              int(t_params[3]),
                              int(t_params[4])
                        )
            if "IMAGE" in t_header and not headless:
                if "ADDIMAGE" in t_header:
                    # Label
                    im.image_add(t_params[0])
                if "ADDKEY" in t_header:
                    # Label
                    im.image_add_key(t_params[0])
                if "SETINDEX" in t_header:
                    # Label 1 (image), index, label 2 (mapped image)
                    im.image_set_index(t_params[0], int(t_params[1]), t_params[2])
                if "SETVALUE" in t_header:
                    # Label, value, width, height
                    im.image_set_value(t_params[0], t_params[1], int(t_params[2]), int(t_params[3]))

    def clear(self) -> None:
        self.system.clear()
        self.interface.clear()
        self.images.clear()
        self.scale_changing = 0.0

    def coordinate(self) -> None:
        """ Syncs a block system with a level interface.
        """
        for s_blocklabel in self.interface.blocks:
            s_nodelabel: str = self.interface.block_get_node(s_blocklabel)
            s_node: str = self.system.node_get(s_nodelabel)
            i_index: int = self.system.node_get_index(s_node)
            self.interface.block_set_index(s_blocklabel, i_index)

    def load_from_script(self, filename: str) -> None:
        """ Populates local level data (BlockSystem) as defined from a script file.
        """
        Level.from_script(self.system, self.interface, self.images, filename)
        self.coordinate()

    def press_block(self, x: int, y: int) -> None:
        """ Finds and presses a block, if any, at the given (x,y) coordinate.
        """
        if not self.system.is_solved() and not self.scale_changing:
            dx, dy = self.interface.field_position
            for s_blocklabel in self.interface.blocks:
                rect: pygame.Rect = self.interface.block_get_rect(s_blocklabel)
                setattr(rect, Level.BLOCK_ANCHOR, self.interface.block_get_position(s_blocklabel))
                if rect.collidepoint(x - dx, y - dy):
                    s_nodelabel: str = self.interface.block_get_node(s_blocklabel)
                    self.system.node_hit(s_nodelabel)
                    self.start_block_animation(s_nodelabel)
                    break

    def start_block_animation(self, s_nodelabel: str) -> None:
        """ Sets variables to trigger block animation routine.
        """
        # Set target scale for affected blocks
        st_affects: Set[str] = self.system.node_get_affect(s_nodelabel)
        for s_affected in st_affects:
            _s_nodelabel: str = self.system.node_get_label(s_affected)
            _b_nodestatic: bool = self.system.node_get_static(_s_nodelabel)
            if not _b_nodestatic:
                _s_blockkey: str = self.interface.node_get_block(_s_nodelabel)
                _s_blocklabel: str = self.interface.block_get_label(_s_blockkey)
                self.interface.block_set_scale_new(_s_blocklabel, 0.0)

        # Set target scale for selected block
        _b_nodestatic: bool = self.system.node_get_static(s_nodelabel)
        _b_nodeimmune: bool = self.system.node_get_immune(s_nodelabel)
        if not (_b_nodestatic or _b_nodeimmune):
            _s_blockkey: str = self.interface.node_get_block(s_nodelabel)
            _s_blocklabel: str = self.interface.block_get_label(_s_blockkey)
            self.interface.block_set_scale_new(_s_blocklabel, 0.0)

        self.scale_changing = 1.0

    def animate_blocks(self, dt: float) -> None:
        """ Does the flipping animation for the blocks (well, tiles now).
        """
        has_changing: bool = False
        if self.scale_changing:
            for s_blocklabel in self.interface.blocks:
                f_old: float = self.interface.block_get_scale_old(s_blocklabel)
                f_new: float = self.interface.block_get_scale_new(s_blocklabel)
                delta: float = Level.ANIMATE_SPEED * dt
                if f_old - f_new < -delta:
                    # Grow
                    self.interface.block_set_scale_old(s_blocklabel, f_old + delta)
                    has_changing = True
                    self.is_resetting = False
                elif f_old - f_new > delta:
                    # Shrink
                    self.interface.block_set_scale_old(s_blocklabel, f_old - delta)
                    has_changing = True
                else:
                    if f_new == 0.0:
                        # Pause before transitioning over
                        if self.scale_changing < 1.0 + Level.ANIMATE_PAUSE:
                            self.interface.block_set_scale_old(s_blocklabel, 0.02)  # Arbitrarily small (1px thick)
                            if not has_changing:
                                self.scale_changing += dt
                        else:
                            self.interface.block_set_scale_new(s_blocklabel, 1.0)
                            self.coordinate()
                        has_changing = True
                    else:
                        # Done transitioning
                        self.interface.block_set_scale_old(s_blocklabel, 1.0)

        if not has_changing:
            self.scale_changing = 0.0

    def draw_background(self, dest: pygame.Surface) -> None:
        """ Renders background for current level.
        """
        if self.system.is_solved() and not self.scale_changing:
            dest.fill((0, 128, 0))
        elif self.is_resetting:
            dest.fill((128, 0, 0))
        else:
            dest.blit(self.background, (0, 0))

    def draw_blocks(self, dest: pygame.Surface) -> None:
        """ Renders all blocks in current level.
        """
        for s_blocklabel in self.interface.blocks:
            s_imglabel, i_index = self.interface.block_get_image(s_blocklabel)
            im_blockimg: pygame.Surface = self.images.image_get(s_imglabel, i_index)
            scale: float = self.interface.block_get_scale_old(s_blocklabel)
            if scale > 0:
                w, h = im_blockimg.get_size()
                new_w = int(round(w * scale))
                new_h = int(round(h * scale))
                im_blockimg = pygame.transform.scale(im_blockimg, (w, new_h))
            x, y = self.interface.block_get_position(s_blocklabel)
            x += self.interface.field_position[0]
            y += self.interface.field_position[1]
            anchor = Level.BLOCK_ANCHOR
            dest.blit(im_blockimg, im_blockimg.get_rect(**{anchor: (x, y)}))

    def render(self, dt: float) -> None:
        """ Once-per-frame render method.
        """
        dest = self.renderer.internal
        self.draw_background(dest)
        self.animate_blocks(dt)
        self.draw_blocks(dest)
        self.renderer.render_cursor(dest)
        self.renderer.flip()

    def reset(self):
        if not self.system.is_solved() and not self.scale_changing:
            for s_blocklabel in self.interface.blocks:
                s_nodelabel: str = self.interface.block_get_node(s_blocklabel)
                v_initial = self.system.node_get_initial(s_nodelabel)
                self.system.node_set_value(s_nodelabel, v_initial)
                self.interface.block_set_scale_new(s_blocklabel, 0.0)
            self.scale_changing = 1.0
            self.is_resetting = True

    def update(self) -> float:
        """ Once-per-frame update method.
        """
        dt: float = self.renderer.tick() / 1000.0

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                self.renderer.quit()
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    self.renderer.quit()
                elif e.key == pygame.K_r:
                    self.reset()
            elif e.type == pygame.MOUSEBUTTONDOWN:
                self.interface.mouse_down = True
            elif e.type == pygame.MOUSEBUTTONUP:
                if not self.interface.mouse_dragging:
                    x, y = e.pos
                    x, y = self.renderer.normalize(x, y)
                    self.press_block(x, y)
                self.interface.mouse_dragging = False
                self.interface.mouse_down = False
            elif e.type == pygame.MOUSEMOTION:
                if self.interface.mouse_down:
                    self.interface.mouse_dragging = True
                    dx, dy = e.rel
                    dx, dy = self.renderer.normalize(dx, dy)
                    self.interface.field_position[0] += dx
                    self.interface.field_position[1] += dy

        return dt



if __name__ == "__main__":
    c = RenderContext()
    l = Level(c)
    l.load_from_script("../res/DUMMY_2.CCP")
    while True:
        dt: float = l.update()
        l.render(dt)

