#!/bin/bash

set -eux

isort dtyper.py test*.py
black dtyper.py test*.py
ruff check --fix dtyper.py test*.py
pytest
mypy dtyper.py
