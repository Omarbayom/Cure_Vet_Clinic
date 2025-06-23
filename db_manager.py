# db_manager.py
import os
import sqlite3

DB_PATH = os.path.join(os.getcwd(), "clinic.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def _initialize_database():
    conn = get_connection()
    cur  = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS owners (
        id    INTEGER PRIMARY KEY AUTOINCREMENT,
        name  TEXT,
        phone TEXT UNIQUE
    );
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS species (
        id   INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE
    );
    """)
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
    conn.commit()
    conn.close()

_initialize_database()

# Owners
def get_owner_by_phone(phone: str):
    conn = get_connection(); cur = conn.cursor()
    cur.execute("SELECT id, name, phone FROM owners WHERE phone = ?", (phone,))
    row = cur.fetchone(); conn.close()
    return dict(row) if row else None

def add_owner(owner_data: dict) -> int:
    conn = get_connection(); cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO owners (name, phone) VALUES (?, ?)",
                (owner_data['name'], owner_data['phone']))
    conn.commit()
    cur.execute("SELECT id FROM owners WHERE phone = ?", (owner_data['phone'],))
    owner_id = cur.fetchone()['id']; conn.close()
    return owner_id

# Species
def get_all_species():
    conn = get_connection(); cur = conn.cursor()
    cur.execute("SELECT name FROM species ORDER BY name")
    rows = [r['name'] for r in cur.fetchall()]; conn.close()
    return rows

def add_species(name: str) -> int:
    conn = get_connection(); cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO species (name) VALUES (?)", (name,))
    conn.commit()
    cur.execute("SELECT id FROM species WHERE name = ?", (name,))
    sp_id = cur.fetchone()['id']; conn.close()
    return sp_id


# Pets
def get_pets_by_owner(owner_id: int):
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
    conn = get_connection(); cur = conn.cursor()
    # species_id
    cur.execute("SELECT id FROM species WHERE name = ?", (pet_data['species'],))
    sp = cur.fetchone()
    species_id = sp['id'] if sp else add_species(pet_data['species'])
    # insert
    cur.execute("""
        INSERT INTO pets 
          (owner_id, pet_name, species_id,
           first_visit, gender)
        VALUES (?, ?, ?, ?, ?)
    """, (
        pet_data['owner_id'], pet_data['pet_name'], species_id,
        pet_data['first_visit'], pet_data['gender']
    ))
    conn.commit()
    pet_id = cur.lastrowid; conn.close()
    return pet_id

def find_pet(owner_id: int, species: str, pet_name: str):
    """
    Return the pet row (including its id) if that owner already has
    a pet of this species and name, else None.
    """
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("""
        SELECT p.id,
               p.owner_id,
               p.pet_name,
               s.name   AS species,
               p.first_visit,
               p.gender
          FROM pets p
          JOIN species s ON p.species_id = s.id
         WHERE p.owner_id = ?
           AND s.name     = ?
           AND p.pet_name = ?
    """, (owner_id, species, pet_name))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None

def update_pet(pet_id: int, pet_data: dict) -> None:
    """
    Update an existing pet record. pet_data keys are same as in add_pet.
    """
    conn = get_connection()
    cur  = conn.cursor()

    # lookup or insert species
    cur.execute("SELECT id FROM species WHERE name = ?", (pet_data['species'],))
    sp = cur.fetchone()
    species_id = sp['id'] if sp else add_species(pet_data['species'])

    # perform update
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
