#!/bin/bash
cd /home/ec2-user/project/crawler
source venv/bin/activate
python3 -c 'from crawler import getFutureDayDiff; getFutureDayDiff()'
deactivate
exit 0
