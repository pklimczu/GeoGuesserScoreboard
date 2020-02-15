source venv/bin/activate

export FLASK_APP=app
export FLASK_DEBUG=1
export FLASK_ENV=development

flask run --host 0.0.0.0
