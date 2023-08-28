dev:
	cd ..; \
	iam/venv/bin/flask --app iam:app run

prepare:
	virtualenv venv -p python3.11
	venv/bin/pip install -r requirements.txt

migrate:
	cd ..; \
	iam/venv/bin/flask --app iam:app db upgrade head -d iam/migrations/

test:
	ps aux | grep "iam:app" | grep -v grep | awk '{print $$2}' | xargs kill -9
	rm -f ../instance/iam.db
	cd ..; \
	iam/venv/bin/flask --app iam:app db upgrade head -d iam/migrations/
	cd ..; \
	iam/venv/bin/flask --app iam:app run &
	sleep 3
	venv/bin/python -m unittest tests/test_* || true
	ps aux | grep "iam:app" | grep -v grep | awk '{print $$2}' | xargs kill -9
