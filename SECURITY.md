# Security

This repository contains local-development defaults only. Do not commit real
credentials, production connection strings or private keys.

For local Kubernetes, `scripts/kind-deploy.sh` creates the database Secret at
runtime. For production deployments, use the secret management mechanism
provided by the target platform.

If you discover a security issue in a deployed copy of this project, report it
privately to the operator of that deployment rather than publishing secrets or
exploit details in an issue.
