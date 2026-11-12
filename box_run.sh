#!/bin/bash
# Box copy of free-proxy-airport: always run the latest generator from the repo,
# then publish the result to the dedicated Gist.
set -e
cd /workspace/free-proxy-airport
RAW="https://raw.githubusercontent.com/lastripple/free-proxy-airport/main"
curl -sL "$RAW/generator.py" -o generator.py
curl -sL "$RAW/box_publish.py" -o box_publish.py
FPA_SKIP_TEST=1 python3 generator.py
python3 box_publish.py
