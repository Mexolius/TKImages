from DogsFilter.lib.classifier import classifier 
import json
import os

def run_classifier(path):

      # NOTE: this function only works for model architectures: 
      #      'vgg', 'alexnet', 'resnet'  
      model = "vgg"

      image_classification = classifier(path, model)
      return image_classification


def check_if_dog(paths):
      filtered_paths = []
      with open(os.path.dirname(__file__) + "/lib/dognames.txt") as f:
            lines = f.read().splitlines() 
            for path in paths:
                  classification = run_classifier(path).lower()
                  if classification in lines:
                        filtered_paths.append(path)
      return filtered_paths


def check_breed(paths, breed):
      filtered_paths = []
      for path in paths:
            classification = run_classifier(path)
            if breed in classification:
                  filtered_paths.append(path)
      return filtered_paths


def process_request(body):
      body = json.loads(body)
      params = body["params"]

      if params["breed"].lower() == "any":
            result = check_if_dog(paths=body["paths"])
      else: 
            result = check_breed(paths=body["paths"], breed = params["breed"])
      return result


