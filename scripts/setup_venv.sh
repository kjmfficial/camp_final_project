#!/bin/bash
# setup_venv
cd /home/ubuntu/lgu_final_project/
source lgu/bin/activate

cd lgu_final
pip install --upgrade pip
pip install -r requirements.txt


echo "3" >> /home/ubuntu/lgu_final_project/test


deactivate