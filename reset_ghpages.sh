#!/bin/bash

if [ "$#" -ne 1 ]; then
    echo "Illegal number of parameters. Usage: GIT_PATH"
    exit 1
fi

GIT_PATH=$1

pushd $GIT_PATH > /dev/null
BRANCH=$(git rev-parse --abbrev-ref HEAD)

if [ "$BRANCH" == "gh-pages" ]; then
	git checkout .
fi

popd > /dev/null
