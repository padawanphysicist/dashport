# TODO: Decidir como será o formato aqui para ler na proxima etapa
def map_resources(url, token, dashboard):
    print(url, token, dashboard)
# def map_resources(cache_dir: Path, dest_url: str, dest_token: str) -> Dict[str, Any]:
#     """
#     Map source resources to destination resources.

#     Phase 1: MAPPING
#     - Reads dependencies.json
#     - Fetches databases, tables, fields from destination
#     - Matches by name
#     - Updates dependencies.json with dest_id
#     """
#     log("=" * 80)
#     log("PHASE 1: MAPPING RESOURCES")
#     log("=" * 80)

#     # Load dependencies
#     deps_file = cache_dir / "dependencies.json"
#     if not deps_file.exists():
#         log(f"ERROR: {deps_file} not found!")
#         sys.exit(1)

#     dependencies = load_json(deps_file)
#     log(f"Loaded dependencies from {deps_file}")

#     # Fetch destination resources
#     log(f"\nFetching resources from {dest_url}...")

#     # Map databases
#     log("\n--- Mapping Databases ---")
#     dest_databases = fetch_databases(dest_url, dest_token)

#     not_found = []
#     low_confidence_matches = []

#     for db_id, db_info in dependencies['databases'].items():
#         db_name = db_info['name']

#         # Try to load detailed database info from cache
#         db_file = cache_dir / f"database_{db_id}.json"
#         if db_file.exists():
#             src_db = load_json(db_file)
#             log(f"\nMatching database {db_id} ('{db_name}')...")

#             # Use smart matching
#             dest_id, confidence, criteria = match_database_smart(
#                 src_db,
#                 dest_databases,
#                 dest_url,
#                 dest_token
#             )

#             if dest_id:
#                 db_info['dest_id'] = dest_id

#                 # Log based on confidence level
#                 if confidence == "exact":
#                     log(f"✓ Database '{db_name}': {db_id} → {dest_id} [EXACT MATCH]")
#                     log(f"  Matched by: {criteria}")
#                 elif confidence == "high":
#                     log(f"✓ Database '{db_name}': {db_id} → {dest_id} [HIGH CONFIDENCE]")
#                     log(f"  Matched by: {criteria}")
#                 elif confidence == "low":
#                     log(f"⚠ Database '{db_name}': {db_id} → {dest_id} [LOW CONFIDENCE - PLEASE REVIEW]")
#                     log(f"  Matched by: {criteria}")
#                     low_confidence_matches.append(f"database: {db_name} (matched by {criteria})")
#             else:
#                 log(f"✗ Database '{db_name}': NOT FOUND in destination")
#                 not_found.append(f"database: {db_name}")
#         else:
#             # Fallback to simple name matching if database file doesn't exist
#             log(f"\n⚠ Warning: {db_file} not found, using simple name matching")
#             db_name_to_id = {db['name']: db['id'] for db in dest_databases}

#             if db_name in db_name_to_id:
#                 db_info['dest_id'] = db_name_to_id[db_name]
#                 log(f"✓ Database '{db_name}': {db_id} → {db_info['dest_id']} [NAME MATCH]")
#             else:
#                 log(f"✗ Database '{db_name}' NOT FOUND in destination")
#                 not_found.append(f"database: {db_name}")

#     # Map tables
#     log("\n--- Mapping Tables ---")

#     # Build list of mapped destination database IDs
#     mapped_db_ids = [info['dest_id'] for info in dependencies['databases'].values() if info.get('dest_id')]

#     # Fetch tables (optimized to only fetch from mapped databases)
#     all_dest_tables = []

#     if mapped_db_ids:
#         # OPTIMIZATION: Fetch tables only from mapped databases
#         log(f"Fetching tables from {len(mapped_db_ids)} mapped databases (optimization enabled)...")
#         for dest_db_id in mapped_db_ids:
#             try:
#                 tables = fetch_tables(dest_url, dest_token, dest_db_id)
#                 all_dest_tables.extend(tables)
#                 log(f"  Fetched {len(tables)} tables from database {dest_db_id}")
#             except Exception as e:
#                 log(f"  Warning: Could not fetch tables from database {dest_db_id}: {e}")
#         log(f"✓ Found {len(all_dest_tables)} tables total in mapped databases")
#     else:
#         # FALLBACK: No mapped databases, fetch from all (for edge cases or old cache format)
#         dest_db_list = fetch_databases(dest_url, dest_token)
#         log(f"No mapped databases. Fetching tables from all {len(dest_db_list)} databases (fallback mode)...")
#         for dest_db in dest_db_list:
#             try:
#                 tables = fetch_tables(dest_url, dest_token, dest_db['id'])
#                 all_dest_tables.extend(tables)
#             except Exception as e:
#                 log(f"  Warning: Could not fetch tables from database {dest_db['id']} ({dest_db.get('name', 'Unknown')}): {e}")
#         log(f"Found {len(all_dest_tables)} tables across {len(dest_db_list)} databases")

