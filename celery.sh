#!/bin/bash

# cd backend/
celery -A project worker -l INFO
