.PHONY: venv install dev

venv:
	python3 -m venv venv

install: venv
	./venv/bin/pip install -r requirements.txt

# Editable install for development

dev: venv
	./venv/bin/pip install -e .
