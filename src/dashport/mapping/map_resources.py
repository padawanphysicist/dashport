import requests
import json
import logging
from dashport.settings import settings

logger = logging.getLogger(__name__)
logging.basicConfig(format=settings.FORMAT, level=logging.INFO)

def load_json(file_path):
    """Load JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def fetch_databases(url, token):
    """Fetch all databases from Metabase."""
    headers = {"X-API-KEY": token}
    response = requests.get(
        f"{url}/api/database",
        headers=headers,
        timeout=settings.REQUEST_TIMEOUT
    )
    response.raise_for_status()
    return response.json().get('data', [])

def fetch_database_metadata(url, token, database_id):
    """Fetch metadata for a specific database including tables."""
    headers = {"X-API-KEY": token}
    response = requests.get(
        f"{url}/api/database/{database_id}/metadata",
        headers=headers,
        timeout=settings.REQUEST_TIMEOUT
    )
    response.raise_for_status()
    return response.json()

def fetch_table_metadata(url, token, table_id):
    """Fetch metadata for a specific table including fields."""
    headers = {"X-API-KEY": token}
    response = requests.get(
        f"{url}/api/table/{table_id}/query_metadata",
        headers=headers,
        timeout=settings.REQUEST_TIMEOUT
    )
    response.raise_for_status()
    return response.json()


def map_resources(url, token, cache_file):
    """
    Map source resources to destination resources.

    Phase 1: MAPPING
    - Reads cache file with resource IDs
    - Fetches databases, tables, fields from destination
    - Matches by name
    - Outputs mapping to stdout
    """
    logger.info("=" * 80)
    logger.info("PHASE 1: MAPPING RESOURCES")
    logger.info("=" * 80)

    # Load cache
    cache = load_json(cache_file)
    logger.info(f"Loaded cache from {cache_file}")

    # Initialize mapping structure
    mapping = {
        "databases": {},
        "tables": {},
        "fields": {}
    }

    # Fetch destination resources
    logger.info(f"\nFetching resources from {url}...")

    # Map databases
    logger.info("\n--- Mapping Databases ---")
    dest_databases = fetch_databases(url, token)
    dest_db_by_name = {db['name']: db for db in dest_databases}

    # Get source database info from cache
    src_dashboard = cache['dashboard']
    src_db_ids = cache.get('databases', [])

    for src_db_id in src_db_ids:
        # Find database name in source dashboard
        src_db_name = None
        for dashcard in src_dashboard.get('dashcards', []):
            card = dashcard.get('card', {})
            if card.get('database_id') == src_db_id:
                # Fetch source database metadata to get name
                # For now, we'll try to match by ID in dest
                src_db_name = f"Database {src_db_id}"  # Placeholder
                break

        # Try to match by name
        dest_db = None
        if src_db_name and src_db_name in dest_db_by_name:
            dest_db = dest_db_by_name[src_db_name]

        # If we have destination databases, try first match as fallback
        if not dest_db and dest_databases:
            dest_db = dest_databases[0]
            logger.warning(f"Could not find exact match for database {src_db_id}, using first available: {dest_db['name']}")

        if dest_db:
            mapping['databases'][src_db_id] = {
                "src_id": src_db_id,
                "dest_id": dest_db['id'],
                "name": dest_db['name']
            }
            logger.info(f"✓ Database {src_db_id} → {dest_db['id']} ({dest_db['name']})")
        else:
            logger.error(f"✗ Database {src_db_id} NOT FOUND in destination")

    # Map tables
    logger.info("\n--- Mapping Tables ---")
    src_table_ids = cache.get('tables', [])

    # Fetch all tables from mapped destination databases
    all_dest_tables = []
    for db_id, db_info in mapping['databases'].items():
        dest_db_id = db_info['dest_id']
        try:
            logger.info(f"Fetching tables from database {dest_db_id}...")
            db_metadata = fetch_database_metadata(url, token, dest_db_id)
            tables = db_metadata.get('tables', [])
            all_dest_tables.extend(tables)
            logger.info(f"  Found {len(tables)} tables")
        except Exception as e:
            logger.error(f"  Error fetching tables: {e}")

    # Create table lookup by name
    dest_tables_by_name = {table['name']: table for table in all_dest_tables}

    # Map each source table
    for src_table_id in src_table_ids:
        # Find table name from source dashboard
        src_table_name = None
        for dashcard in src_dashboard.get('dashcards', []):
            card = dashcard.get('card', {})
            if card.get('table_id') == src_table_id:
                # Get table name from result_metadata or query
                result_metadata = card.get('result_metadata', [])
                if result_metadata:
                    # Table name might be in display_name
                    src_table_name = f"Table {src_table_id}"  # Placeholder
                break

        # Try to match by name
        dest_table = dest_tables_by_name.get(src_table_name) if src_table_name else None

        # Fallback: try to find by ID if table lists have same structure
        if not dest_table and all_dest_tables:
            # Try to find table at same position
            for table in all_dest_tables:
                if table.get('id') == src_table_id:
                    dest_table = table
                    break

        if dest_table:
            mapping['tables'][src_table_id] = {
                "src_id": src_table_id,
                "dest_id": dest_table['id'],
                "name": dest_table['name']
            }
            logger.info(f"✓ Table {src_table_id} → {dest_table['id']} ({dest_table['name']})")
        else:
            logger.warning(f"⚠ Table {src_table_id} not found in destination")

    # Map fields
    logger.info("\n--- Mapping Fields ---")
    src_field_ids = cache.get('fields', [])

    # Fetch all fields from mapped destination tables
    all_dest_fields = []
    for table_id, table_info in mapping['tables'].items():
        dest_table_id = table_info['dest_id']
        try:
            table_metadata = fetch_table_metadata(url, token, dest_table_id)
            fields = table_metadata.get('fields', [])
            all_dest_fields.extend(fields)
        except Exception as e:
            logger.warning(f"  Error fetching fields for table {dest_table_id}: {e}")

    # Create field lookup by name
    dest_fields_by_name = {field['name']: field for field in all_dest_fields}

    # Map each source field
    for src_field_id in src_field_ids:
        # Find field name from source dashboard
        src_field_name = None
        for dashcard in src_dashboard.get('dashcards', []):
            card = dashcard.get('card', {})
            result_metadata = card.get('result_metadata', [])
            for metadata in result_metadata:
                if metadata.get('id') == src_field_id:
                    src_field_name = metadata.get('name')
                    break
            if src_field_name:
                break

        # Try to match by name
        dest_field = dest_fields_by_name.get(src_field_name) if src_field_name else None

        # Fallback: try to find by ID
        if not dest_field:
            for field in all_dest_fields:
                if field.get('id') == src_field_id:
                    dest_field = field
                    break

        if dest_field:
            mapping['fields'][src_field_id] = {
                "src_id": src_field_id,
                "dest_id": dest_field['id'],
                "name": dest_field['name']
            }
            logger.info(f"✓ Field {src_field_id} → {dest_field['id']} ({dest_field['name']})")
        else:
            logger.warning(f"⚠ Field {src_field_id} not found in destination")

    # Output mapping to stdout
    logger.info("\n" + "=" * 80)
    logger.info("MAPPING COMPLETE")
    logger.info("=" * 80)
    
    import sys
    json.dump(mapping, sys.stdout, indent=4)
    sys.stdout.flush()
