#!/bin/sh

export LD_LIBRARY_PATH=`./python-venv/bin/python -c 'import os; import nvidia.cublas.lib; import nvidia.cudnn.lib; print(os.path.dirname(nvidia.cublas.lib.__file__) + ":" + os.path.dirname(nvidia.cudnn.lib.__file__))'`
export CUDA_VISIBLE_DEVICES=0

./python-venv/bin/python classifyimage.py --taskbridgeurl http://127.0.0.1:42000/ --worker SENECA-CPU
