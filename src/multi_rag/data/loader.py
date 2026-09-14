import chromadb
import os
import hashlib
import sqlite3

BLOCKED_KEYWORDS = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE"]


def validate_sql(query: str) -> dict:
    query_upper = query.upper().strip()
    for keyword in BLOCKED_KEYWORDS:
        if f" {keyword} " in f" {query_upper} " or query_upper.startswith(keyword):
            return {"valid": False, "reason": f"Blocked: {keyword} not permitted"}
    if not query_upper.startswith("SELECT"):
        return {"valid": False, "reason": "Only SELECT queries are permitted"}
    return {"valid": True, "reason": "OK"}


class DocRagDataLoader:
    def __init__(self, config):
        self.config = config
        self.doc_dirs = config.doc_dirs
        self.chroma_client = chromadb.Client()
        self.collection = self.chroma_client.get_or_create_collection(
            name="enterprise_documents"
        )

    def load_doc_data(self):
        """Load data from the document directories specified in the config."""
        documents = []
        ids = []
        metadatas = []

        for doc_dir in self.doc_dirs:
            path = doc_dir["path"]
            #print(f"Document Directory: {path}")
            #print("Documents:")
            for filename in os.listdir(path):
                file_path = os.path.join(path, filename)
                if not os.path.isfile(file_path):
                    continue

                #print(f"- {filename}")
                with open(file_path, "r", encoding="utf-8") as file:
                    documents.append(file.read())

                ids.append(hashlib.sha256(file_path.encode()).hexdigest())
                metadatas.append({"source": file_path, "filename": filename})

        if documents:
            self.collection.upsert(
                ids=ids,
                documents=documents,
                metadatas=metadatas,
            )

        return self.collection

    def query_documents(self, query, n_results=1):
        """Return the documents most similar to a natural-language query."""
        result = self.collection.query(
            query_texts=[query],
            n_results=n_results,
        )

        return [
            {"document": document, "metadata": metadata, "distance": distance}
            for document, metadata, distance in zip(
                result["documents"][0],
                result["metadatas"][0],
                result["distances"][0],
            )
        ]

class SQLDataLoader:
    def __init__(self, config):
        self.config = config
        self.sql_dbs = config.sql_dbs
        if not self.sql_dbs:
            raise ValueError("No SQL databases are configured.")

        self.connections = {
            database["name"]: sqlite3.connect(database["path"])
            for database in self.sql_dbs
        }

    def _get_connection(self, database_name=None):
        """Return the connection for a configured database."""
        if database_name is None:
            database_name = self.sql_dbs[0]["name"]

        try:
            return self.connections[database_name]
        except KeyError as error:
            raise ValueError(
                f"Unknown database '{database_name}'. "
                f"Available databases: {', '.join(self.connections)}"
            ) from error

    def list_tables(self, database_name=None):
        """Return the tables available in a configured SQLite database."""
        connection = self._get_connection(database_name)
        rows = connection.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
            """
        ).fetchall()
        return [row[0] for row in rows]

    def get_table_schema(self, table_name, database_name=None):
        """Return a readable schema description for a configured table."""
        connection = self._get_connection(database_name)
        tables = self.list_tables(database_name)
        if table_name not in tables:
            raise ValueError(
                f"Unknown table '{table_name}'. "
                f"Available tables: {', '.join(tables)}"
            )

        escaped_table_name = table_name.replace('"', '""')
        columns = connection.execute(
            f'PRAGMA table_info("{escaped_table_name}")'
        ).fetchall()

        lines = [f"Table: {table_name}", "Columns:"]
        for _, name, data_type, not_null, default_value, primary_key in columns:
            constraints = []
            if primary_key:
                constraints.append("PRIMARY KEY")
            if not_null:
                constraints.append("NOT NULL")
            if default_value is not None:
                constraints.append(f"DEFAULT {default_value}")

            column = f"- {name} ({data_type or 'ANY'})"
            if constraints:
                column += f" [{', '.join(constraints)}]"
            lines.append(column)

        return "\n".join(lines)

    def execute_sql(self, query, database_name=None):
        """Execute a validated read-only SQL query and return its results."""
        validation = validate_sql(query)
        if not validation["valid"]:
            return validation

        connection = self._get_connection(database_name)
        try:
            cursor = connection.execute(query)
            columns = [description[0] for description in cursor.description]
            rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        except sqlite3.Error as error:
            return {
                "valid": True,
                "reason": "SQL error",
                "error": str(error),
                "columns": [],
                "rows": [],
            }

        return {
            "valid": True,
            "reason": "OK",
            "columns": columns,
            "rows": rows,
        }

    def close(self):
        """Close all open database connections."""
        for connection in self.connections.values():
            connection.close()

    def load_sql_data(self):
        """Load data from the SQL databases specified in the config."""
        for sql_db in self.sql_dbs:
            database_name = sql_db["name"]
            print(f"SQL Database: {sql_db['path']}")
            print("Tables:")
            for table in self.list_tables(database_name):
                print(f"- {table}")