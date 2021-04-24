#!/bin/bash

set -e
source ./scripts/config.sh

ssh -t $WOMBAT "$BIN"
