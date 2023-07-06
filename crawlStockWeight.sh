#!/bin/bash
cd $(dirname "$0")
source venv/bin/activate
python3 -c 'from crawler import getStockWeight; getStockWeight()'
deactivate
exit 0
