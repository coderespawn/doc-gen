#!/bin/bash

if [ "$#" -ne 2 ]; then
    echo "Illegal number of parameters. Usage: GIT_PATH VERSION"
    exit 1
fi

GIT_PATH=$1
VERSION=$2

pushd GIT_PATH
git checkout $VERSION
git pull
popd
