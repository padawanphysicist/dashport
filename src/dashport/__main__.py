"""Ferramenta para migração de dashboards do Metabase.

Usage:
    dashport -h
    dashport cache --dashboard-id=<id>
    dashport mapping --dashboard-json=<filepath>
    dashport build --cache-dir=/tmp/dashport
    dashport inject --dashboard-json=<filepath>

Options:
    -h --help                    Exibe esta tela.
    --dashboard-id=<id>          ID do dashboard
    --dashboard-json=<filepath>  Arquivo JSON com payload do dashboard

Examples:
    ############
    # 1. Cache #
    ############
    dashport cache --dashboard-id=1 --cache-dir=/tmp/dashport # Faz um cache do que é necessário
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

        ############################################
        # Construção do payload final para o cache #
        ############################################
        payload = {
            "dashboard": dashboard,
            "collections": collections,
            "questions": questions,
        }
        try:
            json.dump(payload, sys.stdout, indent=4)
            sys.stdout.flush()
        except BrokenPipeError:
            devnull = os.open(os.devnull, os.O_WRONLY)
            os.dup2(devnull, sys.stdout.fileno())
            sys.exit(1)


if __name__ == "__main__":
    main()
