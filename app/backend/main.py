# main.py

# Import json so we can serialize product lists into Redis cache.
import json

# Import os so the application can read environment variables
# injected by Kubernetes ConfigMap / Secret.
import os

# Import psycopg2 so the backend can connect to PostgreSQL.
import psycopg2

# Import redis so the backend can talk to Redis cache.
import redis

# Import FastAPI so we can create our backend API application.
from fastapi import FastAPI

# Import CORSMiddleware so the browser frontend running on a different
# origin can call this backend during local testing or transitional stages.
from fastapi.middleware.cors import CORSMiddleware

# Import BaseModel so we can define the request body schema for creating
# a new product through the API.
from pydantic import BaseModel


# -------------------------------------------------------------------
# Request model
# -------------------------------------------------------------------
class ProductCreateRequest(BaseModel):
    """
    Request payload for creating a new product.
    """
    name: str
    price: int


# Create the FastAPI application instance.
app = FastAPI(
    title="ShopStack Backend",
    description="Backend API for the ShopStack Kubernetes project",
    version="1.0.0",
)

# -------------------------------------------------------------------
# CORS configuration
# -------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------------------
# Redis cache constants
# -------------------------------------------------------------------
PRODUCTS_CACHE_KEY = "products:all"


# -------------------------------------------------------------------
# Database helper functions
# -------------------------------------------------------------------
def get_db_connection():
    """
    Create and return a PostgreSQL connection using environment variables
    provided by Kubernetes ConfigMap and Secret.
    """
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "missing"),
        port=os.getenv("DB_PORT", "missing"),
        dbname=os.getenv("DB_NAME", "missing"),
        user=os.getenv("DB_USER", "missing"),
        password=os.getenv("DB_PASSWORD", ""),
    )


def get_redis_client():
    """
    Create and return a Redis client using environment variables from
    the Kubernetes ConfigMap.
    """
    return redis.Redis(
        host=os.getenv("REDIS_HOST", "missing"),
        port=int(os.getenv("REDIS_PORT", "6379")),
        decode_responses=True,
    )


def initialize_database():
    """
    Create the products table if it does not exist and insert seed data
    if the table is empty.

    This function retries for a short period because in Kubernetes the
    backend container may start before PostgreSQL is fully ready to
    accept connections.
    """
    import time

    max_attempts = 10
    attempt_number = 1

    while attempt_number <= max_attempts:
        connection = None
        cursor = None

        try:
            print(f"[DB INIT] Attempt {attempt_number}/{max_attempts}")

            connection = get_db_connection()
            cursor = connection.cursor()

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS products (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    price INTEGER NOT NULL
                );
                """
            )

            cursor.execute("SELECT COUNT(*) FROM products;")
            product_count = cursor.fetchone()[0]

            if product_count == 0:
                cursor.execute(
                    """
                    INSERT INTO products (name, price)
                    VALUES
                        ('Mechanical Keyboard', 2500),
                        ('Wireless Mouse', 1200),
                        ('27 Inch Monitor', 15000);
                    """
                )

            connection.commit()
            print("[DB INIT] Database initialization successful")
            return

        except Exception as exc:
            print(f"[DB INIT] Database initialization failed: {exc}")

            # If initialization fails, wait a little and retry.
            time.sleep(3)

        finally:
            if cursor is not None:
                cursor.close()
            if connection is not None:
                connection.close()

        attempt_number += 1

    print("[DB INIT] Failed after maximum retry attempts")


# -------------------------------------------------------------------
# FastAPI startup hook
# -------------------------------------------------------------------
@app.on_event("startup")
def startup_event():
    """
    Initialize the database when the backend application starts.
    """
    initialize_database()


# -------------------------------------------------------------------
# Health endpoint
# -------------------------------------------------------------------
@app.get("/api/health")
def health_check():
    """
    Return a simple health response for the backend service.
    """
    return {
        "status": "ok",
        "service": "shopstack-backend",
    }


# -------------------------------------------------------------------
# Products endpoint - READ with Redis cache
# -------------------------------------------------------------------
@app.get("/api/products")
def get_products():
    """
    Return products using Redis cache first. If cache miss occurs, fetch
    from PostgreSQL, cache the result in Redis, and then return it.
    """
    redis_client = None
    connection = None
    cursor = None

    try:
        # ---------------------------------------------------------------
        # Try Redis cache first.
        # ---------------------------------------------------------------
        redis_client = get_redis_client()
        cached_products_json = redis_client.get(PRODUCTS_CACHE_KEY)

        if cached_products_json:
            return {
                "source": "redis-cache",
                "products": json.loads(cached_products_json),
            }

        # ---------------------------------------------------------------
        # Cache miss -> fetch from PostgreSQL.
        # ---------------------------------------------------------------
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT id, name, price
            FROM products
            ORDER BY id;
            """
        )

        rows = cursor.fetchall()

        products = []
        for row in rows:
            products.append(
                {
                    "id": row[0],
                    "name": row[1],
                    "price": row[2],
                }
            )

        # ---------------------------------------------------------------
        # Store the fresh DB result in Redis for future requests.
        # ---------------------------------------------------------------
        redis_client.set(PRODUCTS_CACHE_KEY, json.dumps(products))

        return {
            "source": "postgres",
            "products": products,
        }

    except Exception as exc:
        return {
            "status": "failed to fetch products",
            "error": str(exc),
        }

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()


