CREATE TABLE products (id integer PRIMARY KEY, name text NOT NULL, price_cents integer NOT NULL CHECK (price_cents > 0));
INSERT INTO products VALUES (1, 'Trail mug', 1800), (2, 'Field notebook', 1200), (3, 'Canvas tote', 2400);
CREATE TABLE orders (id uuid PRIMARY KEY, product_id integer REFERENCES products(id), quantity integer NOT NULL, total_cents integer NOT NULL, created_at timestamptz DEFAULT now());
