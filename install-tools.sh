#!/bin/bash
# Checks to verify that the script is running as sudo
if [[ $EUID -ne 0 ]]; then
   echo "THIS SCRIPT NEEDS TO BE RUN AS SUDO."
   echo "EX: sudo bash install-tools.sh"
   exit 1
fi
echo "##############################"
echo "APPLYING UPDATES"
apt update -y 
echo "##############################"
echo "INSTALLING XTERM"
apt install xterm -y
echo "##############################"
echo "INSTALLING NODE PACKAGE MODULES"
apt install npm -y
npm init -y
npm install express
echo "##############################"
echo "RUN THE FOLLOWING COMMANDS"
echo ""
echo "npm start"
echo ""
echo "firefox 127.0.0.1:3000 &"
echo ""
