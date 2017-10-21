#!/bin/bash
# Read me : this script will install Chrome-cut requirements and your user into the
# printing group. this script only meant to be run once before you run FQM for
# the first time

# checking if pip exist
pip_exi=`command -v pip3`
pip2_exi=`command -v pip`
# checking if python exist
python3=`command -v python3.4`
# checking if qt4 exists
qt=`command -v qmake`
# checking if cmake exists
cmake=`command -v cmake`
# checking if virtualenv exists
virtenv=`command -v virtualenv`

if [ "$python3" == "" ]
then
  echo "Error: please install python3.4, from your package manager"
  exit 0
fi
if [ "$pip_exi" == "" ] || [ "$pip2_exi" == "" ]
then
  echo "Error: please install python3-pip, from your package manager"
  exit 0
fi
if [ "$cmake" == "" ]
then
  echo "Error: please install cmake, from your package manager"
  exit 0
fi
if [ "$virtenv" == "" ]
then
  echo "Error: please install python-virtualenv or python3-virtualenv, from your package manager"
  exit 0
fi
if [ "$qt" == "" ]
then
  echo "Error: please install qt5 or qt5-defaults, from your package manager"
  exit 0
fi


if [ "$1" == "--install" ]
then
  if [ -f requirements.txt ]
  then
    echo "##### Creating virtual enviroment #####"
    virtualenv --python=python3.4 installiation/ && source installiation/bin/activate
    echo "##### Installing packages from pip #####"
    pip install -r requirements.txt
    echo "##### All done #####"
  else
    echo "Error: can not find the requirements text file"
  fi
elif [ "$1" == "--uninstall" ]
then
  echo "##### Uninstalling #####"
  if [ -d installiation/ ]
  then
    sudo rm -rf installiation/
    echo "##### All done #####"
  else
    echo "Error: enviroment not installed yet .."
  fi
elif [ "$1" == "--run" ]
then
  if [ -d installiation/ ]
  then
    source installiation/bin/activate
  else
    echo "Error: must --install enviroment first .."
    exit 0
  fi
  echo "##### Running chrome-cut 0.1 #####"
  if [ -f run.py ]
  then
    python run.py
  else
    echo "Error: can not find chrome-cut run.py"
  fi
else
  echo -e "\t --help : Usage \n"
  echo -e "\t\t $0 --install \t to install packages required"
  echo -e "\t\t $0 --uninstall \t to remove packages installed"
  echo -e "\t\t $0 --run \t to run chrome-cut with the right settings"
  echo -e "\t\t $0 --help \t to print out this message"
fi

exit 0
