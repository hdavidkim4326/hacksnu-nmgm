#!/usr/bin/env bash
set -e

# 휠만 설치(소스 빌드 방지) → 빌드시간/용량 이점
pip3 install --upgrade pip
pip3 install --only-binary=:all: -r requirements.txt

python3 manage.py collectstatic --noinput