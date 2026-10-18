"""A system for managing products, inventory, and sales."""

import sqlite3


def connect_database():
    """Connect to the inventory database."""
    connection = sqlite3.connect("inventory.db")
    return connection


def create_tables():
    """Create the products and sales tables if they don't exist."""
    connection = connect_database()
    cursor = connection.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT, 
    name TEXT NOT NULL, 
    price REAL NOT NULL, 
    quantity INTEGER NOT NULL)""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT, 
    product_name TEXT NOT NULL, 
    quantity INTEGER NOT NULL, 
    total REAL NOT NULL)""")

    connection.commit()
    connection.close()


create_tables()


def show_menu():
    """Display the main menu options."""
    print("\n===== INVENTORY MANAGEMENT SYSTEM =====")
    print("1. Add product")
    print("2. View inventory")
    print("3. Update stock")
    print("4. Search for a product")
    print("5. Record a sale")
    print("6. View sales report")
    print("7. View low-stock products")
    print("8. Exit")


def add_product():
    """Add a new product to the inventory."""
    name = input("Enter product name: ").strip()

    if not name:
        print('Product name cannot be empty.')
        return
    try:
        price = float(input("Enter product price: "))
        quantity = int(input("Enter product quantity: "))
    except ValueError:
        print('Please input a valid number.')
        return

    if price <= 0 or quantity < 0:
        print("Price must be greater than zero and quantity cannot be negative.")
        return
    connection = connect_database()
    cursor = connection.cursor()

    cursor.execute(
        "INSERT INTO products ( name, price, quantity) VALUES (?, ?, ?)", (name, price, quantity))
    connection.commit()
    connection.close()

    print(f"{name} added successfully!")


def view_inventory():
    """Display all products stored in the database."""
    connection = connect_database()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()

    connection.close()

    if not products:
        print("Your inventory is empty.")
        return

    print("\n==== CURRENT INVENTORY ====")

    for product in products:
        print(
            f"ID: {product[0]} | "
            f"Name: {product[1]} | "
            f"Price: ${product[2]:.2f} | "
            f"Quantity: {product[3]}")


def update_stock():
    """Increases or decreases a product's stock quantity."""
    view_inventory()

    connection = connect_database()
    cursor = connection.cursor()

    try:
        product_id = int(input("Enter the product ID to update: "))
        change = int(input("Enter quantity to add or remove (+/-): "))
    except ValueError:
        print("Please enter a valid whole numbers.")
        connection.close()
        return

    cursor.execute(
        "SELECT quantity FROM products WHERE id = ?", (product_id,))
    result = cursor.fetchone()

    if result is None:
        print("Product ID not found.")
        connection.close()
        return

    new_quantity = result[0] + change

    if new_quantity < 0:
        print("Stock cannot be negative")
        connection.close()
        return

    cursor.execute("UPDATE products SET quantity = ? WHERE id = ?",
                   (new_quantity, product_id))

    connection.commit()
    connection.close()

    print(f"Stock updated! New quantity: {new_quantity}")


def search_product():
    """Search for a product by name"""
    search_name = input("Enter a product name to search: ").strip()

    if not search_name:
        print("Please enter a product name.")
        return
    connection = connect_database()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM products WHERE name LIKE ?",
                   (f"%{search_name}%",))

    results = cursor.fetchall()
    connection.close()

    if not results:
        print("No matching products found.")
        return

    print("\n==== SEARCH RESULTS ====")

    for product in results:
        print(f"ID: {product[0]} |"
              f"Name: {product[1]} |"
              f"Price: ${product[2]:.2f} |"
              f"Quantity: {product[3]}")


def view_low_stock():
    """Display products with fewer than five items remaining."""
    threshold = 5

    connection = connect_database()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT id, name, price, quantity FROM products WHERE quantity < ?", (threshold,))

    low_stock_products = cursor.fetchall()
    connection.close()

    if not low_stock_products:
        print("No low-stock products found.")
        return
    print("\n==== LOW-STOCK PRODUCTS ====")

    for product in low_stock_products:
        print(f"ID: {product[0]}: | "
              f"Name: {product[1]} | "
              f"Price: {product[2]:.2f} | "
              f"Quantity remaining: {product[3]}")


def record_sales():
    """Record a sale and update inventory."""

    view_inventory()

    connection = connect_database()
    cursor = connection.cursor()
    try:
        product_id = int(input("Enter the product ID sold: "))
        quantity_sold = int(input("Enter quantity sold: "))
    except ValueError:
        print("Please enter a valid whole number.")
        connection.close()
        return
    if quantity_sold <= 0:
        print("Quantity sold must be greater than zero.")
        connection.close()
        return

    cursor.execute(
        "SELECT name, price, quantity FROM products WHERE id = ?", (product_id,))
    product = cursor.fetchone()

    if product is None:
        print("Product ID not found.")
        connection.close()
        return

    name, price, stock = product

    if quantity_sold > stock:
        print(f"Insufficient stock! Available quantity: {stock}")
        connection.close()
        return

    total = price * quantity_sold
    new_stock = stock - quantity_sold

    try:
        cursor.execute(
            " UPDATE products SET quantity = ? WHERE id = ?", (new_stock, product_id))

        cursor.execute(
            """INSERT INTO sales (product_name, quantity, total) 
            VALUES (?, ?, ?)""", (name, quantity_sold, total))

        connection.commit()

    except sqlite3.Error as error:
        connection.rollback()
        print(f"Could not record the sale: {error}")
        return

    finally:
        connection.close()

    print(f"Sale recorded: {quantity_sold} x {name}")
    print(f"Sale total: ${total:.2f}")
    print(f"Remaining stock: {new_stock}")


def view_sales_report():
    """Display recorded sales and calculate total revenue."""
    connection = connect_database()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM sales")
    sales = cursor.fetchall()

    connection.close()

    if not sales:
        print("No sales recorded yet.")
        return

    total_revenue = 0
    print("\n==== SALES REPORT ====")

    for sale in sales:
        print(f"Sale ID: {sale[0]} | "
              f"Product: {sale[1]} | "
              f"Quantity: {sale[2]} | "
              f"Total: ${sale[3]:.2f}")
        total_revenue += sale[3]

    print(f"\nTotal revenue: ${total_revenue:.2f}")


while True:
    show_menu()

    Choice = input("Enter your choice (1-8): ")
    if Choice == '1':
        add_product()

    elif Choice == "2":
        view_inventory()

    elif Choice == "3":
        update_stock()

    elif Choice == "4":
        search_product()

    elif Choice == "5":
        record_sales()

    elif Choice == "6":
        view_sales_report()

    elif Choice == "7":
        view_low_stock()

    elif Choice == "8":
        print("Thank you for using the Inventory Management System!")
        break
    else:
        print("Invalid choice. Please enter a number between 1 and 8.")


# input("Press Enter to close...")
