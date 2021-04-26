#!/bin/bash

set -e

echo "Bundling project..."

rm -f bin/botball_user_program

wipple bundle \
    --bin bin/botball_user_program \
    --interpreter https://github.com/wipplelang/wipple/releases/latest/download/wipple-bundled-armv7-unknown-linux-gnueabihf
