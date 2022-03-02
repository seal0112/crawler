#!/bin/bash
cd /home/ec2-user/project/crawler
source venv/bin/activate
python crawler.py
deactivate
exit 0
