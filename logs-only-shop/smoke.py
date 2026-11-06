"""Run against docker compose up. Creates two successful demo orders."""
import json
import subprocess
import time
import urllib.error
import urllib.request

BASE = 'http://127.0.0.1:3310'


def order_count():
    return int(subprocess.check_output(['docker', 'compose', 'exec', '-T', 'db', 'psql', '-U', 'shop', '-d', 'shop', '-Atc', 'SELECT count(*) FROM orders'], text=True).strip())


def checkout(scenario, expected_status, quantity=1):
    data = json.dumps({'product_id': 1, 'quantity': quantity, 'scenario': scenario}).encode()
    request = urllib.request.Request(BASE + '/api/checkout', data=data, headers={'Content-Type': 'application/json'})
    started = time.monotonic()
    try:
        response = urllib.request.urlopen(request, timeout=10)
    except urllib.error.HTTPError as error:
        response = error
    body = json.load(response)
    assert response.code == expected_status, (response.code, body)
    if expected_status == 201:
        assert body['total_cents'] == 1800 * quantity
        assert body['order_id']
    if scenario == 'slow':
        assert time.monotonic() - started >= 1.4
    print(scenario, response.code)


before = order_count()
with urllib.request.urlopen(BASE + '/api/products') as response:
    assert len(json.load(response)) == 3
checkout('normal', 201)
checkout('slow', 201)
checkout('declined', 422)
checkout('normal', 400, quantity=0)
assert order_count() == before + 2, 'Only successful checkouts should persist'
print('PASS: catalog, normal/slow/declined checkout, validation, and database persistence')
