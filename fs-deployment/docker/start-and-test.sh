#!/bin/bash
########################################################
# Complete Docker Setup and Test Script
########################################################

set -e

echo "========================================="
echo "MAVIS DTC Processing - Docker Test Setup"
echo "========================================="
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "ERROR: Docker is not running. Please start Docker Desktop."
    exit 1
fi

echo "Step 1: Starting Oracle container..."
docker-compose up -d

echo ""
echo "Step 2: Waiting for database to be ready..."
echo "This may take 5-10 minutes on first run..."

# Wait for container to be healthy
MAX_WAIT=600  # 10 minutes
ELAPSED=0
while [ $ELAPSED -lt $MAX_WAIT ]; do
    if docker-compose ps | grep -q "(healthy)"; then
        echo "Database is ready!"
        break
    fi
    echo "Still waiting... ($ELAPSED seconds)"
    sleep 10
    ELAPSED=$((ELAPSED + 10))
done

if [ $ELAPSED -ge $MAX_WAIT ]; then
    echo "ERROR: Database did not become healthy within $MAX_WAIT seconds"
    echo "Check logs with: docker-compose logs oracle-db"
    exit 1
fi

echo ""
echo "Step 3: Checking installation logs..."
docker exec mavis-oracle-db bash -c "
    if [ -f /tmp/db_code_install.log ]; then
        echo 'db_code installation log:'
        tail -20 /tmp/db_code_install.log
    fi
    if [ -f /tmp/faster_staging_install.log ]; then
        echo 'faster_staging installation log:'
        tail -20 /tmp/faster_staging_install.log
    fi
"

echo ""
echo "Step 4: Verifying database objects..."
docker exec mavis-oracle-db sqlplus -s mdqa_owner/mdqa123@//localhost:1521/XEPDB1 <<EOF
SET PAGESIZE 0
SET FEEDBACK OFF
SELECT 'Tables: ' || COUNT(*) FROM user_tables;
SELECT 'Sequences: ' || COUNT(*) FROM user_sequences;
SELECT 'Packages: ' || COUNT(*) FROM user_objects WHERE object_type = 'PACKAGE';
SELECT 'Invalid objects: ' || COUNT(*) FROM user_objects WHERE status != 'VALID';
EXIT;
EOF

echo ""
echo "========================================="
echo "Setup Complete!"
echo "========================================="
echo ""
echo "To run tests:"
echo "  docker exec -it mavis-oracle-db sqlplus mdqa_owner/mdqa123@//localhost:1521/XEPDB1 @/docker/test-scripts/test_d0150.sql"
echo "  docker exec -it mavis-oracle-db sqlplus mdqa_owner/mdqa123@//localhost:1521/XEPDB1 @/docker/test-scripts/test_d0302.sql"
echo ""
echo "Or run tests automatically:"
echo "  ./run-tests.sh"
echo ""
echo "To stop:"
echo "  docker-compose down"
echo ""
