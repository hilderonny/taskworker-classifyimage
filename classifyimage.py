from importlib.metadata import version
import time
import json
import requests
import datetime
import argparse
import os
import numpy

REPOSITORY = "https://github.com/hilderonny/taskworker-imageclassifier"
VERSION = "1.0.0"
LIBRARY = "tensorflow-" + version("tensorflow")
LOCAL_MODEL_PATH = "./models/tensorflow"
LOCAL_FILE_PATH = "./temp"
KERAS_PATH = os.path.join(LOCAL_MODEL_PATH, 'keras')
MODEL_FILE_PATH = os.path.join(LOCAL_MODEL_PATH, 'mobilenetv3large_model.keras')
LABELFILEPATH = {
    "en": "./data/imagenet.en.names",
    "de": "./data/imagenet.de.names",
}
os.environ['KERAS_HOME'] = KERAS_PATH

print(f'Image classifier Version {VERSION}')

# Parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument('--taskbridgeurl', type=str, action='store', required=True, help='Root URL of the API of the task bridge to use, e.g. https://taskbridge.ai/')
parser.add_argument('--version', '-v', action='version', version=VERSION)
parser.add_argument('--worker', type=str, action='store', required=True, help='Unique name of this worker')
args = parser.parse_args()

WORKER = args.worker
print(f'Worker name: {WORKER}')
TASKBRIDGEURL = args.taskbridgeurl
if not TASKBRIDGEURL.endswith("/"):
    TASKBRIDGEURL = f"{TASKBRIDGEURL}/"
APIURL = f"{TASKBRIDGEURL}api/"
print(f'Using API URL {APIURL}')

# Prepare paths
os.makedirs(LOCAL_FILE_PATH, exist_ok=True)

# Download model if neccessary
if not os.path.exists(LOCAL_MODEL_PATH):
    os.makedirs(KERAS_PATH, exist_ok=True)
    os.makedirs(LOCAL_FILE_PATH, exist_ok=True)
    import tensorflow.keras.applications as applications
    model = applications.MobileNetV3Large(weights='imagenet', include_top=True)
    model.save(MODEL_FILE_PATH)


# Load classification labels
print(f'Loading labels')
CLASSES = { "en" : {}, "de" : {} }
for language in LABELFILEPATH:
    filepath = LABELFILEPATH[language]
    with open(filepath, mode='r', encoding='utf-8') as f:
        for line in f.readlines():
            stripped_line = line.strip()
            id, text = stripped_line[:9], stripped_line[10:]
            CLASSES[language][id] = text

# Import TensorFlow and MobileNet
print('Loading TensorFlow and MobileNet V3')
from tensorflow.keras.preprocessing import image
from tensorflow.keras.models import load_model
from tensorflow.keras.applications.mobilenet_v3 import preprocess_input, decode_predictions

# Load MobileNet model
print("Loading model")
MODEL = load_model(MODEL_FILE_PATH, compile=False)

def process_file(file_path, language, number_of_predicitions):
    result = {}
    try:
        img = image.load_img(file_path, target_size=(224, 224))
        imageArray = image.img_to_array(img)
        expandedImageArray = numpy.expand_dims(imageArray, axis=0)
        preprocessedImage = preprocess_input(expandedImageArray)
        predictions = MODEL.predict(preprocessedImage)
        best_predictions = decode_predictions(predictions, top=number_of_predicitions)[0]
        result_predictions = []
        for prediction in best_predictions:
            result_prediction = {} 
            result_prediction["class"] = prediction[0]
            result_prediction["name"] = CLASSES[language][prediction[0]]
            result_prediction["probability"] = float(prediction[2])
            result_predictions.append(result_prediction)
        result["predictions"] = result_predictions
    except Exception as ex:
        result["error"] = str(ex)
    return result

def check_and_process():
    start_time = datetime.datetime.now()
    take_request = {}
    take_request["type"] = "classifyimage"
    take_request["worker"] = WORKER
    response = requests.post(f"{APIURL}tasks/take/", json=take_request)
    if response.status_code != 200:
        return False
    task = response.json()
    taskid = task["id"]
    targetlanguage = task["data"]["targetlanguage"]
    numberofpredictions = int(task["data"]["numberofpredictions"])
    print(json.dumps(task, indent=2))

    file_response = requests.get(f"{APIURL}tasks/file/{taskid}")
    local_file_path = os.path.join(LOCAL_FILE_PATH, taskid)
    with open(local_file_path, 'wb') as file:
        file.write(file_response.content)

    result_to_report = {}
    result_to_report["result"] = process_file(local_file_path, targetlanguage, numberofpredictions)
    end_time = datetime.datetime.now()
    result_to_report["result"]["duration"] = (end_time - start_time).total_seconds()
    result_to_report["result"]["repository"] = REPOSITORY
    result_to_report["result"]["version"] = VERSION
    result_to_report["result"]["library"] = LIBRARY
    result_to_report["result"]["model"] = "MobileNetV3Large"
    print(json.dumps(result_to_report, indent=2))
    print("Reporting result")
    requests.post(f"{APIURL}tasks/complete/{taskid}/", json=result_to_report)
    os.remove(local_file_path)
    print("Done")
    return True

try:
    print('Ready and waiting for action')
    while True:
        task_was_processed = False
        try:
            task_was_processed = check_and_process()
        except Exception as ex:
            print(ex)
        if task_was_processed == False:
            time.sleep(3)
except Exception:
    pass

