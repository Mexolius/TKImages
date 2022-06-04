
cd ImageFinderRabbitMqSetupApp 
docker-compose up -d
call sbt run 
cd ../Client
python -m pip install -r requirements.txt
start cmd /k python ColorFilterConsumer.py 
start cmd /k python DogFilterConsumer.py 
start cmd /k python SimilarityConsumer.py 
start cmd /k python SizeFilterConsumer.py 
start cmd /k python FacesFilterConsumer.py 
start cmd /k python App.py 
start cmd /k npm start
