import argparse
import json
import os

from multi_rag.config import load_config

def cmd_query(args):
    """Run a query against the data sources defined in the config file."""
    query = input("Enter your query: \n")
    # Take this query and put it into the managerAgent, to
    # 1. Decide whether quantiative or qualitative, feed the prompt to the appropriate agent, and return the answer.
    # 2. Run a thought, action, observation loop, breaking down potentially into multiple sub-queries, each being routed
    # then returning all of the outputted results (for transparency) and the final answer.
    print("Query ran: \n" + query)


def cmd_list_sources(args):
    """List the data sources defined in the config file, tables in the SQLite dbs. Provides the option to view table schemas
    and lists of documents in the doc directories."""
    config = load_config()
    config.print_summary()


def cmd_add_source(args):
    """Add a new data source to the config file."""
    config = load_config()
    source_type = input("Enter the type of data source (sql/doc): ").lower()
    if source_type == "sql":
        path = input("Enter the path to the SQLite database: ")
        name = input("Enter a name for this data source: ")
        config.add_sql_db(path, name)
    elif source_type == "doc":
        path = input("Enter the path to the document directory: ")
        name = input("Enter a name for this data source: ")
        config.add_doc_dir(path, name)
    else:
        print(f"Unknown data source type: {source_type}")
        return 1

    config.save_config()

    print(f"Added new {source_type} data source: {name} -> {path}")
    return 0


def build_parser():
    parser = argparse.ArgumentParser(prog="multi_rag", description="Ask queries about Delight using both quantitative and qualitative data sources.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    query_parser = subparsers.add_parser("query", help="Run a query against the data sources")
    query_parser.set_defaults(func=cmd_query)

    list_parser = subparsers.add_parser("list-sources", help="List configured data sources")
    list_parser.set_defaults(func=cmd_list_sources)

    add_source_parser = subparsers.add_parser("add-source", help="Add a new data source to the config file.")
    add_source_parser.set_defaults(func=cmd_add_source)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    exit_code = args.func(args)
    raise SystemExit(exit_code)