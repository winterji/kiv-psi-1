# Assessment 1 of KIV/PSI at FAV ZCU
Author: Jiri Winter

## How to run the server
Server is a python application, so only python 3 is necessary to run it. Server can be launched by the **run.sh** script or simply by **python3 server.py**.

## Brief Introduction
This application opens a tcp socket on port 8080 and listens for incomming connections. For each connection it responds with a html page displaying route table read from **/proc/net/route**.

