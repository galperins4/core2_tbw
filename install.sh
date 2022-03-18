#!/bin/bash
AUTHOR="osrn"
APPNAME="core2_tbw"
APPHOME="$HOME/$APPNAME"
VENV="$APPHOME/.venv"
GITREPO="https://github.com/$AUTHOR/$APPNAME.git"
GITBRANCH="develop"

SUDO_USER=$1
if [ -z "$SUDO_USER" ]
  then
    echo "Error: this script must be called with a sudo user as argument"
    echo usage: $0 user
    exit 1
fi

if  ! id -u $SUDO_USER &>/dev/null
  then
    echo "Error: user $SUDO_USER does not exist"
    exit 1
fi

if [ -z "$(id -Gn $SUDO_USER | grep sudo)" ]
  then
    echo "Error: $SUDO_USER must have sudo privilage"
    exit 1
fi

clear


echo
echo installing system dependencies
echo ==============================
echo "You will be asked for the SUDOER's password twice; first time for su, and second time for sudo in su environment"
echo Please enter the password for $SUDO_USER
su - $SUDO_USER -c "echo Please enter the password for $SUDO_USER again
sudo -S cd ~ # dummy action to submit sudo password
sudo apt-get -y install python3 python3-pip python3-dev python3-venv
sudo apt-get -y install libpq-dev libudev-dev libusb-1.0-0-dev
sudo apt-get -y install build-essential autoconf libtool pkgconf
"
version=$(python3 -c "import sys; print(''.join(map(str, sys.version_info[:2])))")

if [[ "$version" -lt 36 ]]; then
    echo "Error: Python 3.6 minimum version is required"
    exit 1
fi
echo installing latest pip and venv for user
echo =======================================
python3 -m pip install --user --upgrade pip
python3 -m pip install --user virtualenv
echo done.


echo
echo downloading package from git repo
echo =================================
cd ~
if [ -d $APPHOME ]; then
    read -p "existing installation found, shall I wipe it? [y/N]> " r
    case $r in
    y|Y) rm -rf $APPHOME;;
    *) echo -e "did not wipe existing installation";;
    esac
fi
if (git clone -b $GITBRANCH $GITREPO) then
    echo "package retrieved."
    cd $APPHOME
else
    echo "local repo found! resetting to remote..."
    cd $APPHOME
    git reset --hard
    git fetch --all
    git checkout $GITBRANCH
    git pull
fi
echo done


echo
echo creating virtual environment
echo ============================
if [ -d $VENV ]; then
    read -p "remove existing virtual environment ? [y/N]> " r
    case $r in
    y|Y) 
        rm -rf $VENV
        python3 -m venv .venv
        ;;
    *) echo -e "existing virtual environment preserved";;
    esac
else
    python3 -m venv .venv
fi
echo done


echo
echo installing python dependencies
echo ==============================
. $VENV/bin/activate
if [ -n "$CPATH" ]; then
# Workaround for Solar vers > 3.2.0-next.0 setting CPATH 
# causing psycopg2 compilation error for missing header files
    OLDCPATH=$CPATH
    export CPATH="/usr/include"
fi
cd $APPHOME
# wheel and psycopg2 needs to be installed seperately
pip3 install wheel
pip3 install psycopg2
pip3 install -r requirements.txt
deactivate
echo done
if [ -n "$SAVEDCPATH" ]; then
    export CPATH=$OLDCPATH
fi

echo '====================='
echo 'installation complete'
echo '====================='
echo
echo '>>> next steps:'
echo '==============='
echo 'This script requires pm2, which Solar Core already includes'
echo 'but otherwise you can install it with:'
echo 'npm install pm2@latest [-g]'
echo 'or'
echo 'yarn [global] add pm2'
echo
echo 'First, edit core/config/config to set essential parameters like'
echo '  START_BLOCK, NETWORK, DATABASE_USER,'
echo '  DELEGATE, PUBLIC_KEY,'
echo '  INTERVAL, VOTER_SHARE, PASSPHRASE, KEEP, PAY_ADDRESSES,'
echo '  POOL_IP, PROPOSAL'
echo 
echo 'All config parameters are explained in README.md'
echo 
echo 'Next do;' 
echo '  cd '$APPHOME',' 
echo '  bash tbw.bash'
echo '  Select menu option [0] for first time initialization'
echo '  Then, select the menu options for [Start TBW Only], [Start Pay Only] and [Start Pool Only] '
echo '  to start and register the processes with pm2'
echo 
echo 'For subsequent operations you can use;'
echo '  pm2 start|restart|stop|logs tbw'
echo '  pm2 start|restart|stop|logs pay'
echo '  pm2 start|restart|stop|logs pool'