# -------------------------------------------------------------------
# Products endpoint - CREATE
# -------------------------------------------------------------------
@app.post("/api/products")
def create_product(product: ProductCreateRequest):
    """
    Insert a new product into PostgreSQL and invalidate the Redis cache
    so the next GET /api/products fetches fresh data from PostgreSQL.
    """
    connection = None
    cursor = None
    redis_client = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO products (name, price)
            VALUES (%s, %s)
            RETURNING id, name, price;
            """,
            (product.name, product.price),
        )

        inserted_row = cursor.fetchone()
        connection.commit()

        # ---------------------------------------------------------------
        # Invalidate Redis cache after successful DB write so next read
        # does not return stale data.
        # ---------------------------------------------------------------
        redis_client = get_redis_client()
        redis_client.delete(PRODUCTS_CACHE_KEY)

        return {
            "id": inserted_row[0],
            "name": inserted_row[1],
            "price": inserted_row[2],
            "status": "product created successfully",
            "cache_status": "products cache invalidated",
        }

    except Exception as exc:
        if connection is not None:
            connection.rollback()

        return {
            "status": "failed to create product",
            "error": str(exc),
        }

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()


# -------------------------------------------------------------------
# Database check endpoint
# -------------------------------------------------------------------
@app.get("/api/db-check")
def db_check():
    """
    Attempt a real PostgreSQL connection using runtime configuration.
    """
    db_host = os.getenv("DB_HOST", "missing")
    db_port = os.getenv("DB_PORT", "missing")
    db_name = os.getenv("DB_NAME", "missing")
    db_user = os.getenv("DB_USER", "missing")
    db_password = os.getenv("DB_PASSWORD")

    response_payload = {
        "database_host": db_host,
        "database_port": db_port,
        "database_name": db_name,
        "database_user": db_user,
        "database_password_present": bool(db_password),
        "app_env": os.getenv("APP_ENV", "missing"),
        "log_level": os.getenv("LOG_LEVEL", "missing"),
    }

    if not db_password:
        response_payload["status"] = "database password missing"
        return response_payload

    connection = None

    try:
        connection = get_db_connection()
        response_payload["status"] = "database connection successful"
        return response_payload

    except Exception as exc:
        response_payload["status"] = "database connection failed"
        response_payload["error"] = str(exc)
        return response_payload

    finally:
        if connection is not None:
            connection.close()


# -------------------------------------------------------------------
# Cache check endpoint
# -------------------------------------------------------------------
@app.get("/api/cache-check")
def cache_check():
    """
    Check whether backend can connect to Redis and return Redis runtime
    configuration information.
    """
    redis_host = os.getenv("REDIS_HOST", "missing")
    redis_port = os.getenv("REDIS_PORT", "missing")

    response_payload = {
        "redis_host": redis_host,
        "redis_port": redis_port,
        "app_env": os.getenv("APP_ENV", "missing"),
        "log_level": os.getenv("LOG_LEVEL", "missing"),
    }

    try:
        redis_client = get_redis_client()
        redis_client.ping()

        response_payload["status"] = "redis connection successful"
        return response_payload

    except Exception as exc:
        response_payload["status"] = "redis connection failed"
        response_payload["error"] = str(exc)
        return response_payload