"""Deliberately logs-only services. No tracing SDK, metrics, or telemetry exporter."""
import logging
import os
import time
import uuid

import psycopg
import requests
from flask import Flask, jsonify, request

SERVICE = os.environ["SERVICE"]
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s " + SERVICE + " %(message)s")
log = logging.getLogger(SERVICE)
app = Flask(__name__)


def database():
    return psycopg.connect(os.environ["DATABASE_URL"])


@app.get("/health")
def health():
    return {"service": SERVICE, "status": "ok"}


@app.after_request
def log_request(response):
    log.info("%s %s returned %s", request.method, request.path, response.status_code)
    return response


if SERVICE == "catalog":
    @app.get("/products")
    def products():
        with database() as conn:
            rows = conn.execute("SELECT id, name, price_cents FROM products ORDER BY id").fetchall()
        log.info("Loaded %s products from PostgreSQL", len(rows))
        return jsonify([{"id": r[0], "name": r[1], "price_cents": r[2]} for r in rows])


if SERVICE == "payment":
    @app.post("/payments")
    def payments():
        body = request.get_json(silent=True) or {}
        if body.get("scenario") not in ("normal", "slow", "declined"):
            return {"error": "Invalid payment scenario"}, 400
        if body["scenario"] == "slow":
            log.info("Simulating slow payment processor")
            time.sleep(1.5)
        if body["scenario"] == "declined":
            log.warning("Simulated payment declined")
            return {"error": "Payment declined (simulation)"}, 422
        log.info("Simulated payment approved")
        return {"status": "approved"}


if SERVICE == "checkout":
    @app.post("/checkout")
    def checkout():
        body = request.get_json(silent=True) or {}
        product_id, quantity = body.get("product_id"), body.get("quantity")
        scenario = body.get("scenario", "normal")
        if type(product_id) is not int or type(quantity) is not int or not 1 <= quantity <= 10 or scenario not in ("normal", "slow", "declined"):
            return {"error": "Choose a product, quantity from 1 to 10, and a valid scenario"}, 400
        try:
            response = requests.get(os.environ["CATALOG_URL"] + "/products", timeout=3)
            response.raise_for_status()
            product = next((p for p in response.json() if p["id"] == product_id), None)
            if product is None:
                return {"error": "Product not found"}, 404
            total = product["price_cents"] * quantity
            log.info("Starting checkout for %s items", quantity)
            payment = requests.post(os.environ["PAYMENT_URL"] + "/payments", json={"amount_cents": total, "scenario": scenario}, timeout=5)
            if payment.status_code == 422:
                log.warning("Checkout rejected by payment service")
                return {"error": "Payment declined (simulation)"}, 422
            payment.raise_for_status()
            order_id = str(uuid.uuid4())
            with database() as conn:
                conn.execute("INSERT INTO orders (id, product_id, quantity, total_cents) VALUES (%s, %s, %s, %s)", (order_id, product_id, quantity, total))
            log.info("Order saved successfully")
            return {"order_id": order_id, "total_cents": total}, 201
        except (requests.RequestException, psycopg.Error):
            log.exception("Checkout dependency failed")
            return {"error": "A checkout dependency is unavailable. Try again."}, 503
