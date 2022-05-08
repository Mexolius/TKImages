
cd ImageFinderRabbitMqSetupApp 
docker-compose up -d
call sbt run 
cd ../Client
py -m pip install -r requirements.txt
start cmd /k py ColorFilterConsumer.py 
start cmd /k py DogFilterConsumer.py 
start cmd /k py SimilarityConsumer.py 
start cmd /k py SizeFilterConsumer.py 
start cmd /k py App.py 