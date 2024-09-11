# taskworker-classifyimage

Worker for taskbridge which can handle tasks of type `classifyimage`.

## Task format

```json
{
    ...
    "type" : "classifyimage",
    "worker" : "ROG",
    "file" : "123456789",
    "data": {
        "numberofpredictions" : 2,
        "targetlanguage" : "de"
    },
    ...
    "result" : {
        "predictions" : [
            {
                "class" : "n02066245",
                "name" : "Grauwal",
                "probability": 75.4
            },
            {
                "class" : "n02423022",
                "name" : "Gazelle",
                "probability": 32.8
            }
        ],
        "duration" : 12,
        "repository" : "https://github.com/hilderonny/taskworker-classifyimage",
        "version" : "1.0.0",
        "library" : "tensorflow-2.17.0",
        "model" : "mobilenetv3large_model.keras"
    }
}
```

The `type` must be `classifyimage`.

`worker` contains the unique name of the worker.

The worker expects a `file` property defining the filename which contains the image to classify.

In the `data` property you need to define the `targetlanguage` (`en` or `de`). The names of the returned classes will be written in this language. Additionally you need to define in `numberofpredictions`, how many predictions (the best ones) you want to get in return.

When the worker finishes the task, it sends back a `result` property. This property is an object. It contains an array `predictions`. The array size depends on the previosly defined number of predictions. Each element contains a `class` property. This is one of the classes defined in [ILSVRC2011](https://image-net.org/challenges/LSVRC/2012/browse-synsets). The `name`property contains the name of the class in the target language defined before. The `probability` property contains the probability of the detection between 0 and 100.

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