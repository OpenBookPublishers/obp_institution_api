FROM python:2

RUN pip install --upgrade pip

WORKDIR /usr/src/app

COPY ./src/* ./
RUN pip install --no-cache-dir -r requirements.txt && \
    rm requirements.txt

CMD ["python", "api.py"]
