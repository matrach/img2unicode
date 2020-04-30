from setuptools import setup, find_packages

setup(name='img2unicode',
      version='0.1',
      description='Convert images to unicode based on font templates. Especially usable in terminal.',
      url='https://github.com/matrach/img2unicode',
      author='Maciej Matraszek',
      author_email='matraszek.maciej@gmail.com',
      license='MIT',
      packages=find_packages(),
      install_requires=[
            'numpy',
            'pandas',
            'scikit-image',
            'pillow',
            'n2', # For FastRenderer
      ],
      extras_require={
          'develop': [
            'pytest',
            'pytest-cov',
            'sphinx',
            'sphinx_autodoc_typehints',
          ]
      },
      zip_safe=False)
