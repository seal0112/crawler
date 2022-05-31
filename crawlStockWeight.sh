#!/bin/bash
source venv/bin/activate
python3 -c 'from crawler import getStockWeight; getStockWeight()'
deactivate
exit 0
