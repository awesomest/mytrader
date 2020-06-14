# [mytrader](https://mytrader-279617.appspot.com/bitbank/)

## Requirements
* [Docker](https://www.docker.com/)
* Python 3.7.0
* virtualenv

## Python
```sh
$ virtualenv env
$ source env/bin/activate
$ pip install -r requirements.txt
```

### Development tools
```sh
$ black [FILE_NAME]
$ pylint --load-plugins pylint_django --rcfile=.pylintrc [FILE_NAME]
```

## MySQL
### Run
```sh
$ docker-compose up
```

### Stop
```sh
$ docker-compose down
```

### Update
```sh
$ docker exec -it $CONTAINER_NAME sh -c 'mysqldump eraise -u eraise -peraise 2> /dev/null' > sql/init.sql
```

## Django
```sh
$ python manage.py migrate
$ python manage.py runserver
```

## Documents
* [Architechture](https://docs.google.com/presentation/d/1YMLNzz-PrKDV_IeKXlmBPZj72ZlB2rwqpRv3hZfhZWI/edit?usp=sharing)
