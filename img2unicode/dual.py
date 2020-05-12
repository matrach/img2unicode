"""Optimizers that use both foreground and background."""
from abc import ABC, abstractmethod, abstractproperty

import numpy as np
import skimage
import skimage.transform

from img2unicode.templates import get_16x8_flat
from img2unicode.utils import cubify


class BaseDualOptimizer(ABC):
    @abstractproperty
    def n_chars(self):
        pass

    def optimize_char(self, char):  # (16, 8) or (16, 8, 3) depending on optimizer
        return self.optimize_chunk(char)

    def optimize_chunk(self, img):  # (r*16, c*8) or (r*16, c*8, 3) depending on optimizer
        pieces = cubify(img, (16, 8) if len(img.shape) == 2 else (16, 8, 3))
        if hasattr(self, 'optimize_image'):
            return self.optimize_image(pieces)

        chars, fgs, bgs = zip(*[self.optimize_char(c) for c in pieces])
        return np.array(chars), np.array(fgs), np.array(bgs)


class HalfBlockDualOptimizer(BaseDualOptimizer):
    """This is very simple, since we use the block is predefined.

        We use the average color of the top 8x8 block for foreground and bottom 8x8 for background.
    """

    def __init__(self, *args):
        pass

    @property
    def n_chars(self):
        return 1

    def optimize_char(self, piece):
        s = piece.reshape(-1, 3)
        char = ord('▀')
        fc = s[:8].mean(axis=0)
        bg = s[8:].mean(axis=0)
        return char, fc, bg

    def optimize_chunk(self, img):
        min_img = skimage.transform.downscale_local_mean(img, (8, 8, 1))
        chars = np.ones_like(min_img[::2, :, 0], dtype='int') * ord('▀')
        return chars, min_img[::2], min_img[1::2]


class SpaceDualOptimizer(BaseDualOptimizer):
    """This is very simple, since we use only background color – the average color of 16x8 block."""

    def __init__(self, *args):
        pass

    @property
    def n_chars(self):
        return 1

    def optimize_char(self, piece):
        s = piece.reshape(-1, 3)
        char = ord(' ')
        fc = s.mean(axis=0)
        return char, fc, fc

    def optimize_chunk(self, img):
        min_img = skimage.transform.downscale_local_mean(img, (16, 8, 1))
        chars = np.ones_like(min_img[:, :, 0], dtype='int') * ord(' ')
        return chars, min_img, min_img


class FastQuadDualOptimizer(BaseDualOptimizer):
    """Here we use the same trick as in FastGenericDualOptimizer.

    The only difference is that we have homogenous pixels and each template is
    in reality 2x2 matrix. Therefore we reduce the input piece size to 2x2 by subsampling first.
    """
    QUADS = np.array([ord(c) for c in
                         '▀▌▖▗▘▝▚'])  # Minimal set to cover all options of quadrants

    # full block is achieved by setting the same fg and bg

    def __init__(self, _charmask=None, _templates=None):
        #         t16x8, indexer = get_16x8(templates, QUADS)
        #         masks = np.round(masks[:, 8*2+2::8*3+4]) # take a pixel from each quadrant
        masks = np.array([[1., 1., 0., 0.],
                             [1., 0., 1., 0.],
                             [0., 0., 1., 0.],
                             [0., 0., 0., 1.],
                             [1., 0., 0., 0.],
                             [0., 1., 0., 0.],
                             [1., 0., 0., 1.]])
        self.masks = masks
        self.db1 = np.nan_to_num(
            (masks / np.sqrt(np.sum(masks, axis=1))[:, np.newaxis]))
        self.db2 = np.nan_to_num(
            ((1 - masks) / np.sqrt(np.sum(1 - masks, axis=1))[:, np.newaxis]))

    @property
    def n_chars(self):
        return len(self.QUADS)

    def optimize_chunk(self, img):
        img = skimage.transform.downscale_local_mean(img, (8, 4, 1))
        imgc = cubify(img, (2, 2, 3)).reshape(-1, 4, 3)
        masks = self.masks

        best_char = np.argmax(
            ((self.db1 @ imgc) ** 2 + (self.db2 @ imgc) ** 2).sum(axis=2), 1)

        best_masks = masks[best_char][:, :, np.newaxis]

        # compute average color on mask (foreground) and complement (background)
        fg = np.sum(best_masks * imgc, axis=1) / best_masks.sum(axis=1)
        bg = np.sum((1 - best_masks) * imgc, axis=1) / (1 - best_masks).sum(
            axis=1)

        return self.QUADS[best_char], fg, bg

