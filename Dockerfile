FROM python:3.8-slim-buster
RUN pip install --no-cache-dir pipenv
COPY Pipfile ./
COPY Pipfile.lock ./
RUN pipenv install 

COPY ./src .
COPY ./.env .

CMD [ "pipenv", "run", "python", "main.py" ]
