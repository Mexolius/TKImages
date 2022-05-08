#!/usr/bin/bash

cd ImageFinderRabbitMqSetupApp 
docker-compose up -d
sbt run -y
cd ../Client
python3 -m pip install -r requirements.txt
xterm -e python3 ColorFilterConsumer.py 
xterm -e python3 DogFilterConsumer.py 
xterm -e python3 SimilarityConsumer.py 
xterm -e python3 SizeFilterConsumer.py 
xterm -e python3 App.py 