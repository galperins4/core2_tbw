#!/bin/bash
AUTHOR="galperins4"
APPNAME="core2_tbw"
APPHOME="$HOME/$APPNAME"
VENV="$APPHOME/.venv"
GITREPO="https://github.com/$AUTHOR/$APPNAME.git"
GITBRANCH="solar"

# Regular Colors
CBlack='\033[0;30m'  # Black
CRed='\033[0;31m'    # Red
CGreen='\033[0;32m'  # Green
CYellow='\033[0;33m' # Yellow
CBlue='\033[0;34m'   # Blue
CPurple='\033[0;35m' # Purple
CCyan='\033[0;36m'   # Cyan
CWhite='\033[0;37m'  # White
NC='\033[0m'         # Text Reset


SUDO_USER=$1
if [ -z "$SUDO_USER" ]
  then
    echo -e "${CRed}Error: this script must be called with a sudo user as argument${NC}"
    echo usage: $0 user
    exit 1
fi

if  ! id -u $SUDO_USER &>/dev/null
  then
    echo -e "${CRed}Error: user $SUDO_USER does not exist${NC}"
    exit 1
fi

if [ -z "$(id -Gn $SUDO_USER | grep sudo)" ]
  then
    echo -e "${CRed}Error: $SUDO_USER must have sudo privilage${NC}"
    exit 1
fi

cmd_exists () {
    type -t "$1" > /dev/null 2>&1 ;
}

clear


echo
echo installing system dependencies
echo ==============================
echo -e "${CYellow}Notice that you will be asked for the SUDOER's password twice; first time for su, second time for sudo in su environment${NC}"
echo Please enter the password for $SUDO_USER
su - $SUDO_USER -c "echo Please enter the password for $SUDO_USER again
sudo -S echo 'installing...'
sudo apt-get -y install python3 python3-pip python3-dev python3-venv
sudo apt-get -y install libpq-dev libudev-dev libusb-1.0-0-dev
sudo apt-get -y install build-essential autoconf libtool pkgconf
echo '...done'
"

exit_code=$?
if [ "$exit_code" -ne 0 ]; then
    echo -e "${CRed}Error: incorrect password or user $SUDO_USER has no password${NC}"
    exit 1
fi


version=$(python3 -c "import sys; print(''.join(map(str, sys.version_info[:2])))")
if [[ "$version" -lt 36 ]]; then
    echo -e "${CRed}Error: Python 3.6 minimum version is required${NC}"
    exit 1
fi
echo installing latest pip and venv for user
echo =======================================
python3 -m pip install --user --upgrade pip
python3 -m pip install --user virtualenv
echo done.


reqd_cmd="pm2"
if ! cmd_exists $reqd_cmd ; then
    echo -e "${CYellow}Warning: $reqd_cmd command or alias not found!${NC}"
    echo "seeking possible locations..."

    if [ -f "$HOME/.solarrc" ]; then
        shopt -s expand_aliases
        source $HOME/.solarrc
    #elif
        # other possible locations
    fi

    if ! cmd_exists $reqd_cmd ; then
        echo -e "${CYellow}$reqd_cmd not found but I can live without it.${NC}"
    fi
fi
sleep 1

