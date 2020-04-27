# auto-trader

## Requirements
* [Docker](https://www.docker.com/)
* Python 3.8.0

## Docker
### Setup
```
$ docker-compose build
```

### Run
```
$ docker-compose up
```

### Stop
```
$ docker-compose down
```

## Datasets
[datasets - Google Drive](https://drive.google.com/drive/folders/12bvEe6wix1u_lyH9dAJ3C63wM6HOZ1tk)

## Update DB
```
$ docker exec -it $CONTAINER_NAME sh -c 'mysqldump eraise -u eraise -peraise 2> /dev/null' > sql/init.sql
```
