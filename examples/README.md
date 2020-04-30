| Optimizer name | Constructor | Chars | Setup time |
| -------------- | ----------- | ----- | ---------- |
| Initialization | dual/space | (SpaceDualOptimizer()) | 1 | 0.00s |
| Initialization | dual/half | (HalfBlockDualOptimizer()) | 1 | 0.00s |
| Initialization | dual/quad | (FastQuadDualOptimizer()) | 7 | 0.00s |
| Initialization | dual/exact-block | (ExactGenericDualOptimizer("block")) | 24 | 0.03s |
| Initialization | dual/fast-block | (FastGenericDualOptimizer("block")) | 24 | 0.03s |
| Initialization | dual/fast-all | (FastGenericDualOptimizer()) | 5577 | 0.05s |
| Initialization | dual/fast-ascii | (FastGenericDualOptimizer("ascii")) | 94 | 0.03s |
| Initialization | gamma/fast-noblock | (FastGammaOptimizer(charmask="no_block")) | 5553 | 0.64s |
| Initialization | gamma/exact-noblock | (ExactGammaOptimizer(charmask="no_block")) | 5553 | 0.23s |
| Initialization | gamma/basic-noblock | (BasicGammaOptimizer(charmask="no_block")) | 5553 | 0.11s |
| Initialization | gamma/fast-noblock-bw | (FastGammaOptimizer(charmask="no_block", use_color=False)) | 5553 | 0.64s |
| Initialization | gamma/exact-ascii-bw | (ExactGammaOptimizer(charmask="ascii", use_color=False)) | 95 | 0.10s |

| Renderer | Optimizer | Time | Result |
| -------- | --------- | ---- | ------ |
| Renderer | dual/space | 0.22s | ![](obama/dual/space.png) | 
| Renderer | dual/half | 0.21s | ![](obama/dual/half.png) | 
| Renderer | dual/quad | 0.23s | ![](obama/dual/quad.png) | 
| Renderer | dual/exact-block | 1.64s | ![](obama/dual/exact-block.png) | 
| Renderer | dual/fast-block | 0.29s | ![](obama/dual/fast-block.png) | 
| Renderer | dual/fast-all | 6.26s | ![](obama/dual/fast-all.png) | 
| Renderer | dual/fast-ascii | 0.36s | ![](obama/dual/fast-ascii.png) | 
| GammaRenderer | gamma/fast-noblock | 1.24s | ![](obama/gamma/fast-noblock.png) | 
| GammaRenderer | gamma/exact-noblock | 16.97s | ![](obama/gamma/exact-noblock.png) | 
| GammaRenderer | gamma/basic-noblock | 38.56s | ![](obama/gamma/basic-noblock.png) | 
| GammaRenderer | gamma/fast-noblock-bw | 0.67s | ![](obama/gamma/fast-noblock-bw.png) | 
| GammaRenderer | gamma/exact-ascii-bw | 3.19s | ![](obama/gamma/exact-ascii-bw.png) | 
| Renderer | dual/space | 0.23s | ![](matplotlib/dual/space.png) | 
| Renderer | dual/half | 0.23s | ![](matplotlib/dual/half.png) | 
| Renderer | dual/quad | 0.24s | ![](matplotlib/dual/quad.png) | 
| Renderer | dual/exact-block | 1.37s | ![](matplotlib/dual/exact-block.png) | 
| Renderer | dual/fast-block | 0.27s | ![](matplotlib/dual/fast-block.png) | 
| Renderer | dual/fast-all | 4.83s | ![](matplotlib/dual/fast-all.png) | 
| Renderer | dual/fast-ascii | 0.36s | ![](matplotlib/dual/fast-ascii.png) | 
| GammaRenderer | gamma/fast-noblock | 1.01s | ![](matplotlib/gamma/fast-noblock.png) | 
| GammaRenderer | gamma/exact-noblock | 6.95s | ![](matplotlib/gamma/exact-noblock.png) | 
| GammaRenderer | gamma/basic-noblock | 29.60s | ![](matplotlib/gamma/basic-noblock.png) | 
| GammaRenderer | gamma/fast-noblock-bw | 0.56s | ![](matplotlib/gamma/fast-noblock-bw.png) | 
| GammaRenderer | gamma/exact-ascii-bw | 2.37s | ![](matplotlib/gamma/exact-ascii-bw.png) |
