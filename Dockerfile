FROM python:2

RUN pip install --upgrade pip

WORKDIR /usr/src/app

COPY ./src/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt && \
    rm requirements.txt

COPY ./src/* ./

CMD ["python", "api.py"]
