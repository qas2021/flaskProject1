FROM python:3.8.0-buster
WORKDIR /flaskProject1
ADD . /flaskProject1
EXPOSE 5000
COPY . /requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt