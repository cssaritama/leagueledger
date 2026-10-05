# API examples

The interactive OpenAPI UI is available at `/docs` when the backend is running.

## Create teams

```bash
curl -X POST http://localhost:8000/teams \
  -H 'Content-Type: application/json' \
  -d '{"name":"Northbridge FC"}'

curl -X POST http://localhost:8000/teams \
  -H 'Content-Type: application/json' \
  -d '{"name":"Riverside United"}'
```

## Record a match

Use the IDs returned by the previous calls:

```bash
curl -X POST http://localhost:8000/matches \
  -H 'Content-Type: application/json' \
  -d '{"home_team_id":1,"away_team_id":2,"home_goals":2,"away_goals":1}'
```

## Read the derived table

```bash
curl http://localhost:8000/standings
```

## Health checks

```bash
curl http://localhost:8000/health
curl http://localhost:8000/ready
```
