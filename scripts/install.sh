#!/bin/bash

set -e
source ./scripts/config.sh

echo "Bundling project..."

rm -f bin/botball_user_program

wipple bundle \
    --bin bin/botball_user_program \
    --interpreter https://github.com/wipplelang/wipple/releases/latest/download/wipple-bundled-armv7-unknown-linux-gnueabihf

echo "Installing on Wombat ($WOMBAT)..."

rsync -Pz --compress-level=1 -e "ssh -i $HOME/.ssh/id_rsa" --rsync-path="sudo mkdir -p $DIR && sudo rsync" ./bin/botball_user_program "$WOMBAT:$BIN"

echo "Done!"
