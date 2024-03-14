#!/bin/bash
set -e
BRANCH="main"
SCRIPT_DIR=$(cd $(dirname $0); pwd)

cd $SCRIPT_DIR

git pull

python3 generate.py

if [ -n "$(git status --porcelain)" ]; then
  msg="Automated update"
  git add .
  git commit -m "$msg"
  git push
else
  echo "Feed is up to date"
fi
