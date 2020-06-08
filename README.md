# [mytrader](https://mytrader-279617.appspot.com/bitbank/)

## Requirements
* [Docker](https://www.docker.com/)
* Python 3.7.0
* virtualenv

## Docker
### Setup
```sh
$ docker-compose build
```

### Run
```sh
$ docker-compose up
```

### Stop
```sh
$ docker-compose down
```

## Django
```sh
$ source env/bin/activate
$ pip install -r requirements.txt
$ python manage.py migrate
$ python manage.py runserver
```

## Documents
* [Architechture](https://docs.google.com/presentation/d/1YMLNzz-PrKDV_IeKXlmBPZj72ZlB2rwqpRv3hZfhZWI/edit?usp=sharing)

## Update DB
```sh
$ docker exec -it $CONTAINER_NAME sh -c 'mysqldump eraise -u eraise -peraise 2> /dev/null' > sql/init.sql
```
