import time

from img2unicode import *
from pathlib import Path

print("""
| Optimizer name | Constructor | Chars | Setup time |
| -------------- | ----------- | ----- | ---------- |
""")

images = ['obama.jpg', 'matplotlib.png']
dual_optimizers = {
    'space': 'SpaceDualOptimizer()',
    'half': 'HalfBlockDualOptimizer()',
    'quad': 'FastQuadDualOptimizer()',
    'exact-block': 'ExactGenericDualOptimizer(slice(0x2580, 0x259F + 1))',
    'fast-block': 'FastGenericDualOptimizer(slice(0x2580, 0x259F+1))',
    'fast-all': 'FastGenericDualOptimizer()',
    'fast-ascii': 'FastGenericDualOptimizer(slice(0x32, 127))',
}
for k in dual_optimizers:
    s = time.time()
    name = dual_optimizers[k]
    dual_optimizers[k] = eval(name)
    print(f"| Initialization | gamma/{k} | ({name}) | {dual_optimizers[k].n_chars} | {time.time()-s:.4f}s |")

no_block_mask = np.ones_like(DEFAULT_TEMPLATES.default_mask)
no_block_mask[0x2028] = 0
# disable block elements
no_block_mask[0x2580:0x2597] = 0

ascii_mask = np.zeros_like(DEFAULT_TEMPLATES.default_mask)
ascii_mask[32:127] = 1

gamma_optimizers = {
    'fast-noblock': 'FastGammaOptimizer(charmask=no_block_mask)',
    'exact-noblock': 'ExactGammaOptimizer(charmask=no_block_mask)',
    'basic-noblock': 'BasicGammaOptimizer(charmask=no_block_mask)',
    'fast-noblock-bw': 'FastGammaOptimizer(charmask=no_block_mask, use_color=False)',
    'exact-ascii-bw': 'ExactGammaOptimizer(charmask=ascii_mask, use_color=False)',
}

for k in gamma_optimizers:
    s = time.time()
    name = gamma_optimizers[k]
    gamma_optimizers[k] = eval(name)
    print(f"| Initialization | gamma/{k} | ({name}) | {gamma_optimizers[k].n_chars} | {time.time()-s:.4f}s |")

this = Path(__file__).parent
dual_renderer = Renderer(max_w=160, max_h=60)
gamma_renderer = GammaRenderer(max_w=160, max_h=60)

dirs = [('dual', dual_renderer, dual_optimizers),
        ('gamma', gamma_renderer, gamma_optimizers),
]
print("""
| Renderer | Optimizer | Time | Result |
| -------- | --------- | ---- | ------ |
""")
for img in images:
    img_path = this/img
    for dirname, renderer, optimizers in dirs:
        basedir = img_path.with_suffix('') / dirname
        basedir.mkdir(exist_ok=True, parents=True)
        for opt_name, opt in optimizers.items():
            s = time.time()
            renderer.render_terminal(img_path, (basedir/opt_name).with_suffix('.txt'), optimizer=opt)
            e = time.time()
            img_fn = (basedir/opt_name).with_suffix('.png')
            renderer.prerender(img_path, optimizer=opt).save(img_fn)
            print(f"| {renderer.__class__.__name__} | {dirname}/{opt_name} | {e-s:.4f}s | ![]({img_fn}) | ")

