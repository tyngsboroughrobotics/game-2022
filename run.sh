#!/bin/bash -e

USER="pi@raspberrypi.local"
PASSWORD="wallaby"
PROJECT_PATH="/home/root/Documents/KISS/KIPR/botball-2022"

echo "==> Installing..."

sshpass -p $PASSWORD ssh $USER "
    sudo rm -rf \"$PROJECT_PATH\"
    sudo mkdir -p \"$PROJECT_PATH\"
    sudo chmod -R a+rwX \"$PROJECT_PATH\"
"

zip -rq game.zip . -x .\*
sshpass -p $PASSWORD scp game.zip $USER:$PROJECT_PATH
rm game.zip

sshpass -p $PASSWORD ssh $USER "
    cd $PROJECT_PATH
    unzip -q game.zip -d .
    rm game.zip
    mkdir -p bin
    gcc -o bin/botball_user_program -std=c11 -lwallaby -lpthread -lm -Iinclude -Wall -g src/*.c
    echo '==> Running...'
    ./bin/botball_user_program
"
