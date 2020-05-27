# Cardpay project

The fictitious project made as a coding exercise for Primer. 
The idea of the application is to provide an API to tokenize 
card payment information and perform a sale using the generated token.

## Project structure

Root of application code is `src`.
The main django app is called `app`. Here we have configuration files and 
some app-wide things (`views.py`).

## Installing on a local machine
This project is built and tested on Python 3.8.2.  
Pay attention to `.env.example` file. It's a template for `.env` file that 
you should create by yourself if you want to run this project locally.

```bash
$ cd src && cp .env.example .env
```

Don't forget to fill `.env` file with your settings  afterwards.


Install requirements (example with `virtualenv`):

```bash
$ virtualenv -p python3 venv
$ source venv/bin/activate
$ pip install -r dev-requirements.txt
```

Testing:

```bash
$ pytest
```

Linting:

```bash
$ flake8
```

Development server:

```bash
$ ./manage.py runserver
```
