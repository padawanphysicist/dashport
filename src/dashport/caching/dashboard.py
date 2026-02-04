import logging
import requests
import json
import sys
from dashport.settings import settings

logger = logging.getLogger(__name__)
FORMAT = "%(name)-12s: %(levelname)-8s %(message)s"
logging.basicConfig(format=FORMAT, level=logging.INFO)

def fetch_dashboard(url, token, dashboard_id):
    """Obtém o payload de um dashboard do Metabase
    """
    endpoint = f"{url}/api/dashboard/{dashboard_id}"
    headers = {"X-API-KEY": token}
    try:
        response = requests.get(endpoint, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro de rede/API: {e}")
    except Exception as e:
        logger.error(f"Erro inesperado: {e}")

def find_collections(dashboard):
    """Obtém a lista de todas as collections na origem."""
    try:
        cards = dashboard.get("dashcards", [])
        questions = list(
            filter(lambda card: card["card_id"] is not None, cards)
        )
        collections = list(
            set(map(lambda q: q["card"]["collection_id"], questions))
        )
        logger.info(f"Collections utilizadas na origem: {collections}")
        return collections

        # Salva o payload com info das collections para manter um cache
        # collections = []
        # for collection_id in collections:
        #     response = requests.get(
        #         f"{url_orig}/api/collection/{collection_id}",
        #         headers={"X-API-KEY": token_orig},
        #         timeout=settings.REQUEST_TIMEOUT,
        #     )
        #     response.raise_for_status()
        #     collections.append(response.json())
        # json.dump(collections, sys.stdout, indent=4)
        # sys.stdout.flush()
    except BrokenPipeError:
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, sys.stdout.fileno())
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro de rede/API: {e}")
        return None
    except Exception as e:
        logger.error(f"Erro inesperado: {e}")
        return None

def find_questions(url, token, collection_id):
    """Lista questions em uma collection."""
    try:
        response = requests.get(
            f"{url}/api/collection/{collection_id}/items",
            headers={"X-API-KEY": token},
            timeout=settings.REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        data = response.json().get("data", [])
        question_list = sorted(
            [str(x["id"]) for x in data if x["model"] == "card"], reverse=True
        )
        return question_list
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro de rede/API: {e}")
        return None
    except Exception as e:
        logger.error(f"Erro inesperado: {e}")
        return None



    
################################################################################               

def list_collections(url, token, dashboard_id):
    """Obtém a lista de todas as collections na origem."""
    questions = []
    collections = []
    try:
        response = requests.get(
            f"{url_orig}/api/dashboard/{dashboard_id}",
            headers={"X-API-KEY": token},
            timeout=settings.REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        cards = response.json().get("dashcards", [])
        questions = list(
            filter(lambda card: card["card_id"] is not None, cards)
        )
        collections = list(
            set(map(lambda q: q["card"]["collection_id"], questions))
        )
        logger.info(f"Collections utilizadas na origem: {collections}")

        # Salva o payload com info das collections para manter um cache
        collections = []
        for collection_id in collections:
            response = requests.get(
                f"{url_orig}/api/collection/{collection_id}",
                headers={"X-API-KEY": token_orig},
                timeout=settings.REQUEST_TIMEOUT,
            )
            response.raise_for_status()
            collections.append(response.json())
        json.dump(collections, sys.stdout, indent=4)
        sys.stdout.flush()
    except BrokenPipeError:
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, sys.stdout.fileno())
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro de rede/API: {e}")
        return None
    except Exception as e:
        logger.error(f"Erro inesperado: {e}")
        return None


