@ECHO OFF
c:
cd \github\hilderonny\taskworker-classifyimage
git pull
.\python\python.exe classifyimage.py --taskbridgeurl http://192.168.0.152:42000/ --worker RH-WORKBOOK