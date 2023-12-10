#!/bin/bash

cd /home/user2/srb_valuation

python3 scrape_4zida.py
python3 prepare.py
python3 model_train.py
git add .
git commit -m "upd"
git push
