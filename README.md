# fash-backend
Follow the below instructions to set up the database.

1.) Install postgresql

2.) Type "flask db init"

3.) Type "flask db migrate"

4.) Type "flask db upgrade"

## Installing new Python package
```
# create new virtual env
python/python3 -m venv .venv
# enter virtual env
source .venv/bin/activate
# install packages
pip install <package>
# install requirements file
pip install -r requirements.txt
# update requirements file
pip freeze > requirements.txt