#     medium_confidence_matches = []

#     for table_id, table_info in dependencies['tables'].items():
#         table_name = table_info['name']

#         # Try to load detailed table info from cache
#         table_file = cache_dir / f"table_{table_id}.json"
#         if table_file.exists():
#             src_table = load_json(table_file)
#             log(f"\nMatching table {table_id} ('{table_name}')...")

#             # Get the mapped database ID if the table's database was mapped
#             src_db_id = str(src_table.get('db_id'))
#             mapped_db_id = None
#             if src_db_id in dependencies['databases']:
#                 mapped_db_id = dependencies['databases'][src_db_id].get('dest_id')

#             # Use smart matching
#             dest_id, confidence, criteria = match_table_smart(
#                 src_table,
#                 all_dest_tables,
#                 mapped_db_id
#             )

#             if dest_id:
#                 table_info['dest_id'] = dest_id

#                 # Log based on confidence level
#                 if confidence == "exact":
#                     log(f"✓ Table '{table_name}': {table_id} → {dest_id} [EXACT MATCH]")
#                     log(f"  Matched by: {criteria}")
#                 elif confidence == "high":
#                     log(f"✓ Table '{table_name}': {table_id} → {dest_id} [HIGH CONFIDENCE]")
#                     log(f"  Matched by: {criteria}")
#                 elif confidence == "medium":
#                     log(f"⚠ Table '{table_name}': {table_id} → {dest_id} [MEDIUM CONFIDENCE - PLEASE REVIEW]")
#                     log(f"  Matched by: {criteria}")
#                     medium_confidence_matches.append(f"table: {table_name} (matched by {criteria})")
#                 elif confidence == "low":
#                     log(f"⚠ Table '{table_name}': {table_id} → {dest_id} [LOW CONFIDENCE - PLEASE REVIEW]")
#                     log(f"  Matched by: {criteria}")
#                     low_confidence_matches.append(f"table: {table_name} (matched by {criteria})")
#             else:
#                 log(f"✗ Table '{table_name}': NOT FOUND in destination")
#                 not_found.append(f"table: {table_name}")
#         else:
#             # Fallback to simple name matching if table file doesn't exist
#             log(f"\n⚠ Warning: {table_file} not found, using simple name matching")

#             matched = False
#             for table in all_dest_tables:
#                 if table.get('name') == table_name or table.get('display_name') == table_name:
#                     table_info['dest_id'] = table['id']
#                     log(f"✓ Table '{table_name}': {table_id} → {table_info['dest_id']} [NAME MATCH]")
#                     matched = True
#                     break

#             if not matched:
#                 log(f"✗ Table '{table_name}' NOT FOUND in destination")
#                 not_found.append(f"table: {table_name}")

#     # Map fields
#     log("\n--- Mapping Fields ---")
#     field_mappings = {}
#     for table_id, table_info in dependencies['tables'].items():
#         if table_info.get('dest_id'):
#             dest_table_id = table_info['dest_id']
#             try:
#                 fields = fetch_table_fields(dest_url, dest_token, dest_table_id)
#                 for field in fields:
#                     field_mappings[f"{dest_table_id}:{field['name']}"] = field
#             except Exception as e:
#                 log(f"Warning: Could not fetch fields for table {dest_table_id}: {e}")

#     for field_id, field_info in dependencies['fields'].items():
#         field_name = field_info['name']
#         # Fields are harder to map without table context - we'll skip for now
#         # They can be mapped during payload generation if needed
#         log(f"⊙ Field '{field_name}': {field_id} (will map during generation)")

#     # Map collections first
#     log("\n--- Mapping Collections ---")
#     src_collections = dependencies.get('collections', {})

#     if src_collections:
#         log(f"Found {len(src_collections)} source collections used by dashboard")
#     else:
#         log("No collection information in dependencies.json (older cache format)")

