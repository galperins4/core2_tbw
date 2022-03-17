#!/bin/bash
# A menu driven shell script sample template 
## ----------------------------------
# Step #1: Define variables
# ----------------------------------
APPNAME="core2_tbw"
APPHOME="$HOME/$APPNAME"
VENV="$APPHOME/.venv"

cd $APPHOME
# ----------------------------------
# Step #2: User defined function
# ----------------------------------
pause(){
  read -p "Press [Enter] key to continue..." fackEnterKey
}
 
initialize(){
	version=$(python3 -c "import sys; print(''.join(map(str, sys.version_info[:2])))")

	if [[ "$version" -lt 36 ]]; then
    	echo "Python 3.6 minimum version is required"
    	exit 1
	fi

	cd core
	python3 tbw.py
	cd ..
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
	echo "0. Initialize"
	echo "1. Start All"
	echo "2. Start TBW Only"
	echo "3. Start Pay Only"
	echo "4. Start Custom Only"
	echo "5. Start Pool Only"
	echo "8. Stop All"
	echo "9. Exit"
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
 
# -----------------------------------
# Step #4: Main logic - infinite loop
# ------------------------------------
while true
do
	show_menus
	read_options
done
