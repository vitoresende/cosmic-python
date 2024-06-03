# Example application code for the python architecture book

## Chapter: Domain Modeling
This chapter explain about the patterns and we have 4 files here:
* model.py : contains all the code
* test_model : the first tests about the business rules
* test_allocate : 
* test_value : explain about principles of **Value Object** pattern

Also, the chapter add some concepts to be in mind:
* A **value object** is defined by its attributes. It’s usually best implemented as an immutable type. If you change an attribute on a Value Object, it represents a different object. 
* An **entity** has attributes that may vary over time and it will still be the same entity. It’s important to define what does uniquely identify an entity (usually some sort of name or reference field).
* Python is a multiparadigm language, so let the "verbs" in your code be functions. 

## Requirements
* python and pip 3.8+ installed
* sqlite3 installed
* pipenv (`pip install pipenv`)

## Creating a local virtualenv (optional)

First create a `.venv` folder inside the root of the project.

```sh
pipenv install pytest sqlalchemy
```

## Running the tests

```sh
make test
```