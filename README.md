# taskworker-classifyimage

Worker for taskbridge which can handle tasks of type `classifyimage`.

## Result format

When calling the TaskBridge `/api/tasks/complete/:id` API, the following JSON structure is sent to the endpoint.

```json
{
  "result" : {
    "predictions": [
      {
        "class": "n02123394",
        "name": "Perserkatze",
        "probability": 0.8419579267501831
      },
      {
        "class": "n02328150",
        "name": "Angorakatze",
        "probability": 0.025817258283495903
      },
      {
        "class": "n02124075",
        "name": "Aegyptische Katze",
        "probability": 0.0048589943908154964
      }
    ],
    "duration" : 1.6,
    "repository" : "https://github.com/hilderonny/taskworker-imageclassifier",
    "version": "1.0.0",
    "library": "tensorflow-2.17.0",
    "model": "MobileNetV3Large"
  }
}
```

|Property|Description|
|---|---|
|`predictions`|Array of predictions. Number of entries depends on `numberofpredictions` property in request|
|`predictions.class`|Class identifier as defined in [ILSVRC2011](https://image-net.org/challenges/LSVRC/2012/browse-synsets)|
|`predictions.name`|Name of the class in the language defined in request|
|`predictions.probability`|Probability of the class in a range between 0 (0%) and 1 (100%)|
|`duration`|Time in seconds for the processing|
|`repository`|Source code repository of the worker|
|`version`|Version of the worker|
|`library`|Library used to perform image classification|
|`model`|AI model used for image classification|

## Installation

First install Python 3.12. The run the following commands in the folder of the downloaded repository.

```sh
python3.12 -m venv python-venv
python-venv\Scripts\activate # Windows
source ./python-venv/bin/activate # Linux
pip install tensorflow==2.17.0 pillow==10.4.0
```

Adopt the shell script `classifyimage.sh` to your needs and create SystemD config files (if you want to run the worker as Linux service).

**/etc/systemd/system/taskworker-classifyimage.service**:

```
[Unit]
Description=Task Worker - Image classifier

[Service]
ExecStart=/taskworker-classifyimage/classifyimage.sh
Restart=always
User=user
WorkingDirectory=/taskworker-classifyimage/

[Install]
WantedBy=multi-user.target
```

Finally register and start the services.

```
chmod +x ./classifyimage.sh
sudo systemctl daemon-reload
sudo systemctl enable taskworker-classifyimage.service
sudo systemctl start taskworker-classifyimage.service
```


## Running

Running the program the first time, ai models with about 4 GB (depending on the used model) get downloaded automatically.

```sh
python classifyimage.py --taskbridgeurl http://127.0.0.1:42000/ --worker RH-WORKBOOK
```

## Literature

1. https://keras.io/api/applications/mobilenet/