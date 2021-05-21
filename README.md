![](https://github.com/abhiabhi94/blog/workflows/build/badge.svg)

This repository contains the source code powering https://www.hackadda.com. It is used by for posting articles in the technological field(mostly related to programming).

This was our first project while learning `django`.

### Development

The website is build using `python` and `django`. To setup environment for local development it is recommended to use `virtual environment` in python.

```sh
# create virtual environment

python3.6 -m venv venv

# for unix based environment, this activates the virtual environment
. venv/bin/activate

# install dependencies
pip install -r requirements/dev.txt

# make migrations to the database
python manage.py migrate

# run the local server
python manage.py runserver
```

### Testing

To run tests, you may use

```sh
pytest
```
