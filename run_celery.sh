#!/usr/bin/env bash
cd src
celery -A celery_worker worker -l info --uid=nobody --gid=nogroup