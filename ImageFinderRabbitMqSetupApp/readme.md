# TKImagesRabbitMqSetupApp

Requirements:
- docker-compose
- sbt

First start RabbitMq with docker-compose:

    docker-compose up -d

Next, run setupApp:

    sbt run


## Available Topics:
- image_finder.size
- image_finder.colors
- image_finder.faces_smiles
- image_finder.dogs_breeds
- image_finder.similarity
- image_finder.results