class ExactGenericDualOptimizer(BaseDualOptimizer):
    """Here we optimize the following function:

    cs - chars template (Nx16*8)
    x - image chunk to match (16*8, 3)
    $$argmin_i \sum_p (cs_{i,p} * fg_i + (1-cs_{i,p}) * bg_i - s_p)^2$$
    where fg and bg are, respectively, computed average foreground color and background color as follows:

    $$ fg_i = \frac{\sum_p (cs_{i,p} * s_p)}{\sum_p cs_{i,p}} == \frac{cs_i \cdot s}{|cs_i|}$$
    $$ bg_i = \frac{\sum_p ( (1-cs_{i,p}) * s_p)}{\sum_p 1-cs_{i,p}} == \frac{(1-cs_i) \cdot s}{|1-cs_i|} $$
    with the assumption, that 0/0 is 0.

    """

    def __init__(self, charmask=None, templates=None):
        cs, indexer = get_16x8_flat(templates, charmask)
        self.cs = cs
        self.indexer = indexer

    @property
    def n_chars(self):
        return len(self.cs)

    def optimize_char(self, piece):
        cs = self.cs
        s = piece.reshape(-1, 3)
        with np.errstate(divide='ignore', invalid='ignore'):
            fc = np.nan_to_num(
                np.clip((cs @ s) / cs.sum(axis=1)[:, np.newaxis], 0, 1))
            bg = np.nan_to_num(
                np.clip(((1 - cs) @ s) / (1 - cs).sum(axis=1)[:, np.newaxis], 0,
                        1))

        props = cs[:, :, np.newaxis] * fc[:, np.newaxis, :] + (1 - cs)[:, :,
        np.newaxis] * bg[:, np.newaxis, :]
        arr = np.abs(props - s) ** 2
        summ = np.sum(arr, axis=1).sum(axis=1)
        res = np.argsort(
            summ
        )

        idx = self.indexer[res[0]]
        return idx, fc[res[0]], bg[res[0]]

class FastGenericDualOptimizer(BaseDualOptimizer):
    """
        Here we optimize the following function:

        cs - chars templatse (N,16*8)
        x - image chunk to match (16*8,3)
        $$argmin_i \sum_p (cs_{i,p} * fg_i - s_p)^2 + \sum _p ((1-cs_{i,p}) * bg_i - s_p)^2$$

        where fg and bg are, respectively, computed average foreground color and background color as follows:
        fg_i = \frac{\sum_p (cs_{i,p} * s_p)}{\sum_p cs_{i,p}}
        bg_i = \frac{\sum_p ( (1-cs_{i,p}) * s_p)}{\sum_p 1-cs_{i,p}}
        with the assumption, that 0/0 is 0.

        In the special case that cs_{i,p} is binary (either 0 or 1), this is equivalent the the ExactGenericDualOptimizer.
        But in this version, we may convert the initial optimization problem into just:
        $$argmax_i (\sum_p cs_{i,p}/\sqrt{\sum_p cs_{i,p}}  * s_p)^2 + (\sum_p (1-cs_{i,p})/\sqrt{\sum_p 1-cs_{i,p}}  * s_p)^2$$
        Where we may precompute the $cs_{i,p}/\sqrt{\sum_p cs_{i,p}}$ part as [C]{i,p} matrix, (same C' for $1-cs$).
        And now we have just scalar products:

        $$ argmax_i (C_i * s)^2 + (C'_i * s)^2 $$
        Which can be further simplified to tensor multiplication if we have several s-es (S : (batch, 16*8, 3)):

        $$ char(j, S) = argmax_i ((C_i*S)^2+(C'_i*S)^2)_{i,j}$$

    """

    def __init__(self, charmask=None, templates=None, use_median=True):
        cs, indexer = get_16x8_flat(templates, charmask)
        self.cs = cs
        self.indexer = indexer
        self.use_median = use_median
        with np.errstate(divide='ignore', invalid='ignore'):
            self.cs1 = np.nan_to_num(
                (cs / np.sqrt(np.sum(cs, axis=1))[:, np.newaxis]))
            self.cs2 = np.nan_to_num(
                ((1 - cs) / np.sqrt(np.sum((1 - cs), axis=1))[:, np.newaxis]))

    @property
    def n_chars(self):
        return len(self.cs)

    def optimize_image(self, img):
        Q = img.reshape(-1, 16 * 8, 3)
        best_char = np.argmax(
            ((self.cs1 @ Q) ** 2 + (self.cs2 @ Q) ** 2).sum(axis=2), 1)
        best_masks = self.cs[best_char][:, :, np.newaxis]

        with np.errstate(divide='ignore', invalid='ignore'):
            if self.use_median:
                fg = (np.where(best_masks>0.5, 1, np.nan))*Q
                fg = np.nanmedian(fg, axis=1)
                bg = (np.where(best_masks<0.5, 1, np.nan))*Q
                bg = np.nanmedian(bg, axis=1)
            else:
                fg = np.clip(np.sum(best_masks * Q, axis=1) / best_masks.sum(axis=1), 0, 1)
                bg = np.clip(np.sum((1 - best_masks) * Q, axis=1) / (1 - best_masks).sum(axis=1), 0, 1)

            # Fix whole blocks with second color and vice versa
            fg = np.where(np.isnan(fg), bg, fg)
            bg = np.where(np.isnan(bg), fg, bg)

            fg = np.nan_to_num(fg)
            bg = np.nan_to_num(bg)

        return self.indexer[best_char], fg, bg


