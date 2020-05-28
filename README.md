# Cardpay project

The fictitious project made as a coding exercise for Primer. 
The idea of the application is to provide an API to tokenize 
card payment information and perform a sale using the generated token.

## Application details

It literally consists of two endpoints - `/tokenise` and `/sale`, both supports only POST method. 
Don't be scared by "Not Found" instead of home page. Both actions backed by Braintree.
Note that Braintree sandbox environment only accepts 
[specific test credit card numbers](https://developers.braintreepayments.com/reference/general/testing/python#credit-card-numbers).

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

Don't forget to fill `.env` file with your settings afterwards.

**Install requirements** (example with `virtualenv`):

```bash
$ virtualenv -p python3 venv
$ source venv/bin/activate
$ pip install -r dev-requirements.txt
```

**Testing**:

```bash
$ pytest
```

**Linting**:

```bash
$ flake8
```

**Running development server**:

```bash
$ ./manage.py runserver
```

## Deployment  

You should have `ansible` installed on the local machine.    
Ansible Vault is used to encrypt default credentials (stored in `secrets.yml`),
so to run playbook you must know the Vault password by which they were encrypted. 

Defined `playbook.yml` very primitive and built just to get things done, so don't judge :)

```bash
$ cd deployment
$ ansible-playbook playbook.yml -i inventory.ini --ask-vault-pass
```
