FROM python:3.9.7-slim
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
RUN mkdir /code
WORKDIR /code
COPY ../requirements.txt /code/
RUN pip install -r requirements.txt
COPY proxy.py /code/
CMD ["hypercorn", "proxy:app", "-k", "trio", "--bind", "0.0.0.0:5000"]
