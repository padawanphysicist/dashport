import requests
import logging
from dashport.settings import settings

logger = logging.getLogger(__name__)
logging.basicConfig(format=settings.FORMAT, level=logging.INFO)

def inject_dashboard(dashboard, url, token, dashboard_id, dry_run):
    if dry_run:
        logger.info("DRY RUN")

    ####################################################
    # 1. Obtém todos os cartões do dashboard de origem #
    ####################################################
    cards = dashboard.get("dashcards", [])
    #logger.info(f"cards {cards}")

#     #################################################
#     # 2. Lê os mapeamentos de IDs (origem, destino) #
#     #################################################
#     logger.info(
#         f"Obtendo IDs de questions a serem processadas do arquivo {csv_file}..."
#     )
#     question_id_dict = dict()
#     try:
#         with open(csv_file, "r") as f:
#             reader = csv.reader(f)
#             for row in reader:
#                 if len(row) >= 2 and row[0].strip() and row[1].strip():
#                     orig_card_id, dest_card_id = list(
#                         map(lambda x: int(x.strip()), row)
#                     )
#                     question_id_dict[orig_card_id] = dest_card_id
#         logger.info(
#             f"Foram identificadas {len(question_id_dict.keys())} questions a serem processadas"
#         )
#     except Exception as e:
#         logger.error(f"Erro ao obter o mapeamento de questions de {csv_file}: {e}")

    ################################################################
    # 3. Valida se todas as questions do dashboard estão mapeadas #
    ################################################################
    logger.info("Validando mapeamento de questions...")
    missing_questions = []
    for card_orig in cards:
        if card_orig["card_id"] is not None:
            if card_orig["card_id"] not in question_id_dict:
                missing_questions.append(card_orig["card_id"])

    if missing_questions:
        logger.error(
            f"ERRO: {len(missing_questions)} question(s) do dashboard não estão mapeadas no CSV:"
        )
        for qid in missing_questions:
            logger.error(f"  - Question ID: {qid}")
        logger.error(f"\nPara corrigir, adicione as seguintes linhas ao arquivo {csv_file}:")
        for qid in missing_questions:
            logger.error(f"  {qid},<dest_question_id>")
        logger.error(f"\nOu use o comando 'map_question' para encontrar o mapeamento automaticamente:")
        for qid in missing_questions:
            logger.error(
                f"  dashport map_question --url-orig=<orig> --url-dest=<dest> "
                f"--token-orig=<tok_orig> --token-dest=<tok_dest> --question-id={qid}"
            )

        if not skip_unmapped:
            logger.error("\nAbortando migração. Use --skip-unmapped para pular questions não mapeadas.")
            return
        else:
            logger.warning(
                f"\nContinuando com --skip-unmapped: {len(missing_questions)} question(s) serão puladas."
            )
    else:
        logger.info("✓ Todas as questions do dashboard estão mapeadas no CSV")



    ##################################################
    # 6. Sobe o payload para a instância de destino #
    ##################################################
    try:
        if not dry_run:
            logger.info(
                f"Atualizando dashboard {url}/dashboard/{dashboard_id}..."
            )
            response = requests.put(
                f"{url}/api/dashboard/{dashboard_id}",
                headers={"Content-Type": "application/json", "X-API-KEY": token},
                # json={
                #     "dashcards": cards_dest,
                #     "tabs": dashboard_tabs_orig,
                # },
                json=dashboard,
                timeout=settings.REQUEST_TIMEOUT,
            )
            response.raise_for_status()
            logger.info(f"Atualizado: {url}/dashboard/{dashboard_id}")
    except Exception as e:
        logger.error(
            f"Erro ao subir payload para {url}/dashboard/{dashboard_id}: {e}"
        )