echo
echo downloading package from git repo
echo =================================
cd ~
if [ -d $APPHOME ]; then
    read -p "$(echo -e "${CRed}existing installation found, shall I wipe it? [y/N]>${NC}") " r
    case $r in
    y|Y)
        echo 'stopping jobs...'
        pm2 stop tbw
        pm2 stop pay
        pm2 stop pool
        #echo 'unregistering jobs with pm2...'
        #pm2 delete tbw 
        #pm2 delete pay 
        #pm2 delete pool 

        # make a config backup if one exists
        read -p "$(echo -e "${CYellow}do you want to backup your config? [y/N]>${NC}") " rr
        case $rr in
        y|Y)
            bupsrc="$APPHOME/core/config/config"
            if [ -f "$bupsrc" ]; then
                buptgt="$HOME/tbw-config-"$(date +"%s")
                if cp $bupsrc $buptgt ; then
                    chmod 600 $buptgt
                    echo -e "${CBlue}backup $buptgt created with user access only"
                    ls -al $buptgt
                    echo -e "${NC}"
                else
                    read -p "$(echo -e "${CRed}could not backup your config. continue? [y/N]>${NC}") " rrr
                    case $rrr in
                    y|Y) ;;
                    *) exit 1;;
                    esac
                fi
            else
                echo -e "${CBlue}no config file to backup! ${NC}"
            fi
            ;;
        *) echo -e "${CBlue}will not backup any existing config!${NC}";;
        esac

        read -p "$(echo -e "${CYellow}do you want to backup your database? [y/N]>${NC}") " rr
        case $rr in
        y|Y)
            FAILCTR=0
            for FILE in $APPHOME/*.db; do
                echo 'Source file: '$FILE
                buptgt="$HOME/tbw-${FILE##*/}-"$(date +"%s")
                echo 'target file is:'$buptgt
                if cp $FILE $buptgt ; then
                    chmod 600 $buptgt
                    echo -e "${CBlue}backup $buptgt created with user access only"
                    echo -e "${NC}"
                else
                    ((FAILCTR++))
                fi
            done

            if (( FAILCTR > 0 )) ; then
                read -p "$(echo -e "${CRed}could not backup $FAILCTR databases. continue? [y/N]>${NC}") " rrr
                case $rrr in
                y|Y) ;;
                *) exit 1;;
                esac
            fi
            ;;
        *) echo -e "${CBlue}will not backup any existing database!${NC}";;
        esac

        echo 'removing package...'
        rm -rf $APPHOME
        ;;
    *) echo -e "did not wipe existing installation";;
    esac
fi
if (git clone -b $GITBRANCH $GITREPO) then
    echo "package retrieved from GIT"
    cd $APPHOME
else
    echo "local repo found! resetting to remote..."
    cd $APPHOME
    git reset --hard
    git fetch --all
    git checkout $GITBRANCH
    git pull
fi
echo '...done'


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
echo '...done'


echo
echo installing python dependencies
echo ==============================
. $VENV/bin/activate
if [ -n "$CPATH" ]; then
# Workaround for Solar vers > 3.2.0-next.0 setting CPATH 
# causing psycopg2 compilation error for missing header files
    SAVEDCPATH=$CPATH
    export CPATH="/usr/include"
fi
cd $APPHOME
# wheel and psycopg2 needs to be installed seperately
pip3 install wheel
pip3 install psycopg2
pip3 install -r requirements.txt
deactivate
echo '...done'
if [ -n "$SAVEDCPATH" ]; then
    export CPATH=$SAVEDCPATH
fi


echo -e ${CGreen}
echo '====================='
echo 'installation complete'
echo '====================='
echo -e ${NC}
echo '>>> next steps:'
echo '==============='
echo 'This script requires pm2, which Solar Core already includes'
echo 'but otherwise you can install it with:'
echo -e ${CBlue}'  npm install pm2@latest [-g]'
echo -e ${NC}'  or'${CBlue}
echo '  yarn [global] add pm2'
echo -e ${NC}
echo 'First, edit core/config/config to set essential parameters like'
echo -e ${CBlue}'  START_BLOCK, NETWORK, DATABASE_USER,'
echo '  DELEGATE, PUBLIC_KEY,'
echo '  INTERVAL, VOTER_SHARE, PASSPHRASE, KEEP, PAY_ADDRESSES,'
echo '  POOL_IP, PROPOSAL'
echo -e ${NC} 
echo 'All config parameters are explained in README.md'
echo 
echo 'Next do;' 
echo -e ${CBlue}'  cd '$APPHOME 
echo '  bash tbw.sh'
echo '  Select menu option [0] for first time initialization'
echo '  Then, select the menu options for [Start TBW Only], [Start Pay Only] and [Start Pool Only] '
echo '  to start and register the processes with pm2'
echo -e ${NC} 
echo 'For subsequent operations you can use;'
echo -e ${CBlue}'  pm2 start|restart|stop|logs tbw'
echo '  pm2 start|restart|stop|logs pay'
echo '  pm2 start|restart|stop|logs pool'
echo -e ${NC}
