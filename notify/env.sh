#!/bin/bash
printenv | sed 's/^\(.*\)$/export \1/g' > $HOME/.env.sh
exit 0