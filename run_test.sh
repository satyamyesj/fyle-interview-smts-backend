#!/bin/bash

# to stop on first error
set -e

# export environment variables
export FLASK_APP=core/server.py

# reset db
rm core/store.sqlite3
flask db upgrade -d core/migrations/

# run test
pytest -v tests/ --cov
