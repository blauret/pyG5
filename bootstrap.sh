#!/bin/bash

WIN_ACTIVATE=".venv/Scripts/activate"
UNIX_ACTIVATE=".venv/bin/activate"

if ! [ -e $UNIX_ACTIVATE ] || ! [ -e $WIN_ACTIVE ] ;
then
    python -m venv .venv
fi

if [ -e $UNIX_ACTIVATE ] 
then
    source $UNIX_ACTIVATE
else
    source $WIN_ACTIVATE
fi

pip install -r requirements.txt