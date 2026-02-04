def build_target_payload(cache_file, mapping_file):
    pass

# def generate_payloads(cache_dir: Path, collection_id: Optional[str] = None):
#     """
#     Generate JSON payloads for cards and dashboard.

#     Phase 2: GENERATE_PAYLOADS
#     - Reads dependencies.json (with dest_id mappings)
#     - Reads all card_*.json files
#     - Orders cards by dependency (base cards first)
#     - Generates cleaned payloads with ID replacements
#     - Saves to payloads/ directory
#     """
#     log("=" * 80)
#     log("PHASE 2: GENERATE PAYLOADS")
#     log("=" * 80)

#     # Load dependencies
#     deps_file = cache_dir / "dependencies.json"
#     dependencies = load_json(deps_file)

#     # Build ID mapping
#     id_mapping = {}

#     # Add database mappings
#     for src_id, db_info in dependencies['databases'].items():
#         if db_info.get('dest_id'):
#             id_mapping[f"database_{src_id}"] = db_info['dest_id']

#     # Add table mappings
#     for src_id, table_info in dependencies['tables'].items():
#         if table_info.get('dest_id'):
#             id_mapping[f"table_{src_id}"] = table_info['dest_id']

#     # Add field mappings (if available)
#     for src_id, field_info in dependencies['fields'].items():
#         if field_info.get('dest_id'):
#             id_mapping[f"field_{src_id}"] = field_info['dest_id']

#     log(f"\nID Mapping built: {len(id_mapping)} mappings")

#     # Separate base cards from derived cards
#     base_cards = []
#     derived_cards = []

#     for card_id, card_info in dependencies['cards'].items():
#         if card_info.get('is_base_card'):
#             base_cards.append(card_id)
#         else:
#             derived_cards.append(card_id)

#     log(f"\nFound {len(base_cards)} base cards and {len(derived_cards)} derived cards")

#     # Process in order: base cards first, then derived
#     upload_order = base_cards + derived_cards

#     # Create payloads directory
#     payloads_dir = cache_dir / "payloads"
#     payloads_dir.mkdir(exist_ok=True)

#     log(f"\n--- Generating Card Payloads ---")

#     for card_id in upload_order:
#         card_file = cache_dir / f"card_{card_id}.json"

#         if not card_file.exists():
#             log(f"⚠ Warning: {card_file} not found, skipping")
#             continue

#         log(f"\nProcessing card {card_id}...")
#         card = load_json(card_file)

#         # Clean payload
#         payload = clean_card_payload(card)

#         # Replace IDs in dataset_query
#         if 'dataset_query' in payload:
#             log(f"  Replacing IDs in dataset_query...")
#             payload['dataset_query'] = replace_ids_in_query(
#                 payload['dataset_query'],
#                 id_mapping
#             )

#         # Set collection_id if provided
#         if collection_id and collection_id != 'None':
#             payload['collection_id'] = int(collection_id)
#             log(f"  Set collection_id: {collection_id}")

#         # Save payload
#         payload_file = payloads_dir / f"card_{card_id}_payload.json"
#         save_json(payload_file, payload)

#     # Generate upload order file
#     upload_order_data = {
#         "order": upload_order,
#         "base_cards": base_cards,
#         "derived_cards": derived_cards
#     }
#     save_json(payloads_dir / "upload_order.json", upload_order_data)

#     # Generate dashboard payload
#     log(f"\n--- Generating Dashboard Payload ---")
#     dashboard_file = cache_dir / "dashboard.json"

#     if dashboard_file.exists():
#         dashboard = load_json(dashboard_file)

#         # Clean dashboard payload
#         dashboard_payload = {
#             'name': dashboard.get('name', 'Migrated Dashboard'),
#             'description': dashboard.get('description'),
#             'parameters': dashboard.get('parameters', []),
#         }

#         if collection_id and collection_id != 'None':
#             dashboard_payload['collection_id'] = int(collection_id)

#         # Store dashcards separately (will be added after dashboard creation)
#         dashcards_payload = dashboard.get('dashcards', [])

#         # Clean dashcards (remove IDs, will be mapped during upload)
#         cleaned_dashcards = []
#         for dashcard in dashcards_payload:
#             cleaned = {
#                 'card_id': dashcard.get('card_id'),  # Will be replaced during upload
#                 'size_x': dashcard.get('size_x'),
#                 'size_y': dashcard.get('size_y'),
#                 'col': dashcard.get('col'),
#                 'row': dashcard.get('row'),
#                 'parameter_mappings': dashcard.get('parameter_mappings', []),
#                 'visualization_settings': dashcard.get('visualization_settings', {})
#             }
#             cleaned_dashcards.append(cleaned)

#         save_json(payloads_dir / "dashboard_payload.json", dashboard_payload)
#         save_json(payloads_dir / "dashcards_payload.json", cleaned_dashcards)
#     else:
#         log(f"⚠ Warning: {dashboard_file} not found")

#     log("\n" + "=" * 80)
#     log("✓ Payload generation complete!")
#     log(f"Payloads saved to: {payloads_dir}")
#     log("\nNext steps:")
#     log("1. Review payloads in cache/ldf/payloads/")
#     log("2. Run upload script to create resources in destination")
#     log("=" * 80)



