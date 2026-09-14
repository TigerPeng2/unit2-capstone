from ast import Add
import sqlite3
import json
import os


CONFIG_PATH = "config/config.json"

class Config():
    def __init__(self, input_json):
        self.sql_dbs = input_json.get("data_sources", {}).get("sql", [])
        self.doc_dirs = input_json.get("data_sources", {}).get("doc", [])

    def add_sql_db(self, path, name):
        """Add a new SQLite database to the config file, and write the names of the tables"""
        if not os.path.exists(path):
            raise ValueError(f"SQLite database file does not exist: {path}")

        if any(db["path"] == path for db in self.sql_dbs):
            raise ValueError(f"SQLite database already exists in config: {path}")

        conn = sqlite3.connect(path)
        cursor = conn.cursor()

        # Get the list of tables in the database
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        # Add the path of the database to the config, along with the list of names of tables.
        self.sql_dbs.append({
            "name": name,
            "path": path,
            "tables": [table[0] for table in tables]
        })

        conn.close()

    def add_doc_dir(self, path, name):
        """Add a new document directory to the config file, and write the names of the documents in the directory."""
        if not os.path.exists(path):
            raise ValueError(f"Document directory does not exist: {path}")
        if any(doc_dir["path"] == path for doc_dir in self.doc_dirs):
            raise ValueError(f"Document directory already exists in config: {path}")

        # Get the list of documents in the directory
        documents = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]

        # Add to config
        self.doc_dirs.append({
            "name": name,
            "path": path,
            "documents": documents
        })

    def save_config(self):
        """Save the current config to the config file."""
        with open(CONFIG_PATH, "w") as f:
            json.dump({
                "data_sources": {
                    "sql": self.sql_dbs,
                    "doc": self.doc_dirs
                }
            }, f, indent=2)

    def print_summary(self):
        """Print a summary of the data sources in the config file."""
        print("SQL Databases:")
        for db in self.sql_dbs:
            print(f"- {db['name']} -> {db['path']}")
            print(f"  Tables: {', '.join(db['tables'])}")

        print("\nDocument Directories:")
        for doc_dir in self.doc_dirs:
            print(f"- {doc_dir['name']} -> {doc_dir['path']}")
            print(f"  Documents: {', '.join(doc_dir['documents'])}")

def load_config():
    ## Load the config file and return a Config object
    # If the config folder / file don't exist yet, create an empty config
    if not os.path.exists(CONFIG_PATH):
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        with open(CONFIG_PATH, "w") as f:
            json.dump({"data_sources": {"sql": [], "doc": []}}, f, indent=2)

    with open(CONFIG_PATH, "r") as f:
        config_json = json.load(f)
        return Config(config_json)