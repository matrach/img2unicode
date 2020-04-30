import numpy as np
import os
import typing


class Templates:
    def __init__(self, base_16x16, edges_8x8=None, default_mask=None,
            raw_16x16=None):
        assert base_16x16.shape[1:] == (16, 16), base_16x16.shape
        self.base_16x16 = base_16x16
        assert edges_8x8 is None or edges_8x8.shape[1:] == (
            8, 8), edges_8x8.shape
        self._edges_8x8 = edges_8x8
        self.raw_16x16 = raw_16x16
        self.default_mask = default_mask if default_mask is not None else np.ones(
            len(base_16x16), dtype='bool')
        self.indexer = np.arange(len(base_16x16))

    @property
    def n_chars(self):
        return len(self.base_16x16)

    @property
    def base_16x8(self):
        return self.base_16x16[:, :, :8]

    @property
    def edges_8x8(self):
        if self._edges_8x8 is None:
            raise NotImplementedError("TODO compute edges")
        return self._edges_8x8

    @property
    def edges_8x4(self):
        raise NotImplementedError("TODO compute edges")

    @staticmethod
    def from_file(prefix):
        return Templates(**np.load(prefix + '.npz'))

    def save(self, prefix):
        np.savez_compressed(prefix + '.npz',
                            base_16x16=self.base_16x16,
                            edges_8x8=self.edges_8x8,
                            default_mask=self.default_mask,
                            raw_16x16=self.raw_16x16)


DEFAULT_TEMPLATES = Templates.from_file(
    os.path.join(os.path.dirname(__file__), 'Ubuntu Mono'))


def normalize_mask(mask: typing.Union[np.ndarray, slice], reference):
    if isinstance(mask, slice):
        new_mask = np.zeros_like(reference)
        new_mask[mask] = 1
        mask = new_mask
    elif mask is None:
        mask = reference

    return mask


def get_16x8_flat(templates=None, mask=None):
    if templates is None:
        templates = DEFAULT_TEMPLATES

    base = templates.base_16x8
    premask = templates.default_mask

    cs_all = base.reshape(base.shape[0], -1).clip(0, 1)
    mask = normalize_mask(mask, premask) & premask

    return cs_all[mask], templates.indexer[mask]


def get_16x16(templates=None, mask=None, return_edges=True):
    if templates is None:
        templates = DEFAULT_TEMPLATES
    base = templates.base_16x16
    edges = templates.edges_8x8
    premask = templates.default_mask
    mask = normalize_mask(mask, premask) & premask

    if return_edges:
        return base[mask], edges[mask], templates.indexer[mask]
    else:
        return base[mask], templates.indexer[mask]
