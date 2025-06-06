FROM python:3.10

WORKDIR /usr/src/app
COPY . /usr/src/app
RUN pip install -r requirements.txt
EXPOSE 5000

CMD python /usr/src/app/app.py