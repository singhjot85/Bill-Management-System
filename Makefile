.PHONY: run mm m sp superuser setup setup-system setup-python sdu

run:
	poetry run python manage.py runserver

mm:
	poetry run python manage.py makemigrations $(app_name)

m:
	poetry run python manage.py migrate

superuser:
	poetry run python manage.py createsuperuser

sp:
	poetry run python manage.py shell_plus --ipython

setup-system:
	@command -v brew >/dev/null || (echo "Homebrew is required. Install from https://brew.sh"; exit 1)
	brew install poetry cairo pkg-config cmake pango gdk-pixbuf libffi

setup-python:
	poetry lock
	poetry install --no-interaction

setup: setup-system setup-python

start-dev-ui:
	cd bma-frontend && npm install && npm run dev
sdu: start-dev-ui
