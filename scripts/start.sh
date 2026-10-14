#!/bin/bash

# MX-UI Quick Start Script
# Usage: ./scripts/start.sh [docker|k8s|local]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MODE="${1:-docker}"

echo "🚀 MX-UI v2.0.0 - Starting..."
echo "📦 Deployment mode: $MODE"

case $MODE in
    docker)
        echo "🐳 Starting with Docker Compose..."
        cd "$SCRIPT_DIR"
        docker-compose up -d
        echo "✅ Services started!"
        echo "🌐 Access at: http://localhost:8080"
        echo "📊 Status: docker-compose ps"
        echo "📝 Logs: docker-compose logs -f mx-ui"
        ;;
    k8s)
        echo "☸️  Deploying to Kubernetes..."
        cd "$SCRIPT_DIR/k8s"
        kubectl apply -f namespace-config.yaml
        kubectl apply -f deployment.yaml
        kubectl apply -f service-pvc.yaml
        echo "✅ Kubernetes deployment complete!"
        echo "🔍 Check status: kubectl get pods -n mx-ui"
        echo "📝 View logs: kubectl logs -n mx-ui -f -l app=mx-ui"
        echo "🌐 Port forward: kubectl port-forward -n mx-ui svc/mx-ui 8080:80"
        ;;
    local)
        echo "🔧 Starting local development server..."
        cd "$SCRIPT_DIR"
        pip install -r requirements.txt
        python main.py
        ;;
    *)
        echo "❌ Unknown mode: $MODE"
        echo "Usage: ./scripts/start.sh [docker|k8s|local]"
        exit 1
        ;;
esac

echo ""
echo "💡 Need help? See README.md and CHANGELOG.md"
