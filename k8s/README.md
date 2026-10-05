# Local Kubernetes deployment

The manifests are designed for a local `kind` cluster. The deployment script initializes the database schema with a one-shot Kubernetes Job before starting two API replicas. The database uses a
single-node `hostPath` persistent volume, which is appropriate for local
portfolio/demo use but not for a managed production cluster.

From the repository root:

```bash
./scripts/kind-deploy.sh
```

Then expose the web application:

```bash
kubectl port-forward -n leagueledger service/frontend 8080:80
```

Open `http://localhost:8080`.

For a production environment, replace the local Postgres deployment and
`hostPath` volume with a managed PostgreSQL service and a production storage
class.