# def migrate_dashboard(
#     url_orig,
#     token_orig,
#     dashboard_id_orig,
#     url_dest,
#     token_dest,
#     dashboard_id_dest,
#     csv_file,
#     execution_flag,
#     skip_unmapped=False,
# ):
#     """Migra um dashboard entre instâncias."""
#     ####################################################
#     # 1. Obtém todos os cartões do dashboard de origem #
#     ####################################################
#     logger.info(
#         f"Obtendo lista de cartões de ${url_orig}/dashboard/{dashboard_id_orig}..."
#     )
#     try:
#         response = requests.get(
#             f"{url_orig}/api/dashboard/{dashboard_id_orig}",
#             headers={"X-API-KEY": token_orig},
#             timeout=REQUEST_TIMEOUT,
#         )
#         response.raise_for_status()
#         cards_orig = response.json().get("dashcards", [])
#         logger.info(f"O dashboard contém {len(cards_orig)} cartões")
#     except Exception as e:
#         logger.error(
#             f"Erro ao obter a lista de cartões de ${url_orig}/dashboard/{dashboard_id_orig}: {e}"
#         )

#     #################################################
#     # 2. Lê os mapeamentos de IDs (origem, destino) #
#     #################################################
#     logger.info(
#         f"Obtendo IDs de questions a serem processadas do arquivo {csv_file}..."
#     )
#     question_id_dict = dict()
#     try:
#         with open(csv_file, "r") as f:
#             reader = csv.reader(f)
#             for row in reader:
#                 if len(row) >= 2 and row[0].strip() and row[1].strip():
#                     orig_card_id, dest_card_id = list(
#                         map(lambda x: int(x.strip()), row)
#                     )
#                     question_id_dict[orig_card_id] = dest_card_id
#         logger.info(
#             f"Foram identificadas {len(question_id_dict.keys())} questions a serem processadas"
#         )
#     except Exception as e:
#         logger.error(f"Erro ao obter o mapeamento de questions de {csv_file}: {e}")

#     ################################################################
#     # 3. Valida se todas as questions do dashboard estão mapeadas #
#     ################################################################
#     logger.info("Validando mapeamento de questions...")
#     missing_questions = []
#     for card_orig in cards_orig:
#         if card_orig["card_id"] is not None:
#             if card_orig["card_id"] not in question_id_dict:
#                 missing_questions.append(card_orig["card_id"])

#     if missing_questions:
#         logger.error(
#             f"ERRO: {len(missing_questions)} question(s) do dashboard não estão mapeadas no CSV:"
#         )
#         for qid in missing_questions:
#             logger.error(f"  - Question ID: {qid}")
#         logger.error(f"\nPara corrigir, adicione as seguintes linhas ao arquivo {csv_file}:")
#         for qid in missing_questions:
#             logger.error(f"  {qid},<dest_question_id>")
#         logger.error(f"\nOu use o comando 'map_question' para encontrar o mapeamento automaticamente:")
#         for qid in missing_questions:
#             logger.error(
#                 f"  dashport map_question --url-orig=<orig> --url-dest=<dest> "
#                 f"--token-orig=<tok_orig> --token-dest=<tok_dest> --question-id={qid}"
#             )

#         if not skip_unmapped:
#             logger.error("\nAbortando migração. Use --skip-unmapped para pular questions não mapeadas.")
#             return
#         else:
#             logger.warning(
#                 f"\nContinuando com --skip-unmapped: {len(missing_questions)} question(s) serão puladas."
#             )
#     else:
#         logger.info("✓ Todas as questions do dashboard estão mapeadas no CSV")

#     ###########################################
#     # 4. Obtém as abas do Dashboard na origem #
#     ###########################################
#     dashboard_tabs_orig = []
#     try:
#         response = requests.get(
#             f"{url_orig}/api/dashboard/{dashboard_id_orig}",
#             headers={"X-API-KEY": token_orig},
#             timeout=REQUEST_TIMEOUT,
#         )
#         response.raise_for_status()
#         payload = response.json()
#         dashboard_tabs_orig = [
#             {"id": tab["id"], "name": tab["name"]} for tab in payload["tabs"]
#         ]
#     except Exception as e:
#         logger.error(
#             f"Erro ao obter as abas do dashboard {url_orig}/dashboard/{dashboard_id_orig}: {e}"
#         )

