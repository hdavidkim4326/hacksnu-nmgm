#!/bin/bash

# Vercel 환경에 맞게 python3.9 -m pip로 수정
python3.9 -m pip install -r requirements.txt

python3.9 manage.py collectstatic --noinput
