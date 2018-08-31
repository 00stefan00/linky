# Linky

Linky is a discord bot, one that will watch whatever channel you tell it to untill it finds an URL. Whenever it finds one, it will automaticly copy the URL and post it in a seperate channel for all your URLS to be hanging out together in there.

### Requirements

Python 2.7 (python 3 might work, but is not being tested on)
python-pip

### Installation

pip install disco-py
pip install python-jsonstore

git clone the project in the folder you want to use as instalation folder

touch json.config
edit json.config to hold your discord bots token

(You can create your bot and find it's token here: https://discordapp.com/developers/applications/)

### Running

From the instalation folder:
python -m disco.cli --config config.json

