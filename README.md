# Sample applications

Small applications for trying observability and instrumentation workflows.
Each application lives in its own folder with its own run instructions.

## Applications

| Application | Description | Telemetry baseline |
| --- | --- | --- |
| [Field Supply](logs-only-shop/) | Browser storefront behind Nginx, three Python services and PostgreSQL. Includes normal, slow and declined payment scenarios. | Local logs; no traces or exported application metrics. |

Start with the application README for Docker Compose instructions and smoke checks.
