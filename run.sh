#!/bin/bash -e

USER="pi@raspberrypi.local"
PASSWORD="wallaby"
PROJECT_PATH="/home/root/Documents/KISS/KIPR/botball-2022"

if ! [[ $1 ]]; then
    echo "Please provide the name of the file you want to install (eg. 'demobot' or 'create')"
    exit 1
fi

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
    set -e
    cd $PROJECT_PATH
    unzip -q game.zip -d .
    rm game.zip
    mkdir -p bin
    cat <<EOF > bin/botball_user_program
#!/bin/bash -e
/usr/bin/python3 -u $PROJECT_PATH/src/main.py $1
EOF
    chmod +x ./bin/botball_user_program
    echo '==> Running...'
    ./bin/botball_user_program
"
