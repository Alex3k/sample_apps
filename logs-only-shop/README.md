# Field Supply: logs-only instrumentation example

A runnable baseline for the iHub repository-instrumentation demo. All payments are simulated.

```sh
cd logs-only-shop
docker compose up --build -d
# Open http://localhost:3310
docker compose logs -f nginx catalog checkout payment db
# Stop, preserving orders:
docker compose down
```

## Architecture

Nginx serves the browser application and proxies `/api/products` to catalog and
`/api/checkout` to checkout. Checkout calls catalog and payment over HTTP and
inserts successful orders into PostgreSQL. Catalog reads products from PostgreSQL.

Python services emit plain-text business logs plus Gunicorn access logs. Nginx and
PostgreSQL emit their normal logs. Browser logs remain in its developer console.
Logs are not forwarded to Grafana. There is no OpenTelemetry SDK, auto-instrumentation,
collector, trace exporter, application metrics endpoint, or metrics exporter.
PostgreSQL's internal statistics are not an exported application metrics pipeline.

## Scenarios

- Normal: simulated payment approval and a persisted order.
- Slow: payment sleeps 1.5 seconds before approval.
- Declined: HTTP 422, with no order persisted.
- Unavailable dependency: checkout returns HTTP 503 and logs an exception.

No card fields or personal details are collected. The hard-coded database password
is a disposable local demo credential. Only Nginx is exposed, bound to loopback.
This is a teaching sample, not production commerce: no authentication, stock
management, payment idempotency, or real payment integration is provided.

## Instrumentation opportunities

1. Establish OTel initialization, service identity, and OTLP configuration.
2. Instrument Flask, requests, and psycopg with context propagation.
3. Generate/export request metrics and connect infrastructure monitoring for
   Nginx/PostgreSQL through existing Grafana setup flows.
4. Structure logs and attach trace/span identifiers once tracing exists.
5. Add checkout-specific spans and bounded outcome attributes.

## Smoke check

With the application running, run from this directory:

```sh
python3 smoke.py
```

This exercises catalog reads, normal/slow/declined payments, input validation,
and order persistence. It creates two successful demo orders.

This app lives in `Alex3k/sample_apps` under `logs-only-shop/`. Run Compose and
instrumentation changes in this directory; sibling applications are independent.
