FROM python:3.12.1

WORKDIR /usr/src/app

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1



#
COPY ./requirements.txt  /usr/src/app/requirements.txt

#
RUN pip install --no-cache-dir --upgrade -r /usr/src/app/requirements.txt

#
COPY . /usr/src/app

#
CMD ["uvicorn", "fastapi_proxy:app", "--host", "0.0.0.0", "--port", "5000"]