#     # Fetch all destination collections
#     log("Fetching collections from destination...")
#     headers = get_metabase_headers(dest_token)
#     try:
#         collections_response = requests.get(
#             f"{dest_url}/api/collection",
#             headers=headers,
#             timeout=REQUEST_TIMEOUT
#         )
#         collections_response.raise_for_status()
#         dest_collections = collections_response.json()
#         log(f"Found {len(dest_collections)} destination collections\n")
#     except Exception as e:
#         log(f"Error: Could not fetch destination collections: {e}")
#         dest_collections = []

#     # Map source collections to destination collections
#     mapped_collections = []
#     for src_coll_id, src_coll_info in src_collections.items():
#         src_coll_name = src_coll_info.get('name', '')
#         log(f"Matching collection {src_coll_id} ('{src_coll_name}')...")

#         dest_coll_id = match_collection_simple(int(src_coll_id), src_coll_name, dest_collections)

#         if dest_coll_id:
#             dependencies['collections'][src_coll_id]['dest_id'] = dest_coll_id
#             mapped_collections.append(dest_coll_id)
#             log(f"✓ Collection '{src_coll_name}': {src_coll_id} → {dest_coll_id}")
#         else:
#             log(f"⚠ Collection '{src_coll_name}': {src_coll_id} NOT FOUND")

#     # Map cards
#     log("\n--- Mapping Cards ---")

#     # Determine which collections to search
#     if mapped_collections:
#         # Filter dest_collections to only the mapped ones
#         relevant_dest_collections = [c for c in dest_collections if c['id'] in mapped_collections]
#         log(f"Fetching cards from {len(relevant_dest_collections)} relevant collections (optimization enabled)...")
#         all_dest_cards = fetch_all_cards_from_collections(dest_url, dest_token, relevant_dest_collections)
#         log(f"\n✓ Found {len(all_dest_cards)} cards in relevant collections")
#     else:
#         # Fallback: fetch from all collections
#         log(f"No collection mapping available. Fetching cards from all {len(dest_collections)} collections (fallback mode)...")
#         all_dest_cards = fetch_all_cards_from_collections(dest_url, dest_token, dest_collections)
#         log(f"\n✓ Found {len(all_dest_cards)} cards total")

#     card_medium_confidence = []
#     card_low_confidence = []

#     # Only map base cards (cards that are directly used in the dashboard)
#     # Derived cards that are created within the dashboard don't need mapping
#     for card_id, card_info in dependencies['cards'].items():
#         # Skip if this is not a base card (base cards exist independently)
#         if not card_info.get('is_base_card'):
#             continue

#         card_name = card_info['name']

#         # Try to load detailed card info from cache
#         card_file = cache_dir / f"card_{card_id}.json"
#         if card_file.exists():
#             src_card = load_json(card_file)
#             log(f"\nMatching card {card_id} ('{card_name}')...")

#             # Get the mapped collection ID if the card's collection was mapped
#             src_collection_id = src_card.get('collection_id')
#             mapped_collection_id = None
#             # Note: We don't have collection mapping in dependencies.json yet
#             # For now, we'll just search across all collections

#             # Use smart matching
#             dest_id, confidence, criteria = match_card_smart(
#                 src_card,
#                 all_dest_cards,
#                 mapped_collection_id
#             )

#             if dest_id:
#                 card_info['dest_id'] = dest_id

#                 # Log based on confidence level
#                 if confidence == "exact":
#                     log(f"✓ Card '{card_name}': {card_id} → {dest_id} [EXACT MATCH]")
#                     log(f"  Matched by: {criteria}")
#                 elif confidence == "high":
#                     log(f"✓ Card '{card_name}': {card_id} → {dest_id} [HIGH CONFIDENCE]")
#                     log(f"  Matched by: {criteria}")
#                 elif confidence == "medium":
#                     log(f"⚠ Card '{card_name}': {card_id} → {dest_id} [MEDIUM CONFIDENCE - PLEASE REVIEW]")
#                     log(f"  Matched by: {criteria}")
#                     card_medium_confidence.append(f"card: {card_name} (matched by {criteria})")
#                 elif confidence == "low":
#                     log(f"⚠ Card '{card_name}': {card_id} → {dest_id} [LOW CONFIDENCE - PLEASE REVIEW]")
#                     log(f"  Matched by: {criteria}")
#                     card_low_confidence.append(f"card: {card_name} (matched by {criteria})")
#             else:
#                 log(f"✗ Card '{card_name}': NOT FOUND in destination")
#                 not_found.append(f"card: {card_name}")
#         else:
#             log(f"\n⊙ Card {card_id} ('{card_name}'): No cache file, skipping mapping")

