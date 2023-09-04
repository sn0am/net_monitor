FROM python:3.9.13

WORKDIR /usr/app/src

COPY app.py ./
COPY requirements.txt ./
COPY env.example ./.env

RUN pip install --no-cache-dir --upgrade pip \
  && pip install --no-cache-dir -r requirements.txt

CMD [ "python", "-u", "./app.py"]
