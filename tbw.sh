#!/bin/bash
shopt -s expand_aliases
FILE=$HOME/.solarrc && test -f $FILE && source $FILE

# A menu driven shell script sample template
## ----------------------------------
# Step #1: Define variables
# ----------------------------------
required_packages=("python3-pip" "python3-dev" "python3-venv" "python3-wheel" "libudev-dev" "build-essential" "autoconf" "libtool" "pkgconf" "libpq-dev")
# ----------------------------------
# Step #2: User defined function
# ----------------------------------
pause() {
  read -p "Press [Enter] key to continue..." fackEnterKey
}

install_modules() {
  sudo -k
  if sudo true; then
    sudo apt-get install "${required_packages[@]}" -y
  fi

  dpkg -s "${required_packages[@]}" >/dev/null 2>&1 || missing_package # For Solar user which isn't in sudoers

  pip3 install --upgrade pip
  pip3 install setuptools
  pip3 install wheel
  pip3 install -r requirements.txt
}

missing_package() {
  echo -e "Run the following as root:\n
apt-get install python3-pip python3-dev python3-venv python3-wheel libudev-dev build-essential autoconf libtool pkgconf libpq-dev -y\n
Then run again bash tbw.sh"
  pause
  exit 1
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
