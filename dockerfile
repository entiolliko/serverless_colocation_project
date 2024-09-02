FROM ubuntu

RUN apt-get update && apt-get install python3.10 -y && apt install python3-venv -y  && apt install vim -y

WORKDIR /app
COPY . .
RUN python3.10 install.py 
