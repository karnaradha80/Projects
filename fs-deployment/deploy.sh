#!/bin/bash
#
# MAVIS DTC Staging - Docker Deployment Script
#
# Usage: ./deploy.sh [start|stop|logs|connect|deploy]
#

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

ORACLE_USER="MDQA_OWNER"
ORACLE_PASS="MdqA_0wn3r2026"
ORACLE_CONN="//localhost/XEPDB1"

case "$1" in
    start)
        echo "Starting Oracle XE container..."
        docker-compose up -d
        echo "Waiting for Oracle to be ready (this may take a few minutes)..."
        until docker exec mavis-oracle-xe healthcheck.sh 2>/dev/null; do
            echo "  Waiting..."
            sleep 10
        done
        echo "Oracle XE is ready!"
        ;;
    stop)
        echo "Stopping Oracle XE container..."
        docker-compose down
        ;;
    logs)
        docker logs -f mavis-oracle-xe
        ;;
    connect)
        echo "Connecting to Oracle as $ORACLE_USER..."
        docker exec -it mavis-oracle-xe sqlplus "$ORACLE_USER/$ORACLE_PASS@$ORACLE_CONN"
        ;;
    deploy)
        echo "Deploying MAVIS DTC Staging schema..."
        echo "Running SQL scripts..."
        docker exec -i mavis-oracle-xe sqlplus "$ORACLE_USER/$ORACLE_PASS@$ORACLE_CONN" <<EOF
@/opt/oracle/scripts/startup/run_deployment.sql
EOF
        echo "Deployment complete!"
        ;;
    status)
        docker ps -a --filter name=mavis-oracle-xe
        ;;
    *)
        echo "MAVIS DTC Staging - Docker Deployment Script"
        echo ""
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  start   - Start the Oracle XE container"
        echo "  stop    - Stop the Oracle XE container"
        echo "  logs    - View container logs (follow mode)"
        echo "  connect - Connect to Oracle as MDQA_OWNER"
        echo "  deploy  - Run database deployment scripts"
        echo "  status  - Show container status"
        echo ""
        echo "Example workflow:"
        echo "  1. $0 start      # Start container and wait for Oracle"
        echo "  2. $0 deploy     # Deploy schema, tables, packages"
        echo "  3. $0 connect    # Connect to verify deployment"
        ;;
esac
