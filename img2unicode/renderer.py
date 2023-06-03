import io
import logging
from pathlib import Path

import PIL
import PIL.Image
import numpy as np
import skimage.filters
import skimage.transform
import skimage.feature
import skimage

from img2unicode.templates import DEFAULT_TEMPLATES
from img2unicode.utils import uncubify, open_or_pass

DEFAULT_SENTINEL = '\N{LEFT-TO-RIGHT OVERRIDE}' # '\u202D'

def term_fore(fg):
    fore = "\x1b[38;2;{};{};{}m".format(*list(fg))
    return fore

def float_rgb2term_fore(fg):
    fore =  list((fg*255).astype('uint8'))
    return term_fore(fore)

def term_back(back):
    back = "\x1b[48;2;{};{};{}m".format(*list(back))
    return back


def float_rgb2term_back(bg):
    back = list((bg*255).astype('uint8'))
    return term_back(back)

def term_reset():
    return "\x1b[0m"

class Renderer:
    def __init__(self, default_optimizer=None, max_w=None, max_h=None, allow_upscale=False):
        self.default_optimizer = default_optimizer
        self.max_w = max_w
        self.max_h = max_h
        self.allow_upscale = allow_upscale


    def _resize(self, img):
        w, h = img.size
        ratio = 8 if self.allow_upscale else 1
        if self.max_w is not None:
            ratio = min(ratio, (self.max_w*8) / w)
        if self.max_h is not None:
            ratio = min(ratio, (self.max_h*16) / h)
        return img.resize((round(w*ratio), round(h*ratio)), PIL.Image.LANCZOS)

    def _ensure_image(self, path_or_img):
        if isinstance(path_or_img, PIL.Image.Image):
            img = path_or_img
        elif isinstance(path_or_img, (str, Path)):
            img = PIL.Image.open(path_or_img)
        elif isinstance(path_or_img, np.ndarray):
            img = PIL.Image.fromarray(path_or_img)
        elif isinstance(path_or_img, bytes):
            img = PIL.Image.open(io.BytesIO(path_or_img))
        else:
            raise ValueError("Cannot interpret %s as image" % path_or_img)

        return self._resize(img).convert('RGB')

    def _prepare_image(self, img):
        ims = skimage.img_as_float32(img)
#         ims = skimage.transform.downscale_local_mean(ims, (downscale, downscale, 1))
        ims = skimage.filters.gaussian(ims, 1, channel_axis=-1)
        ims = ims[:ims.shape[0]-(ims.shape[0]%16), :ims.shape[1]-(ims.shape[1]%8)]
        return ims

    def optimize(self, path_or_img, optimizer=None, invert=False):
        if optimizer is None:
            optimizer = self.default_optimizer

        img = self._prepare_image(self._ensure_image(path_or_img))

        chars, fgs, bgs = optimizer.optimize_chunk(img)
        return img, chars, fgs, bgs

    @staticmethod
    def print_to_terminal(file, chars, fgs, bgs, sentinel=DEFAULT_SENTINEL):
        with open_or_pass(file, 'w') as f:
            for y in range(chars.shape[0]):
                for x in range(chars.shape[1]):
                    idx = y, x
                    res = chars[idx]

                    if fgs is not None:
                        fore = term_fore(fgs[idx])
                    else:
                        fore = ''
                    if bgs is not None:
                        back = term_back(bgs[idx])
                    else:
                        back = ''
                    # Add LTR override to fix Arabic script (\u202D)
                    prefix = sentinel
                    f.write(prefix + fore + back + chr(res))
                f.write(term_reset() + '\n')

    def render_terminal(self, path_or_img, file, optimizer=None, sentinel=DEFAULT_SENTINEL, **kwargs):
        chars, fgs, bgs = self.render_numpy(path_or_img, optimizer, **kwargs)
        self.print_to_terminal(file, chars, fgs, bgs, sentinel=sentinel)

    def render_numpy(self, path_or_img, optimizer=None, **kwargs):
        img, chars, fgs, bgs = self.optimize(path_or_img, optimizer, **kwargs)
        if fgs is not None:
            fgs = (255*fgs).astype('uint8')
        if bgs is not None:
            bgs = (255*bgs).astype('uint8')

        if len(chars.shape)==2:
            return chars, fgs, bgs
        new_shape = (img.shape[0]//16, img.shape[1]//8)
        chars = chars.reshape(new_shape)
        if fgs is not None:
            fgs = fgs.reshape(*new_shape, 3)
        if bgs is not None:
            bgs = bgs.reshape(*new_shape, 3)

        return chars, fgs, bgs

    def prerender(self, path_or_img, optimizer=None, templates=DEFAULT_TEMPLATES, show=False, **kwargs):
        img, chars, fgs, bgs = self.optimize(path_or_img, optimizer, **kwargs)

        cs_all = templates.base_16x8.clip(0., 1.)
        cs_all = cs_all.reshape(cs_all.shape[0], -1, 1)

        chars = chars.ravel()

        recov = cs_all[chars]
        if fgs is not None:
            recov = recov * fgs.reshape(-1, 1, 3)
        if bgs is not None:
            recov += (1-cs_all[chars])*bgs.reshape(-1, 1, 3)
        if recov.shape[-1] == 1:
            # no colors used?
            recov = np.tile(recov, (1, 1, 3))
        recov_img = uncubify(recov.reshape(-1, 16, 8, 3), img.shape).clip(0., 1.)

        if show:
            import matplotlib.pyplot as plt
            plt.figure(figsize=(20,10))
            plt.imshow(recov_img)
            plt.show()
            plt.close()

        return PIL.Image.fromarray(skimage.img_as_ubyte(recov_img))

class GammaRenderer(Renderer):
    def _prepare_image(self, img):

        imgl = skimage.img_as_float(img.convert('L'))
        imgl = skimage.filters.unsharp_mask(imgl, 3)
#         if downscale not in (0, 1):
#             imgl = skimage.transform.downscale_local_mean(imgl, (downscale,downscale))

        img_gray = skimage.filters.gaussian(imgl, 1, channel_axis=None)
#         img_gray = skimage.exposure.adjust_sigmoid(img_gray)
        img_edges = skimage.feature.canny(skimage.transform.downscale_local_mean(imgl, (2,2)), 1).astype('float')
        img_gray = img_gray[:img_gray.shape[0]-(img_gray.shape[0]%16), :img_gray.shape[1]-(img_gray.shape[1]%8)]


        imgc = skimage.img_as_float(img.convert('RGB'))
#         if downscale not in (0, 1):
#             imgc = skimage.transform.downscale_local_mean(imgc, (downscale,downscale,1))
        imgc = skimage.filters.gaussian(imgc, 1, channel_axis=-1)
        imgc = imgc[:imgc.shape[0]-(imgc.shape[0]%16), :imgc.shape[1]-(imgc.shape[1]%8)]


        return img_gray, img_edges, imgc

    def optimize(self, path_or_img, optimizer=None, invert=False):
        if optimizer is None:
            optimizer = self.default_optimizer

        img_gray, img_edges, imgc = self._prepare_image(self._ensure_image(path_or_img))
        if invert:
            img_gray = 1-img_gray
            img_edges = img_edges
            imgc = 1-imgc

        chars, fgs, bgs = optimizer.optimize_chunk(img_gray, img_edges, imgc)
        if invert:
            if fgs is not None:
                fgs = 1 - fgs
            if bgs is not None:
                bgs = 1 - bgs
        return imgc[:,:-8], chars, fgs, bgs
