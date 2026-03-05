import sqlite3
import os

db_path = "priceintel.db"

def migrate():
    if not os.path.exists(db_path):
        print(f"Error: Database {db_path} not found.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("Checking for 'colors' column in 'price_sheet_pincodes'...")
    try:
        cursor.execute("PRAGMA table_info(price_sheet_pincodes)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'colors' not in columns:
            print("Adding 'colors' column to 'price_sheet_pincodes'...")
            cursor.execute("ALTER TABLE price_sheet_pincodes ADD COLUMN colors TEXT")
            conn.commit()

        # Add product_url to price_sheet_rows
        cursor.execute("PRAGMA table_info(price_sheet_rows)")
        columns_rows = [column[1] for column in cursor.fetchall()]
        if 'product_url' not in columns_rows:
            print("Adding 'product_url' column to 'price_sheet_rows'...")
            cursor.execute("ALTER TABLE price_sheet_rows ADD COLUMN product_url TEXT")
            conn.commit()
            
        if 'retailer' not in columns_rows:
            print("Adding 'retailer' column to 'price_sheet_rows'...")
            cursor.execute("ALTER TABLE price_sheet_rows ADD COLUMN retailer TEXT")
            conn.commit()
            print("Migration successful: 'retailer' column added.")

        # Add delivery_info and colors to products
        cursor.execute("PRAGMA table_info(products)")
        columns_products = [column[1] for column in cursor.fetchall()]
        if 'delivery_info' not in columns_products:
            print("Adding 'delivery_info' column to 'products'...")
            cursor.execute("ALTER TABLE products ADD COLUMN delivery_info TEXT")
            conn.commit()
        if 'colors' not in columns_products:
            print("Adding 'colors' column to 'products'...")
            cursor.execute("ALTER TABLE products ADD COLUMN colors TEXT")
            conn.commit()
            
        print("Migration check complete.")
            
    except sqlite3.OperationalError as e:
        print(f"Error during migration: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
