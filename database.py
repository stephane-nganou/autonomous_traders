import sqlite3
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(override=True)

DATABASE = "accounts.db"

with sqlite3.connect(DATABASE) as connection:
    cursor = connection.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS accounts (name TEXT PRIMARY KEY, account TEXT)')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            datetime DATETIME,
            type TEXT,
            message TEXT
        )
    ''')
    cursor.execute('CREATE TABLE IF NOT EXISTS market (date TEXT PRIMARY KEY, data TEXT)')
    connection.commit()


def write_account(name:str, account_dict: dict):
    json_data = json.dumps(account_dict)
    with sqlite3.connect(DATABASE) as connection:
        cursor = connection.cursor()
        cursor.execute(
            '''
                INSERT INTO accounts (name, account)
                VALUES (?, ?)
                ON CONFLICT(name) DO UPDATE SET account=excluded.account
            ''', (name.lower(), json_data)
        )
        connection.commit()

def read_account(name) -> dict | None:
    with sqlite3.connect(DATABASE) as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT account FROM accounts WHERE name = ?', (name.lower(),))
        row = cursor.fetchone()

        return json.loads(row[0]) if row else None

def write_log(name:str, type: str, message: str):
    """
    Write a log entry to the logs table.
    
    Args:
        name (str): The name associated with the log
        type (str): The type of log entry
        message (str): The log message
    """

    now = datetime.now().isoformat()

    with sqlite3.connect(DATABASE) as connection:
        cursor = connection.cursor()
        cursor.execute(
            '''
            INSERT INTO logs (name, datetime, type, message)
            VALUES (?, datetime('now'), ?, ?)
            ''', (name.lower(), type, message)
        )
        connection.commit()

def read_log(name:str, last_n: int = 10):
    """
    Read the most recent log entries for a given name.
    
    Args:
        name (str): The name to retrieve logs for
        last_n (int): Number of most recent entries to retrieve
        
    Returns:
        list: A list of tuples containing (datetime, type, message)
    """
    with sqlite3.connect(DATABASE) as connection:
        cursor = connection.cursor()
        cursor.execute(
            '''
                SELECT datetime, type, message FROM logs
                WHERE name = ?
                ORDER BY datetime DESC
                limit ?
            ''', (name.lower(), last_n)
        )

        return reversed(cursor.fetchall())


def write_market(date:str, data: dict):
    data_json = json.dumps(data)
    with sqlite3.connect(DATABASE) as connection:
        cursor = connection.cursor()
        cursor.execute(
            '''
                INSERT INTO market (date, data)
                VALUES (?, ?)
                ON CONFLICT(date) DO UPDATE SET data=excluded.data
            ''', (date, data_json)
        )
        connection.commit()

def reaad_market(date:str) -> dict | None:
    with sqlite3.connect(DATABASE) as connection:
        cursor = connection.cursor()
        cursor.execute(
            '''
                SELECT data FROM market WHERE date = ?
            ''', (date,)
        )
        row = cursor.fetchone()

        return json.loads(row[0]) if row else None