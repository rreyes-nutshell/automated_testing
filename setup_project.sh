#!/bin/bash

mkdir -p NS_AI_Tester
mkdir -p NS_AI_Tester/oracle
mkdir -p NS_AI_Tester/sap
mkdir -p NS_AI_Tester/routes
touch NS_AI_Tester/routes/__init__.py
touch NS_AI_Tester/routes/oracle_runner.py
mkdir -p NS_AI_Tester/providers
touch NS_AI_Tester/providers/__init__.py
mkdir -p NS_AI_Tester/services
touch NS_AI_Tester/services/step_interpreter.py
mkdir -p NS_AI_Tester/use_cases
touch NS_AI_Tester/use_cases/run_session.py
mkdir -p NS_AI_Tester/utils
touch NS_AI_Tester/utils/logging.py
mkdir -p NS_AI_Tester/templates
touch NS_AI_Tester/templates/index.html
mkdir -p NS_AI_Tester/static
mkdir -p NS_AI_Tester/instance
touch NS_AI_Tester/instance/.env
mkdir -p NS_AI_Tester/migrations
touch NS_AI_Tester/app.py
touch NS_AI_Tester/requirements.txt
touch NS_AI_Tester/db_init.py
