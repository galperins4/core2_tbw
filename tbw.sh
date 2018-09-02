#!/bin/bash
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
  pip3 install -r requirements.txt
}

install(){
        install_modules
        pause 
}
 
initialize(){
        cd core
	python3 tbw.py
        pause
}

all(){
	cd core
	pm2 start apps.json
	pause
}

tbw(){
        cd core
	pm2 start apps.json --only tbw
        pause
}

pay(){
	cd core
	pm2 start apps.json --only pay
        pause
}

custom(){
	cd core
	pm2 start apps.json --only custom
        pause
}

pool(){
	cd core
	pm2 start apps.json --only pool
        pause
}

stop(){
	cd core
	pm2 stop apps.json
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
