# db_manager.py

import os
import sqlite3

DB_PATH = os.path.join(os.getcwd(), "clinic.db")

def get_connection():
    """
    Return a new SQLite connection with row_factory set to sqlite3.Row.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def _initialize_database():
    conn = get_connection()
    cur  = conn.cursor()

    # ── Owners ──
    cur.execute("""
    CREATE TABLE IF NOT EXISTS owners (
        id    INTEGER PRIMARY KEY AUTOINCREMENT,
        name  TEXT,
        phone TEXT UNIQUE
    );
    """)

    # ── Species ──
    cur.execute("""
    CREATE TABLE IF NOT EXISTS species (
        id   INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE
    );
    """)

    # ── Pets ──
    cur.execute("""
    CREATE TABLE IF NOT EXISTS pets (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        owner_id     INTEGER,
        pet_name     TEXT,
        species_id   INTEGER,
        first_visit  TEXT,
        gender       TEXT,
        FOREIGN KEY(owner_id)   REFERENCES owners(id),
        FOREIGN KEY(species_id) REFERENCES species(id)
    );
    """)

    # ── Inventory ──
    # Allow multiple batches (same name, different expiry)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS inventory (
        id                 INTEGER PRIMARY KEY AUTOINCREMENT,
        name               TEXT,
        category           TEXT,
        quantity           INTEGER DEFAULT 0,
        unit               TEXT,
        reorder_level      INTEGER DEFAULT 0,
        expiration_date    TEXT,       -- YYYY-MM-DD
        default_sell_price REAL,
        UNIQUE(name, expiration_date)
    );
    """)

    # ── Visits ──
    cur.execute("""
    CREATE TABLE IF NOT EXISTS visits (
        id                INTEGER PRIMARY KEY AUTOINCREMENT,
        pet_id            INTEGER,
        visit_date        TEXT,       -- YYYY-MM-DD
        notes             TEXT,
        next_appointment  TEXT,       -- YYYY-MM-DD
        FOREIGN KEY(pet_id) REFERENCES pets(id)
    );
    """)

    # ── Prescriptions ──
    cur.execute("""
    CREATE TABLE IF NOT EXISTS prescriptions (
        id             INTEGER PRIMARY KEY AUTOINCREMENT,
        visit_id       INTEGER,
        inventory_id   INTEGER,
        quantity       INTEGER,
        unit_price     REAL,
        FOREIGN KEY(visit_id)     REFERENCES visits(id),
        FOREIGN KEY(inventory_id) REFERENCES inventory(id)
    );
    """)

    conn.commit()
    conn.close()

# initialize on import
_initialize_database()

# ── Owners ──

def get_owner_by_phone(phone: str):
    conn = get_connection(); cur = conn.cursor()
    cur.execute("SELECT id, name, phone FROM owners WHERE phone = ?", (phone,))
    row = cur.fetchone(); conn.close()
    return dict(row) if row else None

def add_owner(owner_data: dict) -> int:
    """
    owner_data = { 'name': str, 'phone': str }
    """
    conn = get_connection(); cur = conn.cursor()
    cur.execute(
        "INSERT OR IGNORE INTO owners (name, phone) VALUES (?, ?)",
        (owner_data['name'], owner_data['phone'])
    )
    conn.commit()
    cur.execute("SELECT id FROM owners WHERE phone = ?", (owner_data['phone'],))
    owner_id = cur.fetchone()['id']
    conn.close()
    return owner_id

# ── Species ──

def get_all_species() -> list[str]:
    conn = get_connection(); cur = conn.cursor()
    cur.execute("SELECT name FROM species ORDER BY name")
    rows = [r['name'] for r in cur.fetchall()]
    conn.close()
    return rows

def add_species(name: str) -> int:
    conn = get_connection(); cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO species (name) VALUES (?)", (name,))
    conn.commit()
    cur.execute("SELECT id FROM species WHERE name = ?", (name,))
    sp_id = cur.fetchone()['id']
    conn.close()
    return sp_id

# ── Pets ──

def get_pets_by_owner(owner_id: int) -> list[tuple[str,str]]:
    """
    Returns list of (species, pet_name) for a given owner_id.
    """
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        SELECT s.name AS species, p.pet_name
          FROM pets p
          JOIN species s ON p.species_id = s.id
         WHERE p.owner_id = ?
    """, (owner_id,))
    rows = [(r['species'], r['pet_name']) for r in cur.fetchall()]
    conn.close()
    return rows

def add_pet(pet_data: dict) -> int:
    """
    pet_data = {
      'owner_id': int,
      'pet_name': str,
      'species':  str,
      'first_visit': 'YYYY-MM-DD',
      'gender': str
    }
    """
    conn = get_connection(); cur = conn.cursor()
    # ensure species exists
    cur.execute("SELECT id FROM species WHERE name = ?", (pet_data['species'],))
    sp = cur.fetchone()
    species_id = sp['id'] if sp else add_species(pet_data['species'])

    cur.execute("""
        INSERT INTO pets
          (owner_id, pet_name, species_id, first_visit, gender)
        VALUES (?, ?, ?, ?, ?)
    """, (
        pet_data['owner_id'],
        pet_data['pet_name'],
        species_id,
        pet_data['first_visit'],
        pet_data['gender']
    ))
    conn.commit()
    pet_id = cur.lastrowid
    conn.close()
    return pet_id

def find_pet(owner_id: int, species: str, pet_name: str):
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        SELECT p.id, p.owner_id, p.pet_name, s.name AS species,
               p.first_visit, p.gender
          FROM pets p
          JOIN species s ON p.species_id = s.id
         WHERE p.owner_id = ?
           AND s.name     = ?
           AND p.pet_name = ?
    """, (owner_id, species, pet_name))
    row = cur.fetchone(); conn.close()
    return dict(row) if row else None

