import logging
import os
import streamlit as st

from database import (
    add_product,
    delete_product,
    get_all_products,
    init_db,
    sell_product,
)
from security import validate_product_input, verify_admin_password

# Configure page settings
st.set_page_config(
    page_title="Clothing Store Management System",
    page_icon="👕",
    layout="wide",
)

# Configure Python logging to write to both file and console
LOG_FILE = "store_system.log"
logger = logging.getLogger("ClothingStoreLogger")
logger.setLevel(logging.INFO)

if not logger.handlers:
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

# Initialize database on startup
init_db()

# Initialize session state variables
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False


def render_login() -> None:
    """Render the Admin Login screen."""
    st.title("👕 Clothing Store Management System")
    st.subheader("Admin Login")

    col1, _ = st.columns([1, 2])
    with col1:
        with st.form("login_form"):
            password = st.text_input("Admin Password", type="password", placeholder="Enter password")
            submitted = st.form_submit_button("Login", use_container_width=True)

            if submitted:
                if verify_admin_password(password):
                    st.session_state.authenticated = True
                    logger.info("Admin logged in successfully.")
                    st.rerun()
                else:
                    logger.warning("Failed admin login attempt.")
                    st.error("Invalid password. Please try again.")


def render_inventory_dashboard() -> None:
    """Render the Inventory Dashboard with KPIs, search filter, and delete option."""
    st.header("📦 Inventory Dashboard")

    df = get_all_products()

    # Summary KPIs
    total_skus = len(df)
    total_units = int(df["stock"].sum()) if not df.empty else 0
    inventory_value = float((df["price"] * df["stock"]).sum()) if not df.empty else 0.0
    low_stock_count = int((df["stock"] <= 5).sum()) if not df.empty else 0

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Total Products (SKUs)", total_skus)
    kpi2.metric("Total Units in Stock", total_units)
    kpi3.metric("Total Inventory Value", f"${inventory_value:,.2f}")
    kpi4.metric("Low Stock Items (≤ 5)", low_stock_count)

    st.divider()

    if df.empty:
        st.info("No clothing items in inventory yet. Go to 'Add New Clothing' to add stock.")
        return

    # Search / Filter bar
    search_query = st.text_input("🔍 Search by Product Name or Color", "").strip().lower()
    if search_query:
        filtered_df = df[
            df["name"].str.lower().str.contains(search_query)
            | df["color"].str.lower().str.contains(search_query)
        ]
    else:
        filtered_df = df

    st.dataframe(
        filtered_df.style.format({"price": "${:.2f}"}),
        use_container_width=True,
        hide_index=True,
    )

    # Delete Product Section
    st.subheader("🗑️ Remove Product from Inventory")
    col1, col2 = st.columns([3, 1])
    with col1:
        product_options = {
            f"ID {row['id']} — {row['name']} ({row['size']}, {row['color']}) [Stock: {row['stock']}]": row["id"]
            for _, row in df.iterrows()
        }
        selected_label = st.selectbox("Select item to delete", list(product_options.keys()))

    with col2:
        st.write("")
        st.write("")
        if st.button("Delete Product", type="primary", use_container_width=True):
            prod_id = product_options[selected_label]
            success, message = delete_product(prod_id)
            if success:
                logger.info(f"DELETE: {message}")
                st.success(message)
                st.rerun()
            else:
                logger.error(f"DELETE FAILED: {message}")
                st.error(message)


def render_add_product() -> None:
    """Render form to add new clothing items."""
    st.header("➕ Add New Clothing")

    with st.form("add_clothing_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Product Name *", placeholder="e.g., Classic Cotton T-Shirt")
            size = st.selectbox("Size *", ["XS", "S", "M", "L", "XL", "XXL", "Free Size"])
        with col2:
            color = st.text_input("Color *", placeholder="e.g., Navy Blue")
            price = st.number_input("Unit Price ($) *", min_value=0.01, value=19.99, step=0.50, format="%.2f")

        stock = st.number_input("Initial Stock Quantity *", min_value=0, value=10, step=1)
        submitted = st.form_submit_button("Save Clothing Item", use_container_width=True)

        if submitted:
            is_valid, error_msg = validate_product_input(name, color, price, int(stock))
            if not is_valid:
                st.error(error_msg)
                return

            success, message = add_product(name, size, color, price, int(stock))
            if success:
                logger.info(f"INVENTORY ADD: {message}")
                st.success(message)
            else:
                logger.error(f"INVENTORY ADD FAILED: {message}")
                st.error(message)


def render_process_sale() -> None:
    """Render POS screen to sell clothing and deduct stock."""
    st.header("💳 Process Sale")

    df = get_all_products()
    in_stock_df = df[df["stock"] > 0] if not df.empty else df

    if in_stock_df.empty:
        st.warning("No items currently in stock to sell.")
        return

    product_map = {
        f"{row['name']} | Size: {row['size']} | Color: {row['color']} — ${row['price']:.2f} ({row['stock']} left)": row
        for _, row in in_stock_df.iterrows()
    }

    selected_label = st.selectbox("Select Clothing Item", list(product_map.keys()))
    selected_product = product_map[selected_label]

    max_qty = int(selected_product["stock"])
    quantity = st.number_input(
        "Quantity to Sell",
        min_value=1,
        max_value=max_qty,
        value=1,
        step=1,
    )

    total_price = selected_product["price"] * quantity
    st.info(f"**Total Sale Amount:** ${total_price:,.2f}")

    if st.button("Complete Sale", type="primary"):
        success, message, _ = sell_product(int(selected_product["id"]), int(quantity))
        if success:
            logger.info(f"SALE: {message}")
            st.success(message)
            st.rerun()
        else:
            logger.warning(f"SALE FAILED: {message}")
            st.error(message)


def render_system_logs() -> None:
    """Render audit logs recorded via Python's logging module."""
    st.header("📜 System Logs")

    col1, col2 = st.columns([4, 1])
    with col2:
        if st.button("Clear Logs", use_container_width=True):
            with open(LOG_FILE, "w", encoding="utf-8") as f:
                f.write("")
            logger.info("System logs cleared by admin.")
            st.rerun()

    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            logs = f.read()
        if logs.strip():
            st.text_area("Audit Trail (Newest at Bottom)", value=logs, height=400, disabled=True)
        else:
            st.info("Log file is currently empty.")
    else:
        st.info("No log entries recorded yet.")


def main() -> None:
    """Main application controller."""
    if not st.session_state.authenticated:
        render_login()
        return

    with st.sidebar:
        st.title("🛍️ Store Admin")
        page = st.radio(
            "Navigation",
            [
                "Inventory Dashboard",
                "Add New Clothing",
                "Process Sale",
                "System Logs",
            ],
        )
        st.divider()
        if st.button("Logout", use_container_width=True):
            logger.info("Admin logged out.")
            st.session_state.authenticated = False
            st.rerun()

    if page == "Inventory Dashboard":
        render_inventory_dashboard()
    elif page == "Add New Clothing":
        render_add_product()
    elif page == "Process Sale":
        render_process_sale()
    elif page == "System Logs":
        render_system_logs()


if __name__ == "__main__":
    main()
