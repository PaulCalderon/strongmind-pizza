
# Pizza Store Project 
This application is a REST API for a fictional pizza store currently implementing two functions, 
-  ##### Manage Toppings
-  ##### Manage Pizza

The project is implemented using Python and uses the Django and Django Rest Framework. It uses DRF's browserable API as the main UI. 

Intended as a code exercise for Strongmind/SMLP Interview.

# Overview
- [Installation](#installation)
- [Usage](#usage)
- [Implementation](#implementation)
- [Testing](#testing)
- [Swagger](#swagger)
- [Deployment](#deployment)
- [Areas of Improvement](#areas-of-improvement)

## Installation
The project was developed under the following versions:
>Python 3.11.0

>Django 4.2

>djangorestframework 3.14

*It is recommented to install the packages in a virtual environment (venv)*

##### To install the project locally 
Clone the repository and navigate to the project root:
```bash
git clone https://github.com/PaulCalderon/strongmind-pizza.git
```
```bash
cd strongmind-pizza
```
and install the requirements (this will included packages used for developing the application)
```bash
pip install -r requirements.txt
```
Alternatively, you can use the package manager pip to only install the packages below.
```python
pip install Django==4.2
pip install djangorestframework==3.14
pip install whitenoise==6.6.0
pip install Markdown==3.5.1
```
The GitHub repository includes a sqlite database with pre configured groups and users.

2 groups have been made
1.  Pizza Owner - read-write permissions over toppings 
2.  Pizza Chef - read-write permissions over pizzas

| username | password | group
| ------ | ------ | ------ | 
| owner | 1234 | Pizza Owner
| chef | 1234 | Pizza Chef
| admin | 1234 | superuser*

*granted all permissions**

If you decide to not use the database from the repository, you can delete the old database and create a new database by running:
```
python manage.py migrate
```
This will create a new database with the groups and users, described above, created at migration.

*The automatic creation of groups and users on the first migration is implemented in 0004 and 0005 in pizza/migrations**
## Usage
To run the server locally:
```python
python manage.py runserver
```
You can now access the Browserable API homepage at:
```
http://127.0.0.1:8000/
```
- The Browserable API provides a convenient way to send requests and display responses from the API.
#### Endpoints 

The applcation exposes 4 endpoints with implemented methods:

```
1. /toppings       | GET, POST 
```
```
2. /toppings/<id>  | GET, PUT, DELETE
```
```
3. /pizzas         | GET, POST
```
```
4. /pizzas/<id>    | GET, PUT, DELETE
```
You can send a HTTP request to the API and receive a JSON response based on the request 

#### Browserable API
- The Browserable API has forms and buttons for sending requests to the API and will display the response.
- You can navigate to the endpoints and the appropriate forms and buttons will be displayed based on the implemented methods 
- The application uses the django provdied authentication and permission system.
- Unauthenticated users and without the proper permission can only use read HTTP methods. e.g. GET
    - For the toppings, only users in the *Pizza Owner* group can write data e.g POST, PUT, DELETE
    - For the pizzas, only users in the *Pizza Chef* group can write data e.g POST, PUT, DELETE

**You can send raw JSON with the request instead of using the HTML forms. The format is as follows:**

```json
 { "topping" : "name of the topping" }
 ```
 ```json
 { "pizza" : "name of the pizza", "toppings" : ["name of existing topping"] }
 ```

*For pizzas, the toppings in the request must have an entry, otherwise an error will be raised.*

###### You can also use sites like [reqbin](https://reqbin.com/) to send requests to the API. You can provide the login details using Basic Auth. 

- *A raw POST request for an individual topping*
```
POST /toppings/ HTTP/1.1
Host: pizzastoredeployment-env.eba-ywgipkmu.ap-southeast-1.elasticbeanstalk.com
Content-Type: application/json
Content-Length: 34

{ "topping" : "topping to be add"}
```
##### /toppings 
- Displays a list of toppings (GET)
- Create a new topping (POST)

##### /toppings/{id}
- Displays an individual topping (GET)
- Edit an existing topping (PUT)
- Delete an existing topping (DELETE)


##### /pizzas 
- Display a list of pizzas (GET)
- Create a new pizza and include existing toppings (POST)

##### /pizzas/{id}
- Displays an individual pizza (GET)
- Edit an existing pizza (POST)
- Delete an existing pizza (DELETE)



The [swagger](#swagger) documentation has a more detailed explanation of the endpoints

#### The Admin Page 
This project has enabled the django admin site which can be accessed locally at http://127.0.0.1:8000/admin/

- You need to have permissions to access the admin site. Login with username and password respectively:
```
admin   
1234
```
- You can use the admin site to interact with the API but includes the ability to configure the API administrative settings.
    - You can create new users and groups, as well as change and assign permissions.

[Link to deployed project's admin site](http://pizzastoredeployment-env.eba-ywgipkmu.ap-southeast-1.elasticbeanstalk.com/admin/)


## Implementation
The project used Django and Django Rest Framework to build and implement the API.
#### Models
- ##### PizzaToppings 
    -   id | Primary Key 
    -   topping | CharField | Unique = True (case-insensitive) 
- ##### Pizza 
    - id | Primary Key 
    - pizza | CharField | Unique = True (case-insensitive)
    - toppings | ManyToManyField 
    
When checking for duplicates, the comparison is case-insensitive.

#### Serializer 
- The Serializers use ModelSerializer to autogenerate fields from the models.
- An additional url field is declared on the serializer model to navigate to the individual pages of an entry. 


#### Views
- The views are mostly implemented using class based views to take advantage of the framework's autogeneration of HTML forms for interacting with the API.
- Permissions and Authentication has been enfored on the views.

#### Project settings 
The project settings are located at /pizza\_store/settings.py

The default password validator of django are disabled for the sake of convenience, i.e. allowing fully numeric passwords of any length.

The local project's debug setting is set to True while the deployed project is set to False

[Whitenoise](https://pypi.org/project/whitenoise/) was used to help facilitate serving the project's static files.

## Testing
The tests are divided into two files tests\_unit.py and tests\_integration.py.

The tests are located at pizza/test/

You can run all the tests by running the command:
```
python manage.py test
```
To only run a specific test 
```
python manage.py test pizza.test.tests_unit
python manage.py test pizza.test.tests_integration
```

## Swagger
The project includes an OpenAPI documentation locally located at http://127.0.0.1:8000/swagger-index

The document is included in the project files at static/openapi/schema.yml


## Deployment
The project is deployed on AWS using their free tier resources.

Available users to be logged in are the same as the users described in the [installation](#installation).

[Link to deployed project](http://pizzastoredeployment-env.eba-ywgipkmu.ap-southeast-1.elasticbeanstalk.com/)

------------------------------------
#### Areas of Improvement
Various points of improvements for the project. (may or may not be feasible)
 - Create an auto populated slug field in the model and use it as part of the URL instead of pk.
 - Create a new layer/file and move some of the business logic from the views.py into it.
 - Refactor code for better isolation between layers and better layering of business logic.
 - Topping name should only be alphanumeric and hyphens.(same with pizza name).
 - Customize error pages/messages.
 - Create an actual homepage instead of using the browseable API.
 - Expand model to include more parameters.
 - Implement patch method.
 - Implement pagination.
 - Refactor integration to have less hardcoded variables and tests.
 - Refactor tests with regards to DRY.
 - Create models in mermaid js for the readme.
 - Give more feedback after write methods. 