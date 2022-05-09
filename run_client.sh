#!/usr/bin/bash

cd ImageFinderRabbitMqSetupApp 
docker-compose up -d
sbt run -y
cd ../Client
python3 -m pip install -r requirements.txt
gnome-terminal -- python3 ColorFilterConsumer.py 
gnome-terminal -- python3 DogFilterConsumer.py 
gnome-terminal -- python3 SimilarityConsumer.py 
gnome-terminal -- python3 SizeFilterConsumer.py 
gnome-terminal -- python3 App.py 