import time

from img2unicode import *
from pathlib import Path

print("""
| Optimizer name | Constructor | Chars | Setup time |
| -------------- | ----------- | ----- | ---------- |
""", end='')

images = ['obama.jpg', 'matplotlib.png']
dual_optimizers = {
    'space': 'SpaceDualOptimizer()',
    'half': 'HalfBlockDualOptimizer()',
    'quad': 'FastQuadDualOptimizer()',
    'exact-block': 'ExactGenericDualOptimizer("block")',
    'fast-block': 'FastGenericDualOptimizer("block")',
    'fast-all': 'FastGenericDualOptimizer()',
    'fast-ascii': 'FastGenericDualOptimizer("ascii")',
}
for k in dual_optimizers:
    s = time.time()
    name = dual_optimizers[k]
    dual_optimizers[k] = eval(name)
    print(f"| dual/{k} | ({name}) | {dual_optimizers[k].n_chars} | {time.time()-s:.2f}s |")

gamma_optimizers = {
    'fast-noblock': 'FastGammaOptimizer(charmask="no_block")',
    'exact-noblock': 'ExactGammaOptimizer(charmask="no_block")',
    'basic-noblock': 'BasicGammaOptimizer(charmask="no_block")',
    'fast-noblock-bw': 'FastGammaOptimizer(charmask="no_block", use_color=False)',
    'exact-ascii-bw': 'ExactGammaOptimizer(charmask="ascii", use_color=False)',
}

for k in gamma_optimizers:
    s = time.time()
    name = gamma_optimizers[k]
    gamma_optimizers[k] = eval(name)
    print(f"| gamma/{k} | ({name}) | {gamma_optimizers[k].n_chars} | {time.time()-s:.2f}s |")

this = Path(__file__).parent
dual_renderer = Renderer(max_w=160, max_h=60)
gamma_renderer = GammaRenderer(max_w=160, max_h=60)

dirs = [('dual', dual_renderer, dual_optimizers),
        ('gamma', gamma_renderer, gamma_optimizers),
]
print("""
| Renderer | Optimizer | Time | Result |
| -------- | --------- | ---- | ------ |
""", end='')
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
            print(f"| {renderer.__class__.__name__} | {dirname}/{opt_name} | {e-s:.2f}s | ![]({img_fn}) | ")

