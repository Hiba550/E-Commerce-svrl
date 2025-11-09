import sqlite3

DB = 'app.db'

def main():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [t[0] for t in cur.fetchall()]
    print('Tables in', DB, ':', tables)

    if 'products' in tables:
        cur.execute('SELECT id, name, slug, is_active, stock_quantity FROM products')
        rows = cur.fetchall()
        print('\nProducts (first 50 rows):')
        for r in rows[:50]:
            print('  ', r)
        print('\nTotal products:', len(rows))
    else:
        print('\nNo products table found in DB')

    # Print categories and a few users for context
    if 'categories' in tables:
        cur.execute('SELECT id, name, slug, is_active FROM categories')
        cats = cur.fetchall()
        print('\nCategories:')
        for c in cats:
            print('  ', c)

    if 'users' in tables:
        cur.execute('SELECT id, username, email, user_type FROM users LIMIT 10')
        us = cur.fetchall()
        print('\nUsers (up to 10):')
        for u in us:
            print('  ', u)

    conn.close()

if __name__ == "__main__":
    main()
