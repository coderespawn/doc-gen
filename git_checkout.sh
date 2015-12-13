#!/bin/bash

if [ "$#" -ne 2 ]; then
    echo "Illegal number of parameters. Usage: GIT_PATH BRANCH"
    exit 1
fi

GIT_PATH=$1
BRANCH=$2

pushd $GIT_PATH > /dev/null
git checkout $BRANCH
git pull
popd > /dev/null
