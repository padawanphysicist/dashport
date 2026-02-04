"""Ferramenta para migração de dashboards do Metabase.

Usage:
    dashport -h
    dashport cache --dashboard-id=<id>
    dashport mapping --cache-file=<f1>
    dashport build --cache-file=<f1> --mapping-file=<f2>
    dashport inject --payload-file=<f1> --dashboard-id=<id> [-X]

Options:
    -h --help                    Exibe esta tela.
    --dashboard-id=<id>          ID do dashboard
    --cache-file=<f1>            Arquivo de cache.
    --mapping-file=<f2>          Arquivo contendo os mapeamentos necessários
    --payload-file=<p1>          Arquivo contendo o payload para revisão
    -X --execute                 Efetiva as operações na instância alvo

Examples:
    ############
    # 1. Cache #
    ############
    dashport cache --dashboard-id=1 # Faz um cache do que é necessário
                                    # para a migração do dashboard com ID=1
    ##############
    # 2. Mapping #
    ##############
    dashport mapping --cache-dir=/tmp/dashport # Atualiza o cache com os arquivos de mapeamento de:
                                               # 
    # 3. Building
    dashport build --cache-dir=/tmp/dashport 

    # 4. Upload
    dashpoirt 
  
"""
from docopt import docopt
from dashport.caching.dashboard import fetch_dashboard, find_collections, find_questions
from dashport.mapping.map_resources import map_resources
from dashport.migrating.build_payload import build_target_payload
from dashport.migrating.inject import inject_dashboard
from dashport.settings import settings
import sys
import json
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(format=settings.FORMAT, level=logging.INFO)

def flatten_deep(nested_list):
    flat = []
    for item in nested_list:
        if isinstance(item, list):
            flat.extend(flatten_deep(item))
        else:
            flat.append(item)
    return flat

def extract_resource_ids(dashboard):
    """Extract unique database, table, and field IDs from dashboard."""
    database_ids = set()
    table_ids = set()
    field_ids = set()

    dashcards = dashboard.get('dashcards', [])
    for dashcard in dashcards:
        card = dashcard.get('card', {})

        # Extract database_id
        if card.get('database_id'):
            database_ids.add(card['database_id'])

        # Extract table_id
        if card.get('table_id'):
            table_ids.add(card['table_id'])

        # Extract field IDs from result_metadata
        result_metadata = card.get('result_metadata', [])
        for metadata in result_metadata:
            if metadata.get('id'):
                field_ids.add(metadata['id'])

    return sorted(list(database_ids)), sorted(list(table_ids)), sorted(list(field_ids))

def main():
    args = docopt(__doc__, version='0.1')

    ####################
    # Etapa 1: Caching #
    ####################
    if args["cache"] is True:
        url = settings.METABASE_URL_SOURCE
        token = settings.METABASE_TOKEN_SOURCE
        dashboard_id = args["--dashboard-id"]

        ####################################################
        # Obtém as informações necessárias para a migração #
        ####################################################
        dashboard = fetch_dashboard(url, token, dashboard_id)
        collections = find_collections(dashboard)
        questions = sorted(list(map(int, flatten_deep([find_questions(url, token, c) for c in collections]))))

        ########################################
        # Extrai IDs de recursos do dashboard #
        ########################################
        databases, tables, fields = extract_resource_ids(dashboard)

        ############################################
        # Construção do payload final para o cache #
        ############################################
        payload = {
            "dashboard": dashboard,
            "collections": collections,
            "questions": questions,
            "databases": databases,
            "tables": tables,
            "fields": fields,
        }
        try:
            json.dump(payload, sys.stdout, indent=4)
            sys.stdout.flush()
        except BrokenPipeError:
            devnull = os.open(os.devnull, os.O_WRONLY)
            os.dup2(devnull, sys.stdout.fileno())
            sys.exit(1)

    ####################
    # Etapa 2: Mapping #
    ####################
    if args["mapping"] is True:
        url = settings.METABASE_URL_TARGET
        token = settings.METABASE_TOKEN_TARGET
        cache_file = args["--cache-file"]
        logger.info(f"Arquivo de cache: {cache_file}")
        logger.warning(f"Pulando etapa")
        map_resources(url, token, cache_file)

    if args["build"] is True:
        logger.info("Construindo o payload para a instância alvo")
        cache_file = args["--cache-file"]
        mapping_file = args["--mapping-file"]
        dashboard = build_target_payload(cache_file, mapping_file)

        ############################################
        # Construção do payload final para o cache #
        ############################################
        payload = {
            "cache_file": cache_file,
            "mapping_file": mapping_file,
            "dashboard": dashboard,
        }
        try:
            json.dump(payload, sys.stdout, indent=4)
            sys.stdout.flush()
        except BrokenPipeError:
            devnull = os.open(os.devnull, os.O_WRONLY)
            os.dup2(devnull, sys.stdout.fileno())
            sys.exit(1)

    if args["inject"] is True:
        url = settings.METABASE_URL_TARGET
        token = settings.METABASE_TOKEN_TARGET
        dry_run = not args["--execute"]
        dashboard_id = args["--dashboard-id"]
        payload_file = args["--payload-file"]
    
        logger.info("Injetando dash no MB target")
        logger.info(f"*** DRY-RUN: {dry_run}")
        logger.info(f"Payload: {payload_file}")

        # TODO: corrigir no futuro (MUITO) próximo
        with open(payload_file, "r", encoding='utf-8') as file:
            dashboard = json.load(file)
        logger.info(dashboard)
        
        inject_dashboard(dashboard, url, token, dashboard_id, dry_run)

if __name__ == "__main__":
    main()
