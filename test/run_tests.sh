#!/bin/bash
set -e

TEST_DB_USER="test"
TEST_DB_PASS="testpass"
TEST_DB_NAME="test_db"
TEST_DB_HOST="localhost"
TEST_DB_PORT="5432"

sudo -u postgres psql -c "DO \$\$ BEGIN
   IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '$TEST_DB_USER') THEN
      CREATE USER $TEST_DB_USER WITH PASSWORD '$TEST_DB_PASS';
   END IF;
END \$\$;"

sudo -u postgres psql -v ON_ERROR_STOP=1 -c "DROP DATABASE IF EXISTS $TEST_DB_NAME;"
sudo -u postgres psql -v ON_ERROR_STOP=1 -c "CREATE DATABASE $TEST_DB_NAME OWNER $TEST_DB_USER;"

echo "Test DB ready. Executing tests"
export TEST_DB_USER TEST_DB_PASS TEST_DB_NAME TEST_DB_HOST TEST_DB_PORT

pytest --cov=Chatbot test/
