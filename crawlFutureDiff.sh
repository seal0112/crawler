#!/bin/bash
source venv/bin/activate
python3 -c 'from crawler import getFutureDayDiff; getFutureDayDiff()'
deactivate
exit 0
