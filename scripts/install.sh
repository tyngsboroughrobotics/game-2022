#!/bin/bash

set -e
source ./scripts/config.sh

./scripts/bundle.sh

echo "Installing on Wombat ($WOMBAT)..."

rsync -Pz --compress-level=1 -e "ssh -i $HOME/.ssh/id_rsa" --rsync-path="sudo mkdir -p $DIR && sudo rsync" ./bin/botball_user_program "$WOMBAT:$BIN"

echo "Done!"
