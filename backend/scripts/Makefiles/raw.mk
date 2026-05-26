###################################
## Make Targets for normal shell ##
###################################

poetry-run:
	cd ${BACKEND_DIR} && poetry run python manage.py runserver

poetry-mm:
	cd ${BACKEND_DIR} && poetry run python manage.py makemigrations $(app)

poetry-m:
	cd ${BACKEND_DIR} && poetry run python manage.py migrate

poetry-superuser:
	cd ${BACKEND_DIR} && poetry run python manage.py createsuperuser

poetry-shell-plus:
	cd ${BACKEND_DIR} && poetry run python manage.py shell_plus --ipython

poetry-test:
	cd ${BACKEND_DIR} && poetry run pytest

setup-system:
	@command -v brew >/dev/null || (echo "Homebrew is required. Install from https://brew.sh"; exit 1)
	brew install poetry cairo pkg-config cmake pango gdk-pixbuf libffi

setup-python:
	cd ${BACKEND_DIR} && poetry lock && poetry install --no-interaction

pre-commit:
	cd ${BACKEND_DIR} && poetry run pre-commit run --all-files


.PHONY:
	poetry-run
	poetry-mm
	poetry-m
	poetry-superuser
	poetry-shell-plus
	poetry-test
	setup-system
	setup-python
	pre-commit
