# Visualization of data onto the digitized tree

The following notebook allow to load and display the data onto a 3D representation of the foliage of the digitized mango tree.

To use it with Binder without any installation: [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/fredboudon/mangolight.git/master?urlpath=lab/tree/src%2Fdisplayinfo%2Fdisplay.ipynb)

# Installation

- Install conda : https://docs.conda.io/en/latest/miniconda.html

- In your menu, launch 'Anaconda Prompt'.

- Prepare conda environment: 

```bash
conda create -y -n pgl -c fredboudon -c conda-forge python=3.7 openalea.pgljupyter jupyterlab ipywidgets ipython=7 matplotlib git
```

- Retrieve the files of the project: 

```bash
git clone https://github.com/fredboudon/mangolight.git
```

# Activation and use of the environment

- Activate conda environment: 

```bash
conda activate pgl
```

- Enter the project visualization subfolder: 

```bash
cd src/displayinfo
```

- Launch jupyterlab: 

```bash
jupyter lab display.ipynb
```
