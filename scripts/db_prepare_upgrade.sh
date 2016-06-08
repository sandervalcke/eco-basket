#!/bin/sh

if [ $# -ne 1 ]; then
    echo 'Usage: db_prepare_upgrade.sh <message>'
    exit 1
fi

python3 manage.py db migrate -m "$1"
