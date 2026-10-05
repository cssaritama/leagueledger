#!/usr/bin/env sh
set -eu

CLUSTER_NAME="${CLUSTER_NAME:-leagueledger}"
NAMESPACE="leagueledger"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-leagueledger-local}"

for command in docker kind kubectl; do
  if ! command -v "$command" >/dev/null 2>&1; then
    echo "Missing required command: $command" >&2
    exit 1
  fi
done

if ! kind get clusters | grep -qx "$CLUSTER_NAME"; then
  kind create cluster --name "$CLUSTER_NAME"
fi

docker build -t leagueledger-api:local ./backend
docker build --build-arg VITE_API_BASE_URL=/api -t leagueledger-web:local ./frontend

kind load docker-image leagueledger-api:local --name "$CLUSTER_NAME"
kind load docker-image leagueledger-web:local --name "$CLUSTER_NAME"

kubectl apply -f k8s/namespace.yaml

kubectl -n "$NAMESPACE" create secret generic leagueledger-postgres \
  --from-literal=POSTGRES_PASSWORD="$POSTGRES_PASSWORD" \
  --from-literal=DATABASE_URL="postgresql+psycopg://leagueledger:${POSTGRES_PASSWORD}@postgres:5432/leagueledger" \
  --dry-run=client -o yaml | kubectl apply -f -

kubectl apply -f k8s/postgres-storage.yaml
kubectl apply -f k8s/postgres.yaml
kubectl rollout status deployment/postgres -n "$NAMESPACE" --timeout=120s

kubectl delete job db-init -n "$NAMESPACE" --ignore-not-found=true
kubectl apply -f k8s/db-init-job.yaml
kubectl wait --for=condition=complete job/db-init -n "$NAMESPACE" --timeout=120s

kubectl apply -f k8s/backend.yaml
kubectl apply -f k8s/frontend.yaml
kubectl rollout status deployment/backend -n "$NAMESPACE" --timeout=120s
kubectl rollout status deployment/frontend -n "$NAMESPACE" --timeout=120s

kubectl get pods -n "$NAMESPACE"

echo
echo "Deployment is ready."
echo "Open the application with:"
echo "  kubectl port-forward -n $NAMESPACE service/frontend 8080:80"
echo "API docs (optional):"
echo "  kubectl port-forward -n $NAMESPACE service/backend 8000:8000"
