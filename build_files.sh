#!/usr/bin/env bash

set -euo pipefail

python manage.py migrate --noinput
python manage.py seed_showcase_user
python manage.py collectstatic --noinput
