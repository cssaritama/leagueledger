# Deployment guide

## Docker Compose

Copy the example environment file if you want to customize the local database
credentials:

```bash
cp .env.example .env
```

Start the complete stack:

```bash
docker compose up --build -d --wait
```

Open:

- Web: `http://localhost:8080`
- API docs: `http://localhost:8000/docs`

Verify it:

```bash
./scripts/smoke-test.sh
```

Stop it:

```bash
docker compose down
```

Use `docker compose down -v` only when you also want to delete the local
PostgreSQL data volume.

## Kubernetes with kind

Requirements: Docker, kind and kubectl.

```bash
./scripts/kind-deploy.sh
```

Expose the frontend:

```bash
kubectl port-forward -n leagueledger service/frontend 8080:80
```

Inspect the deployment:

```bash
kubectl get all -n leagueledger
kubectl get pvc -n leagueledger
```
