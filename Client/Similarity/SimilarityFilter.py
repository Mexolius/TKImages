import json

from PIL import Image
from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer('clip-ViT-B-32')


def run_classifier(path, photo_path):
    image1 = Image.open(path).convert('RGB')
    image2 = Image.open(photo_path).convert('RGB')

    encoded_image = model.encode([image1, image2], batch_size=128,
                                 convert_to_tensor=True)
    processed_images = util.paraphrase_mining_embeddings(encoded_image)
    return processed_images[0][0]


def check_similarity(paths, similarity, photo_path, logger):
    filtered_paths = []

    for path in paths:
        try:
            calculated_percent = run_classifier(path, photo_path) * 100
            logger.info(f'Processed {path} with result {calculated_percent}%')
            if calculated_percent >= float(similarity):
                filtered_paths.append(path)
        except ValueError:
            logger.warn(f'{path} not valid')
            continue
    return filtered_paths


def process_request(body, logger):
    body = json.loads(body)
    params = body["params"]

    path = params['path']
    percent = params['percent']
    paths = body['paths']

    result = check_similarity(paths, percent, path, logger)

    return result
