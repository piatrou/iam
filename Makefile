dev:
	cd ..; \
	iam/venv/bin/flask --app iam:app run

prepare:
	virtualenv venv -p python3.11
	venv/bin/pip install -r requirements.txt

migrate:
	cd ..; \
	iam/venv/bin/flask --app iam:app db upgrade head -d iam/migrations/