#     ######################################################
#     # 5. Cria o payload para atualizar o dash no destino #
#     ######################################################
#     cards_dest = []
#     skipped_count = 0

#     for card_orig in cards_orig:
#         try:
#             logger.info(
#                 f"Processando {'cartão' if card_orig['card_id'] is None else 'question'}: id={card_orig['id']}, card_id={card_orig['card_id']}"
#             )

#             # Tenta obter o ID de destino, tratando KeyError especificamente
#             question_id_dest = None
#             if card_orig["card_id"] is not None:
#                 try:
#                     question_id_dest = question_id_dict[card_orig["card_id"]]
#                 except KeyError:
#                     if skip_unmapped:
#                         logger.warning(
#                             f"Pulando question {card_orig['card_id']}: não mapeada no CSV {csv_file}"
#                         )
#                         skipped_count += 1
#                         continue
#                     else:
#                         logger.error(
#                             f"Question {card_orig['card_id']} não encontrada no mapeamento CSV."
#                         )
#                         logger.error(f"Adicione a linha '{card_orig['card_id']},<dest_id>' ao arquivo {csv_file}")
#                         logger.error(f"Ou use --skip-unmapped para pular questions não mapeadas.")
#                         raise ValueError(
#                             f"Question {card_orig['card_id']} não mapeada. Veja logs para mais detalhes."
#                         )

#             # Question no destino
#             card_dest = dict()
#             if card_orig["card_id"] is not None:
#                 response = requests.get(
#                     f"{url_dest}/api/card/{question_id_dest}",
#                     headers={"X-API-KEY": token_dest},
#                     timeout=REQUEST_TIMEOUT,
#                 )
#                 response.raise_for_status()
#                 payload = response.json()
#                 card_dest = payload

#             # Tratamento de cartões virtuais
#             visualization_settings = dict()
#             if card_orig["card_id"] is None:
#                 visualization_settings = card_orig["visualization_settings"]

#             cards_dest.append(
#                 {
#                     "dashboard_id": int(dashboard_id_dest),
#                     "dashboard_tab_id": card_orig["dashboard_tab_id"],
#                     "id": card_orig["id"],
#                     "card_id": question_id_dest,
#                     "entity_id": card_orig["entity_id"],
#                     "size_x": card_orig["size_x"],
#                     "size_y": card_orig["size_y"],
#                     "col": card_orig["col"],
#                     "row": card_orig["row"],
#                     "card": card_dest,
#                     "visualization_settings": visualization_settings,
#                 }
#             )
#         except ValueError:
#             # Re-raise ValueError (from KeyError handling above)
#             raise
#         except requests.exceptions.RequestException as e:
#             logger.error(
#                 f"Erro de rede/API ao processar card {card_orig['id']}: {e}"
#             )
#             if not skip_unmapped:
#                 raise
#         except Exception as e:
#             logger.error(
#                 f"Erro inesperado ao processar card {card_orig['id']}: {type(e).__name__}: {e}"
#             )
#             raise

#     if skipped_count > 0:
#         logger.warning(f"Total de questions puladas: {skipped_count}")

#     ##################################################
#     # 6. Sobe o payload para a instância de destino #
#     ##################################################
#     try:
#         if execution_flag:
#             logger.info(
#                 f"Atualizando dashboard {url_dest}/dashboard/{dashboard_id_dest}..."
#             )
#             response = requests.put(
#                 f"{url_dest}/api/dashboard/{dashboard_id_dest}",
#                 headers={"Content-Type": "application/json", "X-API-KEY": token_dest},
#                 json={
#                     "dashcards": cards_dest,
#                     "tabs": dashboard_tabs_orig,
#                 },
#                 timeout=REQUEST_TIMEOUT,
#             )
#             response.raise_for_status()
#             logger.info(f"Atualizado: {url_dest}/dashboard/{dashboard_id_dest}")
#     except Exception as e:
#         logger.error(
#             f"Erro ao subir payload para {url_dest}/dashboard/{dashboard_id_dest}: {e}"
#         )

