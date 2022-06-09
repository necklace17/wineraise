# Wine Raise Backend

## Get Started

### Install Poetry

### Setup project

### Run tests

### Run server

### User creation and login

#### Create user

Create a user with the following command:
`curl --location --request POST 'http://localhost:8000/api/user/create/' \
--header 'Content-Type: application/json' \
--data-raw '{
"email": "ilikewine@wine.de",
"password": "test_password",
"name": "Ned Stark"
}'`

#### Create Authorization token

`curl --location --request POST 'http://localhost:8000/api/user/token/' \
--header 'Content-Type: application/json' \
--data-raw '{
"email": "ilikewine@wine.de",
"password": "test_password"
}'`

#### Include token in request

`curl --location --request GET 'http://localhost:8000/api/wine/wines/' \
--header 'Authorization: token a8186096b404628fa64b6da63e470a67c6a2380c'`
