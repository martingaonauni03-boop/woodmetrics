"""Persistencia SQLite: transacciones, relaciones y restricciones del dominio."""
import sqlite3
from flask import current_app, g

SCHEMA = '''
CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT NOT NULL UNIQUE, password TEXT NOT NULL, role TEXT NOT NULL CHECK(role IN ('admin','operador')), active INTEGER NOT NULL DEFAULT 1 CHECK(active IN (0,1)));
CREATE TABLE IF NOT EXISTS categories(id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE);
CREATE TABLE IF NOT EXISTS board_types(id INTEGER PRIMARY KEY, category_id INTEGER NOT NULL REFERENCES categories(id), name TEXT NOT NULL, thickness REAL NOT NULL CHECK(thickness>0), finish TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS formats(id INTEGER PRIMARY KEY, type_id INTEGER NOT NULL REFERENCES board_types(id), name TEXT NOT NULL UNIQUE, length REAL NOT NULL CHECK(length>0), width REAL NOT NULL CHECK(width>0), enabled INTEGER NOT NULL DEFAULT 1 CHECK(enabled IN (0,1)));
CREATE TABLE IF NOT EXISTS clients(id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS settings(id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE, kerf REAL NOT NULL CHECK(kerf>0), min_length REAL NOT NULL CHECK(min_length>0), min_width REAL NOT NULL CHECK(min_width>0));
CREATE TABLE IF NOT EXISTS orders(id INTEGER PRIMARY KEY, client_id INTEGER NOT NULL REFERENCES clients(id), setting_id INTEGER NOT NULL REFERENCES settings(id), user_id INTEGER REFERENCES users(id), created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, name TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'Borrador' CHECK(status IN ('Borrador','Listo','Cancelado')), version INTEGER NOT NULL DEFAULT 1);
CREATE TABLE IF NOT EXISTS pieces(id INTEGER PRIMARY KEY, order_id INTEGER NOT NULL REFERENCES orders(id), type_id INTEGER NOT NULL REFERENCES board_types(id), name TEXT NOT NULL, length REAL NOT NULL CHECK(length>0), width REAL NOT NULL CHECK(width>0), quantity INTEGER NOT NULL CHECK(quantity>0), rotate INTEGER NOT NULL CHECK(rotate IN (0,1)));
'''

def db():
    if 'db' not in g:
        g.db = sqlite3.connect(current_app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
        g.db.execute('PRAGMA foreign_keys=ON')
    return g.db

def rows(sql, args=()):
    return db().execute(sql, args).fetchall()

def close_db(error=None):
    conn = g.pop('db', None)
    if conn is not None:
        conn.close()
