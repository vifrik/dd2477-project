#!/usr/bin/sh
source ../venv/bin/activate
python3 -m pip uninstall query_dsl -y && python3 -m pip install ../query_dsl && python3 webserver.py
