sudo apt-get install -y freeglut3-dev git
git config --global alias.st status
git config --global user.name "Frederic Boudon"
git config --global user.email frederic.boudon@cirad.fr
curl https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -o miniconda.sh
chmod a+rwx miniconda.sh
./miniconda.sh -b -p $HOME/miniconda
export PATH=$HOME/miniconda/bin:$PATH
conda config --set always_yes yes
conda config --add channels fredboudon 
conda config --add channels conda-forge
source activate
conda init bash
conda create -n mangolight openalea.plantgl openalea.mtg alinea.caribu alinea.astk
git clone https://github.com/fredboudon/mangolight.git
cd mangolight/src
screen -S mangolight 
conda activate mangolight
python benchmark.py
rcrssimulation.py