def update_pet(pet_id: int, pet_data: dict) -> None:
    conn = get_connection(); cur = conn.cursor()
    cur.execute("SELECT id FROM species WHERE name = ?", (pet_data['species'],))
    sp = cur.fetchone()
    species_id = sp['id'] if sp else add_species(pet_data['species'])

    cur.execute("""
        UPDATE pets
           SET pet_name   = ?,
               species_id = ?,
               first_visit= ?,
               gender     = ?
         WHERE id = ?
    """, (
        pet_data['pet_name'],
        species_id,
        pet_data['first_visit'],
        pet_data['gender'],
        pet_id
    ))
    conn.commit()
    conn.close()

# ── Inventory ──

def get_all_inventory() -> list[dict]:
    conn = get_connection(); cur = conn.cursor()
    cur.execute("SELECT * FROM inventory ORDER BY name, expiration_date")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

def add_or_restock_inventory(batch: dict) -> int:
    """
    batch = {
      'name':               str,
      'category':           str,
      'quantity':           int,
      'unit':               str,
      'reorder_level':      int,
      'expiration_date':    'YYYY-MM-DD',
      'default_sell_price': float
    }
    """
    conn = get_connection(); cur = conn.cursor()
    # look for existing batch
    cur.execute("""
      SELECT id, quantity
        FROM inventory
       WHERE name = ?
         AND expiration_date = ?
    """, (batch['name'], batch['expiration_date']))
    existing = cur.fetchone()

    if existing:
        inv_id  = existing['id']
        new_qty = existing['quantity'] + batch['quantity']
        cur.execute("""
          UPDATE inventory
             SET quantity          = ?,
                 default_sell_price = ?
           WHERE id = ?
        """, (new_qty, batch['default_sell_price'], inv_id))
    else:
        cur.execute("""
          INSERT INTO inventory
            (name, category, quantity, unit,
             reorder_level, expiration_date,
             default_sell_price)
          VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
          batch['name'],
          batch['category'],
          batch['quantity'],
          batch['unit'],
          batch['reorder_level'],
          batch['expiration_date'],
          batch['default_sell_price']
        ))
        inv_id = cur.lastrowid

    conn.commit()
    conn.close()
    return inv_id

def update_inventory_item(item_id: int, item: dict) -> None:
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        UPDATE inventory
           SET name               = ?,
               category           = ?,
               quantity           = ?,
               unit               = ?,
               reorder_level      = ?,
               expiration_date    = ?,
               default_sell_price = ?
         WHERE id = ?
    """, (
        item['name'], item['category'], item['quantity'],
        item['unit'], item['reorder_level'], item['expiration_date'],
        item['default_sell_price'], item_id
    ))
    conn.commit()
    conn.close()

def delete_inventory_item(item_id: int) -> None:
    conn = get_connection(); cur = conn.cursor()
    cur.execute("DELETE FROM inventory WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()

def get_low_stock_items() -> list[dict]:
    conn = get_connection(); cur = conn.cursor()
    cur.execute("SELECT * FROM inventory WHERE quantity <= reorder_level")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

def get_inventory_batches(name: str) -> list[dict]:
    """
    Return all batches for a given medicine name,
    sorted by soonest expiration_date first.
    """
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
      SELECT id, expiration_date, quantity, default_sell_price
        FROM inventory
       WHERE name = ?
       ORDER BY expiration_date ASC
    """, (name,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

# ── Visits & Prescriptions ──

def get_visits_by_pet(pet_id: int) -> list[dict]:
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
      SELECT id, visit_date, notes, next_appointment
        FROM visits
       WHERE pet_id = ?
       ORDER BY visit_date DESC
    """, (pet_id,))
    rows = [dict(r) for r in cur.fetchall()]; conn.close()
    return rows

def add_visit(data: dict) -> int:
    """
    data = {
      'pet_id': int,
      'visit_date': 'YYYY-MM-DD',
      'notes': str,
      'next_appointment': 'YYYY-MM-DD'
    }
    """
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
      INSERT INTO visits
        (pet_id, visit_date, notes, next_appointment)
      VALUES (?, ?, ?, ?)
    """, (
      data['pet_id'], data['visit_date'],
      data['notes'], data['next_appointment']
    ))
    vid = cur.lastrowid
    conn.commit(); conn.close()
    return vid

def add_prescription(presc: dict) -> int:
    """
    presc = {
      'visit_id': int,
      'inventory_id': int,
      'quantity': int,
      'unit_price': float
    }
    """
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
      INSERT INTO prescriptions
        (visit_id, inventory_id, quantity, unit_price)
      VALUES (?, ?, ?, ?)
    """, (
      presc['visit_id'], presc['inventory_id'],
      presc['quantity'], presc['unit_price']
    ))
    pid = cur.lastrowid
    conn.commit(); conn.close()
    return pid
