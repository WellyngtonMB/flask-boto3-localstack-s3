FROM python:3.10.4

WORKDIR /app

COPY requirements.txt requirements.txt
COPY app.py app.py

RUN pip3 install -r requirements.txt
RUN mkdir -v /app/uploads
RUN mkdir -v /app/downloads

EXPOSE 5000

ENV FLASK_APP=app.py

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]