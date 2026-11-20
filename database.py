import sqlite3
from contextlib import contextmanager
from typing import Generator, List, Optional, Tuple
import pandas as pd

DB_NAME = "clothing_store.db"


@contextmanager
def get_connection() -> Generator[sqlite3.Connection, None, None]:
    """Context manager for safe SQLite database connections."""
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    """Initialize the SQLite database and create the products table if missing."""
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                size TEXT NOT NULL,
                color TEXT NOT NULL,
                price REAL NOT NULL CHECK(price > 0),
                stock INTEGER NOT NULL CHECK(stock >= 0),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def add_product(
    name: str, size: str, color: str, price: float, stock: int
) -> Tuple[bool, str]:
    """Add a new clothing item or update stock if exact item already exists."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, stock FROM products
                WHERE LOWER(name) = LOWER(?) AND size = ? AND LOWER(color) = LOWER(?)
                """,
                (name.strip(), size, color.strip()),
            )
            existing = cursor.fetchone()

            if existing:
                new_stock = existing["stock"] + stock
                cursor.execute(
                    "UPDATE products SET stock = ?, price = ? WHERE id = ?",
                    (new_stock, round(float(price), 2), existing["id"]),
                )
                return True, f"Updated existing product stock to {new_stock}."

            cursor.execute(
                """
                INSERT INTO products (name, size, color, price, stock)
                VALUES (?, ?, ?, ?, ?)
                """,
                (name.strip(), size, color.strip(), round(float(price), 2), int(stock)),
            )
            return True, f"Added '{name.strip()}' ({size}, {color.strip()}) successfully."
    except sqlite3.Error as exc:
        return False, f"Database error: {exc}"


def get_all_products() -> pd.DataFrame:
    """Retrieve all clothing products ordered by newest first as a Pandas DataFrame."""
    with get_connection() as conn:
        query = """
            SELECT id, name, size, color, price, stock, created_at
            FROM products
            ORDER BY id DESC
        """
        df = pd.read_sql_query(query, conn)
    return df


def sell_product(product_id: int, quantity: int) -> Tuple[bool, str, Optional[float]]:
    """
    Deduct sold quantity from stock if sufficient inventory exists.
    Returns (success, message, total_sale_amount).
    """
    if quantity <= 0:
        return False, "Sale quantity must be at least 1.", None

    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name, size, color, price, stock FROM products WHERE id = ?",
                (product_id,),
            )
            product = cursor.fetchone()

            if not product:
                return False, "Selected product was not found.", None

            if product["stock"] < quantity:
                return (
                    False,
                    f"Insufficient stock. Only {product['stock']} unit(s) available.",
                    None,
                )

            updated_stock = product["stock"] - quantity
            total_amount = round(product["price"] * quantity, 2)

            cursor.execute(
                "UPDATE products SET stock = ? WHERE id = ?",
                (updated_stock, product_id),
            )
            msg = (
                f"Sold {quantity}x {product['name']} ({product['size']}, {product['color']}) "
                f"for ${total_amount:.2f}. Remaining stock: {updated_stock}."
            )
            return True, msg, total_amount
    except sqlite3.Error as exc:
        return False, f"Database error during sale: {exc}", None


def delete_product(product_id: int) -> Tuple[bool, str]:
    """Delete a clothing product permanently by ID."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM products WHERE id = ?", (product_id,))
            product = cursor.fetchone()

            if not product:
                return False, "Product not found."

            cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
            return True, f"Deleted '{product['name']}' (ID: {product_id}) from inventory."
    except sqlite3.Error as exc:
        return False, f"Database error during deletion: {exc}"
