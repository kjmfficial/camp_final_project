#!/bin/bash
#start_service
cd /home/ubuntu/lgu_final_project/
source lgu/bin/activate

cd /home/ubuntu/lgu_final_project/lgu_final/backend

uvicorn main:app > /home/ubuntu/lgu_final_project/uvicorn.log 2>&1 &

echo "4" >> /home/ubuntu/lgu_final_project/test