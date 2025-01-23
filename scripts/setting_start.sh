#!/bin/bash

# scripts/setting_start.sh
if [ -d /home/ubuntu/lgu_final_project/lgu_final ]; then
    rm -rf /home/ubuntu/lgu_final_project/lgu_final || { echo "Failed to delete directory" >> /home/ubuntu/lgu_final_project/test;}
fi

mkdir /home/ubuntu/lgu_final_project/lgu_final || { echo "Failed to create directory" >> /home/ubuntu/lgu_final_project/test; }

echo "1" >> /home/ubuntu/lgu_final_project/test