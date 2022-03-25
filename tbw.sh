#!/bin/bash

## -------------------------
# Step #1: Define variables
# --------------------------
APPNAME="core2_tbw"
APPHOME="$HOME/$APPNAME"
VENV="$APPHOME/.venv"

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

## ----------------
# Preflight checks
# -----------------
cmd_exists () {
    type -t "$1" > /dev/null 2>&1 ;
}

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
        echo -e "${CRed}Error: cannot continue without $reqd_cmd!${NC}"
        exit 1
    fi
fi
sleep 1

# -------------------------------
# Step #2: User defined function
# -------------------------------
cd $APPHOME

pause(){
  read -p "Press [Enter] key to continue..." fackEnterKey
}
 
initialize(){
    . .venv/bin/activate
    version=$(python3 -c "import sys; print(''.join(map(str, sys.version_info[:2])))")

    if [[ "$version" -lt 36 ]]; then
        echo "Python 3.6 minimum version is required"
        exit 1
    fi

    cd core
    python3 tbw.py
    cd ..
    deactivate
    pause
}

all(){
    pm2 start apps.json
    pause
}

tbw(){
    pm2 start apps.json --only tbw
    pause
}

pay(){
    pm2 start apps.json --only pay
    pause
}

custom(){
    pm2 start apps.json --only custom
    pause
}

pool(){
    pm2 start apps.json --only pool
    pause
}

stop(){
    pm2 stop apps.json
    pause
}

# function to display menus
show_menus() {
    clear
    echo "~~~~~~~~~~~~~~~~~~~~~"	
    echo " M A I N - M E N U"
    echo "~~~~~~~~~~~~~~~~~~~~~"
    echo -e "${CRed}0. Initialize${NC}"
    echo "1. Start All"
    echo "2. Start TBW Only"
    echo "3. Start Pay Only"
    echo "4. Start Custom Only"
    echo "5. Start Pool Only"
    echo -e "${CRed}8. Stop All${NC}"
    echo -e "${CBlue}9. Exit${NC}"
}

read_options(){
    local choice
    read -p "Enter choice [0 - 9] " choice
    case $choice in
        0) initialize ;;
        1) all ;;
        2) tbw ;;
        3) pay ;;
        4) custom ;;
        5) pool ;;
        8) stop ;;
        9) exit 0;;
        *) echo -e "${RED}Error...${STD}" && sleep 2
    esac
}
 
# ----------------------------------------------
# Step #3: Trap CTRL+C, CTRL+Z and quit singles
# ----------------------------------------------
trap '' SIGINT SIGQUIT SIGTSTP
 
# ------------------------------------
# Step #4: Main logic - infinite loop
# ------------------------------------
while true
do
    show_menus
    read_options
done
