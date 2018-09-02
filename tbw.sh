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

ark(){
        install_modules
        pause 
}
 
persona(){
        install_modules
        mkdir node_modules
        cd node_modules
        git clone https://github.com/PersonaIam/persona-js
        cd persona-js
        npm install
        pause
}

ripa(){
        install_modules
        npm install https://github.com/RipaEx/ripa-js
        pause
}

swapblocks(){
        install_modules
        npm install https://github.com/lwfcoin/lwf-nano-js 
        pause
}

# function to display menus
show_menus() {
	clear
	echo "~~~~~~~~~~~~~~~~~~~~~"	
	echo " M A I N - M E N U"
	echo "~~~~~~~~~~~~~~~~~~~~~"
	echo "1. Install ARK"
	echo "2. Install PERSONA"
        echo "3. Install RIPA"
        echo "4. Install SWAPBLOCKS"
	echo "9. Exit"
}
read_options(){
	local choice
	read -p "Enter choice [ 1 - 9] " choice
	case $choice in
		1) ark ;;
		2) persona ;;
                3) ripa ;;
                4) swapblocks ;;
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
