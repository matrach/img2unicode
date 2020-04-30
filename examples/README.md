| Optimizer name | Constructor | Chars | Setup time |
| -------------- | ----------- | ----- | ---------- |
| gamma/space | (SpaceDualOptimizer()) | 1 | 0.0000s |
| gamma/half | (HalfBlockDualOptimizer()) | 1 | 0.0000s |
| gamma/quad | (FastQuadDualOptimizer()) | 7 | 0.0002s |
| gamma/fast-block | (FastGenericDualOptimizer(slice(0x2580, 0x259F+1))) | 32 | 0.0327s |
| gamma/fast-ascii | (FastGenericDualOptimizer(slice(0x32, 127))) | 77 | 0.0326s |
| gamma/fast-all | (FastGenericDualOptimizer()) | 5577 | 0.0493s |
| gamma/exact-block | (ExactGenericDualOptimizer(slice(0x2580, 0x259F + 1))) | 32 | 0.0323s |
| gamma/fast-noblock | (FastGammaOptimizer(charmask=no_block_mask)) | 5554 | 0.6563s |
| gamma/exact-noblock | (ExactGammaOptimizer(charmask=no_block_mask)) | 5554 | 0.2332s |
| gamma/basic-noblock | (BasicGammaOptimizer(charmask=no_block_mask)) | 5554 | 0.1065s |
| gamma/fast-noblock-bw | (FastGammaOptimizer(charmask=no_block_mask, use_color=False)) | 5554 | 0.6405s |
| gamma/exact-ascii-bw | (ExactGammaOptimizer(charmask=ascii_mask, use_color=False)) | 95 | 0.1084s |

| Renderer | Optimizer | Time | Result |
| -------- | --------- | ---- | ------ |
| Renderer | dual/space | 0.2223s | ![](obama/dual/space.png) | 
| Renderer | dual/half | 0.2152s | ![](obama/dual/half.png) | 
| Renderer | dual/quad | 0.2427s | ![](obama/dual/quad.png) | 
| Renderer | dual/exact-block | 1.8685s | ![](obama/dual/exact-block.png) | 
| Renderer | dual/fast-block | 0.2739s | ![](obama/dual/fast-block.png) | 
| Renderer | dual/fast-all | 6.1598s | ![](obama/dual/fast-all.png) | 
| Renderer | dual/fast-ascii | 0.3410s | ![](obama/dual/fast-ascii.png) | 
| GammaRenderer | gamma/fast-noblock | 1.2404s | ![](obama/gamma/fast-noblock.png) | 
| GammaRenderer | gamma/exact-noblock | 17.1551s | ![](obama/gamma/exact-noblock.png) | 
| GammaRenderer | gamma/basic-noblock | 39.5970s | ![](obama/gamma/basic-noblock.png) | 
| GammaRenderer | gamma/fast-noblock-bw | 0.6616s | ![](obama/gamma/fast-noblock-bw.png) | 
| GammaRenderer | gamma/exact-ascii-bw | 3.1052s | ![](obama/gamma/exact-ascii-bw.png) | 
| Renderer | dual/space | 0.2291s | ![](matplotlib/dual/space.png) | 
| Renderer | dual/half | 0.2304s | ![](matplotlib/dual/half.png) | 
| Renderer | dual/quad | 0.2427s | ![](matplotlib/dual/quad.png) | 
| Renderer | dual/fast-block | 0.2786s | ![](matplotlib/dual/fast-block.png) | 
| Renderer | dual/fast-ascii | 0.3525s | ![](matplotlib/dual/fast-ascii.png) | 
| Renderer | dual/fast-all | 4.9054s | ![](matplotlib/dual/fast-all.png) | 
| Renderer | dual/exact-block | 1.5077s | ![](matplotlib/dual/exact-block.png) | 
| GammaRenderer | gamma/fast-noblock | 1.0009s | ![](matplotlib/gamma/fast-noblock.png) | 
| GammaRenderer | gamma/exact-noblock | 6.7828s | ![](matplotlib/gamma/exact-noblock.png) | 
| GammaRenderer | gamma/basic-noblock | 31.1373s | ![](matplotlib/gamma/basic-noblock.png) | 
| GammaRenderer | gamma/fast-noblock-bw | 0.5534s | ![](matplotlib/gamma/fast-noblock-bw.png) | 
| GammaRenderer | gamma/exact-ascii-bw | 2.4228s | ![](matplotlib/gamma/exact-ascii-bw.png) | 
-----------------------------------------------------------
