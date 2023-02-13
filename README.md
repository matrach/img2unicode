# img2unicode
A tool to display images as Unicode in your terminal.
The library is currently optimized for Ubuntu Mono font rendered by libvte (Gnome Terminal, Terminator etc.) i.e. it works on stock Ubuntu.

````bash
pip install img2unicode
imgcat image.jpg
````

## Installation

You can install img2unicode via pip from PyPI:

```sh
$ pip install img2unicode
```

If you want to utilize `FastGammaOptimizer`,
install the optional n2 dependency:

```sh
$ pip install 'img2unicode[n2]'
```

Note that `ExactGammaOptimizer` is more portable, yet much slower.
Use `BestGammaOptimizer` alias to choose automatically between these two.

## Usage

```python
import img2unicode
# Use Unicode Block Elements
optimizer = img2unicode.FastGenericDualOptimizer("block")
renderer = img2unicode.Renderer(default_optimizer=optimizer, max_h=60, max_w=160)
renderer.render_terminal('examples/obama.jpg', 'obama-block.txt')

# Pair Renderer to Optimizer
optimizer = img2unicode.FastGammaOptimizer("no_block") # Or ExactGammaOptimizer
renderer = img2unicode.GammaRenderer(default_optimizer=optimizer, max_h=60, max_w=160)
renderer.render_terminal('examples/obama.jpg', 'obama-noblock.txt')

pil_image = renderer.prerender('examples/obama.jpg')
pil_image.save('obama-rendered.png')

# Use own mask: it may be name from common masks (see source), slice or numpy bool array.
ascii_optimizer = img2unicode.FastGammaOptimizer(slice(32, 127), use_color=False)
# Get the characters, foreground and background colors. Use non-default optimizer.
chars, fores, backs = renderer.render_numpy('examples/obama.jpg', optimizer=ascii_optimizer)
```

## Optimizers
Here is a quick comparison of the most usable optimizers:

