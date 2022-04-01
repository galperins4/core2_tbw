#!/bin/bash

shopt -s expand_aliases
FILE=$HOME/.solarrc && test -f "$FILE" && source "$FILE" # For Solar nodes.

# A menu driven shell script sample template 
## ----------------------------------
# Step #1: Define variables
# ----------------------------------

# ----------------------------------
# Step #2: User defined function
# ----------------------------------
pause(){
  read -p "Press [Enter] key to continue..." fackEnterKey
}

install_modules(){
  sudo apt-get install python3-pip
  sudo apt-get install python3-dev
  sudo apt-get install libudev-dev libusb-1.0.0-dev
  sudo apt-get install build-essential
  sudo apt-get install autoconf
  sudo apt-get install libtool
  sudo apt-get install pkgconf
  sudo apt-get install libpq-dev
  pip3 install setuptools
  pip3 install -r requirements.txt
}

install(){
        install_modules
        pause 
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
	cd core
	pm2 start apps.json
	cd ..
	pause
}

tbw(){
        cd core
	pm2 start apps.json --only tbw
	cd ..
        pause
}

pay(){
	cd core
	pm2 start apps.json --only pay
	cd ..
        pause
}

custom(){
	cd core
	pm2 start apps.json --only custom
	cd ..
        pause
}

pool(){
	cd core
	pm2 start apps.json --only pool
	cd ..
        pause
}

stop(){
	cd core
	pm2 stop apps.json
	cd  ..
	pause
}

# function to display menus
show_menus() {
	clear
	echo "~~~~~~~~~~~~~~~~~~~~~"	
	echo " M A I N - M E N U"
	echo "~~~~~~~~~~~~~~~~~~~~~"
	echo "1. Install"
	echo "2. Initialize"
        echo "3. Start All"
        echo "4. Start TBW Only"
	echo "5. Start Pay Only"
	echo "6. Start Custom Only"
	echo "7. Start Pool Only"
	echo "8. Stop All"
	echo "9. Exit"
}
read_options(){
	local choice
	read -p "Enter choice [ 1 - 9] " choice
	case $choice in
		1) install ;;
		2) initialize ;;
                3) all ;;
                4) tbw ;;
		5) pay ;;
		6) custom ;;
		7) pool ;;
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
