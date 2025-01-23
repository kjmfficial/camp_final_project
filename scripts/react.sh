#!/bin/bash
#react
cd /home/ubuntu/lgu_final_project/
source lgu/bin/activate

cd /home/ubuntu/lgu_final_project/lgu_final/frontend

npm install vite --save-dev

cat ../../env_creat > .env

npm run build

sudo cp -r /home/ubuntu/lgu_final_project/lgu_final/frontend/dist/* /var/www/html/
sudo chown -R www-data:www-data /var/www/html
sudo systemctl restart nginx

echo "5" >> /home/ubuntu/lgu_final_project/test