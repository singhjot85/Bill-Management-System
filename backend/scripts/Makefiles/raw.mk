#####################################
### Docker Explicit Make Targets  ###
#####################################

# ----------------------------------
# Django Explicit Targets
# ----------------------------------
poetry-activate:
	cd ${BACKEND_DIR} && eval "$$(poetry env activate)" && exec $$SHELL
pa: poetry-activate

poetry-run:
	cd ${BACKEND_DIR} && poetry run python ${arg}

poetry-lock:
	cd ${BACKEND_DIR} && poetry lock

poetry-install:
	cd ${BACKEND_DIR} && poetry install --no-root --no-interaction

poetry-refresh-system:
	cd ${BACKEND_DIR} && poetry lock && poetry install --no-interaction

pre-commit:
	cd ${BACKEND_DIR} && poetry run pre-commit run --all-files


# ----------------------------------
# Django Specific Targets
# ----------------------------------

poetry-runserver:
	cd ${BACKEND_DIR} && poetry run python manage.py runserver

poetry-mm:
	cd ${BACKEND_DIR} && poetry run python manage.py makemigrations $(app)

poetry-m:
	cd ${BACKEND_DIR} && poetry run python manage.py migrate

poetry-shell-plus:
	cd ${BACKEND_DIR} && poetry run python manage.py shell_plus --ipython



.PHONY: poetry-activate poetry-run poetry-lock poetry-install poetry-refresh-system pre-commit poetry-runserver poetry-mm poetry-m poetry-shell-plus pa
