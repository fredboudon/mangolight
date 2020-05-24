curl https://repo.anaconda.com/miniconda/Miniconda${CONDA_VERSION}-latest-Linux-${ARCH}.sh -o miniconda.sh
chmod a+rwx miniconda.sh
./miniconda.sh -b -p $HOME/miniconda
export PATH=$HOME/miniconda/bin:$PATH
conda config --set always_yes yes
conda config --add channels fredboudon conda-forge
source activate
conda create -n mangolight openalea.plantgl alinea.caribu alinea.astk git
conda activate mangolight
git clone https://github.com/fredboudon/mangolight.git
cd mangolight/src
screen -S mangolight -m conda activate mangolight ; python rcrssimulation.py 

