FROM python:3.8-slim

RUN apt update

RUN apt install -y fonts-dejavu-core fonts-dejavu

WORKDIR /app

COPY . ./

RUN python3 -m pip install --upgrade pip

RUN pip3 install -r requirements.txt --no-cache-dir

CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000"]