#     # Add card confidence matches to the general lists
#     medium_confidence_matches.extend(card_medium_confidence)
#     low_confidence_matches.extend(card_low_confidence)

#     # Save updated dependencies
#     save_json(deps_file, dependencies)

#     # Generate report
#     report_file = cache_dir / "mapping_report.txt"
#     with open(report_file, 'w', encoding='utf-8') as f:
#         f.write("MAPPING REPORT\n")
#         f.write("=" * 80 + "\n\n")

#         f.write(f"Total Databases: {len(dependencies['databases'])}\n")
#         f.write(f"Total Tables: {len(dependencies['tables'])}\n")
#         f.write(f"Total Fields: {len(dependencies['fields'])}\n")
#         f.write(f"Total Collections: {len(dependencies.get('collections', {}))}\n")
#         f.write(f"Total Cards: {len(dependencies['cards'])}\n\n")

#         # Collections mapping info
#         if dependencies.get('collections'):
#             collections_mapped = sum(1 for c in dependencies['collections'].values() if c.get('dest_id'))
#             collections_not_mapped = len(dependencies['collections']) - collections_mapped
#             f.write(f"Collections Mapped: {collections_mapped}/{len(dependencies['collections'])}\n")
#             if collections_not_mapped > 0:
#                 f.write(f"Collections Not Mapped: {collections_not_mapped}\n")
#             f.write("\n")

#         # Section: Medium confidence matches
#         if medium_confidence_matches:
#             f.write("MEDIUM CONFIDENCE MATCHES (RECOMMENDED TO REVIEW):\n")
#             f.write("-" * 80 + "\n")
#             f.write("These resources were matched with medium confidence.\n")
#             f.write("They are likely correct, but please verify.\n\n")
#             for item in medium_confidence_matches:
#                 f.write(f"  ⚠ {item}\n")
#             f.write("\n")

#         # Section: Low confidence matches
#         if low_confidence_matches:
#             f.write("LOW CONFIDENCE MATCHES (MUST REVIEW):\n")
#             f.write("-" * 80 + "\n")
#             f.write("These resources were matched but with low confidence.\n")
#             f.write("Please verify that the mappings are correct.\n\n")
#             for item in low_confidence_matches:
#                 f.write(f"  ⚠ {item}\n")
#             f.write("\n")

#         # Section: Not found
#         if not_found:
#             f.write("RESOURCES NOT FOUND IN DESTINATION:\n")
#             f.write("-" * 80 + "\n")
#             for item in not_found:
#                 f.write(f"  ✗ {item}\n")
#             f.write("\n")

#         # Summary
#         if not not_found and not low_confidence_matches and not medium_confidence_matches:
#             f.write("✓ All resources mapped successfully with high confidence!\n")
#         elif not_found or low_confidence_matches or medium_confidence_matches:
#             f.write("NEXT STEPS:\n")
#             f.write("-" * 80 + "\n")
#             if medium_confidence_matches or low_confidence_matches:
#                 f.write("1. Review medium/low confidence matches in dependencies.json\n")
#                 f.write("2. Update dest_id manually if incorrect\n")
#             if not_found:
#                 f.write("3. For resources not found, manually add dest_id in dependencies.json\n")
#                 f.write("4. Re-run 'generate' command after fixing mappings\n")

#     log(f"\nMapping report saved to: {report_file}")

#     if not_found:
#         log(f"\n⚠ WARNING: {len(not_found)} resources not found in destination")
#         log("Please review mapping_report.txt and update dependencies.json manually")

#     if medium_confidence_matches:
#         log(f"\n⚠ INFO: {len(medium_confidence_matches)} medium confidence matches")
#         log("Recommended to review mapping_report.txt to verify these mappings")

#     if low_confidence_matches:
#         log(f"\n⚠ WARNING: {len(low_confidence_matches)} low confidence matches")
#         log("Please review mapping_report.txt to verify these mappings are correct")

#     if not not_found and not low_confidence_matches and not medium_confidence_matches:
#         log("\n✓ All resources mapped successfully with high confidence!")

#     return dependencies

