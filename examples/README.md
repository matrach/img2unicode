| Optimizer name | Constructor | Chars | Setup time |
| -------------- | ----------- | ----- | ---------- |
| dual/space | (SpaceDualOptimizer()) | 1 | 0.00s |
| dual/half | (HalfBlockDualOptimizer()) | 1 | 0.00s |
| dual/quad | (FastQuadDualOptimizer()) | 7 | 0.00s |
| dual/exact-block | (ExactGenericDualOptimizer("block")) | 24 | 0.03s |
| dual/fast-block | (FastGenericDualOptimizer("block")) | 24 | 0.04s |
| dual/fast-all | (FastGenericDualOptimizer()) | 4763 | 0.05s |
| dual/fast-ascii | (FastGenericDualOptimizer("ascii")) | 94 | 0.03s |
| gamma/fast-noblock | (FastGammaOptimizer(charmask="no_block")) | 4739 | 0.59s |
| gamma/exact-noblock | (ExactGammaOptimizer(charmask="no_block")) | 4739 | 0.24s |
| gamma/basic-noblock | (BasicGammaOptimizer(charmask="no_block")) | 4739 | 0.12s |
| gamma/fast-noblock-bw | (FastGammaOptimizer(charmask="no_block", use_color=False)) | 4739 | 0.58s |
| gamma/exact-ascii-bw | (ExactGammaOptimizer(charmask="ascii", use_color=False)) | 95 | 0.12s |

| Renderer | Optimizer | Time | Result |
| -------- | --------- | ---- | ------ |
| Renderer | dual/space | 0.22s | ![](obama/dual/space.png) |
| Renderer | dual/half | 0.21s | ![](obama/dual/half.png) |
| Renderer | dual/quad | 0.23s | ![](obama/dual/quad.png) |
| Renderer | dual/exact-block | 1.74s | ![](obama/dual/exact-block.png) |
| Renderer | dual/fast-block | 0.27s | ![](obama/dual/fast-block.png) |
| Renderer | dual/fast-all | 5.12s | ![](obama/dual/fast-all.png) |
| Renderer | dual/fast-ascii | 0.36s | ![](obama/dual/fast-ascii.png) |
| GammaRenderer | gamma/fast-noblock | 1.28s | ![](obama/gamma/fast-noblock.png) |
| GammaRenderer | gamma/exact-noblock | 19.09s | ![](obama/gamma/exact-noblock.png) |
| GammaRenderer | gamma/basic-noblock | 33.98s | ![](obama/gamma/basic-noblock.png) |
| GammaRenderer | gamma/fast-noblock-bw | 0.67s | ![](obama/gamma/fast-noblock-bw.png) |
| GammaRenderer | gamma/exact-ascii-bw | 3.21s | ![](obama/gamma/exact-ascii-bw.png) |
| Renderer | dual/space | 0.02s | ![](matplotlib/dual/space.png) |
| Renderer | dual/half | 0.02s | ![](matplotlib/dual/half.png) |
| Renderer | dual/quad | 0.02s | ![](matplotlib/dual/quad.png) |
| Renderer | dual/exact-block | 0.31s | ![](matplotlib/dual/exact-block.png) |
| Renderer | dual/fast-block | 0.04s | ![](matplotlib/dual/fast-block.png) |
| Renderer | dual/fast-all | 0.92s | ![](matplotlib/dual/fast-all.png) |
| Renderer | dual/fast-ascii | 0.05s | ![](matplotlib/dual/fast-ascii.png) |
| GammaRenderer | gamma/fast-noblock | 0.23s | ![](matplotlib/gamma/fast-noblock.png) |
| GammaRenderer | gamma/exact-noblock | 2.26s | ![](matplotlib/gamma/exact-noblock.png) |
| GammaRenderer | gamma/basic-noblock | 6.05s | ![](matplotlib/gamma/basic-noblock.png) |
| GammaRenderer | gamma/fast-noblock-bw | 0.10s | ![](matplotlib/gamma/fast-noblock-bw.png) |
| GammaRenderer | gamma/exact-ascii-bw | 0.53s | ![](matplotlib/gamma/exact-ascii-bw.png) |
