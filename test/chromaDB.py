#!/usr/bin/env python3
"""
ChromaDB Admin Helper Script
Performs:
  1. List all collections
  2. Count items in a collection
  3. Peek into a collection

# List collections
./chroma_admin.py list

# Count records in a collection
./chroma_admin.py count my_collection

# Peek at first 5 records
./chroma_admin.py peek my_collection --limit 5
"""

import argparse
import chromadb

# Connect to a persistent Chroma instance
# Change the path to where your Chroma data is stored
client = chromadb.PersistentClient(path="/home/unimate/chroma_db")


def list_collections():
    """List all collections in the database."""
    collections = client.list_collections()
    print("Collections in ChromaDB:")
    for c in collections:
        print(f"- {c.name}")


def count_items(collection_name: str):
    """Count the number of items in a collection."""
    collection = client.get_collection(collection_name)
    print(f"Collection '{collection_name}' has {collection.count()} items.")


def peek_items(collection_name: str, limit: int):
    """Peek into a collection and show sample records."""
    collection = client.get_collection(collection_name)
    items = collection.peek(limit)
    print(f"Peeking into collection '{collection_name}' (showing {len(items['ids'])} items):")
    for i, _id in enumerate(items["ids"]):
        print(f"- ID: {_id}")
        print(f"  Metadata: {items['metadatas'][i]}")
        print(f"  Document: {items['documents'][i]}")
        print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ChromaDB Admin CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # list
    subparsers.add_parser("list", help="List all collections")

    # count
    count_parser = subparsers.add_parser("count", help="Count items in a collection")
    count_parser.add_argument("collection_name", help="Name of the collection")

    # peek
    peek_parser = subparsers.add_parser("peek", help="Peek into a collection")
    peek_parser.add_argument("collection_name", help="Name of the collection")
    peek_parser.add_argument("--limit", type=int, default=5, help="Number of items to show (default=5)")

    args = parser.parse_args()

    if args.command == "list":
        list_collections()
    elif args.command == "count":
        count_items(args.collection_name)
    elif args.command == "peek":
        peek_items(args.collection_name, args.limit)