| FastQuadDualOptimizer() |  FastGenericDualOptimizer ("block") | FastGammaOptimizer (charmask="no_block") | FastGammaOptimizer (charmask="no_block", use_color=False) |
| --- | --- | --- | ---
| Choses from 4-pixel characters like ▚ | Optimizes foreground/background for whole [Unicode Block Elements](https://en.wikipedia.org/wiki/Block_Elements). | Optimizes foreground color for all Unicode rendered in single cell. | Same, but does't use terminal colors. |
| ![](examples/obama/dual/quad.png) | ![](examples/obama/dual/fast-block.png) | ![](examples/obama/gamma/fast-noblock.png) | ![](examples/obama/gamma/fast-noblock-bw.png) |
| ![](examples/matplotlib/dual/quad.png) | ![](examples/matplotlib/dual/fast-block.png) | ![](examples/matplotlib/gamma/fast-noblock.png)  |  ![](examples/matplotlib/gamma/fast-noblock-bw.png) |
| Good color representation | Good color and crisper image | Crisp edges with black | Pure art, no color. |
| Foreground & background    | Foreground & background | Just foreground | No color |
| ~5Hz | ~4Hz | ~1Hz | ~2Hz |
| O(S*T), T=7 | O(S*T), T=24 | O(S*log(T)), T=5553 | O(S*log(T)), T=5553 |

Where `S` is the number of 16x8 pixel samples to optimize for and `T` is the number of templates.

## See it yourself

Use the included `termview` script to browse images with all renderers. First, install the optional dependency:

```sh
$ pip install 'img2unicode[termview]'
```

then execute:

```bash
termview examples/obama.jpg
```
![termview demo](examples/termview.gif)

or use `imgcat` to display an image in your terminal:

```bash
imgcat examples/obama.jpg
```


## More samples
To see how other optimizers compare to each other, see [examples/README.md](examples/README.md).

To see more eyecandy of photos, videos and plots, see the [matrach/img2unicode-demos repo](https://github.com/matrach/img2unicode-demos)

# How FastGammaOptimizer works

`img2unicode` employs optimization with (Approximate) Nearest Neighbors. For each chunk of an image (i.e. 16x32 px), the tool basically selects a glyph (from a prerendered dataset) that optimizes both:

- perceptual similarity (implemented as a pixel-by-pixel Euclidean distance between the blurred glyph template and the chunk),
- visually matching edges (as you can see in the Obama example).

The need to use ML arose from the need to support arbitrary Unicode glyphs. This is not easily portable while maintaining the rendering quality, because there is a lot of variability between rendering by different terminal backends (e.g., libvte, kitty, etc.) and fonts.

# Details of FastGenericDualOptimizer
The algorithm select characters when we control both background and foreground of each piece.

In a general case, when using characters with a grayscale channel and a [well-behaved color space such as LAB or HCL](https://www.youtube.com/watch?v=xAoljeRJ3lU), the algorithm should minimize the total deviation of each pixel from the selected template.

Let `cs` be a matrix of char template luma values -- an `(N, H*W)` float matrix called a mask, where `N` is the number of templates and `H, W` are the image chunk dimensions.
By $\lVert c \rVert^2$ I will indicate the error in pixel color rendering (squared euclidean distance -- $L_2$ loss function), and $\cdot$ will designate a mask-color combination.
Then, if `s` is an image chunk for rendering -- `(H*W, 3)` shaped matrix, my tool would optimize the following:
    $$argmin_{i \in 0,\ldots,N} \sum_{p=0}^{WH} \lVert cs_{i,p} \cdot fg_i + (1-cs_{i,p}) \cdot bg_i - s_p \rVert^2$$

where $fg$ and $bg$ are the calculated average foreground and background colors, respectively, as follows

$$fg_i = \frac{\sum_{p=0}^{WH} (cs_{i,p} \cdot s_p)}{\sum_{p=0}^{WH} cs_{i,p}}$$
$$bg_i = \frac{\sum_{p=0}^{WH} (1-cs_{i,p}) \cdot s_p)}{\sum_{p=0}^{WH} 1-cs_{i,p}}$$
    with the assumption, that $0/0$ is $0$. (For some reason, the $\Sigma$ is weirdly rendered by GitHub's MathJax).


In the special case that $cs_{i,p}$ is binary (either 0 or 1 - as in the case of Unicode block characters), the first formula may be written equivalently as
    $$argmin_{i \in 0,\ldots,N}~ \sum_{p=0}^{WH} \lVert cs_{i,p} \cdot fg_i  - s_p \rVert^2 + \sum_{p=0}^{WH} \lVert (1-cs_{i,p}) \cdot bg_i - s_p \rVert^2$$

But in this version, we may convert the initial optimization problem into just:
```math
argmax_i~ \lVert
\frac{
  \sum_p cs_{i,p}
}{
  \sqrt{\sum_p cs_{i,p}}
} \cdot s_p \rVert^2
+ \lVert
\frac{\sum_p (1-cs_{i,p})}{\sqrt{\sum_p 1-cs_{i,p}}}  \cdot s_p
\rVert^2
```
This formula allows us to precompute the
```math
C_{i,p} \equiv \frac{
  \sum_p cs_{i,p}
}{
  \sqrt{\sum_p cs_{i,p}}
} 
```
part as a matrix, (same $C'$ for $1-cs$).
And now we can rewrite the above formula as (using dot-products):
$$argmax_i \lVert C_i \cdot s \rVert ^2 + \lVert C'_i \cdot s \rVert ^2$$
This can be further simplified to matrix multiplication if we have multiple samples to optimize at the same time (the $S$ tensor has shapes ``(chunks, W*H, 3)``).
Then, the optimal characters are selected by calculating just:
```math 
best\_char(j, S) = (argmax_i  \lVert (C_i \cdot S \rVert^2+ \lVert C'_i \cdot S \rVert^2)_{j}
```
With a bit of juggling, this may be implemented as:

1. $Q$ = query matrix of image chunks ``(chunks, W*H, 3)``
2. $C$ = foreground template tensor with shape extended to ``(N, W*H, 3)``. $C'$ - same for background.
3. ``foreground_match = C.mat_mult(Q)**2`` - shaped ``(chunks, N, W*H)``
3. ``background_match = C'.mat_mul(Q)**2`` - shaped ``(chunks, N, W*H)``
4. ``scores = (foreground_match + background_match).sum(axis=2)`` shaped ``(chunks, N)``
5. ``best_char = scores.argmax(axis=1)`` -- highest scoring template -- a vector (list) of ``chunks`` integers of  ``0...N``.

All that remains is to average the pixels over the mask to compute the appropriate color for the background and foreground.



# TODO

  - [ ] write more docs, document code
  - [x] describe how dual optimizer works in readme
  - [ ] describe how gamma optimizer works in readme
  - [ ] solve foreground & background optimization sublinear in templates
  - [ ] add support for Unicode 13 Legacy Computing block
  - [ ] add support for edges optimization in FastDualGenericOptimizer
