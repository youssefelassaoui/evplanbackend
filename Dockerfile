FROM python:3.8.10-slim-buster

# set work directory
WORKDIR /usr/src/app

# set env. variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# copy src
COPY . .

# install dependencies
RUN pip install -r requirements.txt

# entrypoint
RUN chmod 755 ./run.sh

EXPOSE 8000
ENTRYPOINT [ "./run.sh" ]
