import json
import os
import time
from datetime import datetime
from typing import List

import requests
from loguru import logger

FEAST_ONLINE_SERVER_HOST = os.getenv("FEAST_ONLINE_SERVER_HOST", "feature_online_server")
FEAST_ONLINE_SERVER_PORT = os.getenv("FEAST_ONLINE_SERVER_PORT", "6566")
API_HOST = os.getenv("API_HOST", "api")
API_PORT = os.getenv("API_PORT", "8000")

def get_recommendations(user_id, top_k_retrieval=100, count=10, debug=False):

    url = f"http://{API_HOST}:{API_PORT}/recs/u2i/rerank"

    try:
        result = requests.get(
            url=url,
            params= {
                "user_id" : user_id,
                "top_k_retrieval": top_k_retrieval,
                "count" : count,
                "debug": False
            },
            headers={
                "accept": "application/json",
            }
        )

        # Raise an exception for HTTP errors
        result.raise_for_status()
        return result.json()

    except Exception as e:
        print(f"An error occur {e}")
        return None

def get_user_item_sequence(user_id: str):

    try:
        response = requests.get(
            url=f"http://{API_HOST}:{API_PORT}/feast/fetch/item_sequence",
            headers={
                "accept": "application/json",
            },
            params = {
                "user_id": user_id
            },
        )
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"An error occured {e}")
        return None

def push_new_item_sequence(
    user_id: str, new_items: List[str], sequence_length: int = 10
):
    response = get_user_item_sequence(user_id)

    item_sequences = response["item_sequence"]
    new_item_sequences = item_sequences + new_items
    new_item_sequences = new_item_sequences[-sequence_length:]
    new_item_sequences_str = ",".join(new_item_sequences)

    item_sequence_tss = response["item_sequence_ts"]
    new_item_sequence_tss = item_sequence_tss + [int(time.time())]
    new_item_sequence_tss = new_item_sequence_tss[-sequence_length:]
    new_item_sequence_tss_str = ",".join([str(ts) for ts in new_item_sequence_tss])

    event_dict = {
        "user_id": [user_id],
        "timestamp": [str(datetime.now())],
        "dedup_rn": [
            1
        ],  # Mock to conform with current offline schema TODO: Remove this column in the future
        "user_rating_cnt_90d": [1],  # Mock
        "user_rating_avg_prev_rating_90d": [4.5],  # Mock
        "user_rating_list_10_recent_asin": [new_item_sequences_str],
        "user_rating_list_10_recent_asin_timestamp": [new_item_sequence_tss_str],
    }
    push_data = {
        "push_source_name": "user_rating_stats_push_source",
        "df": event_dict,
        "to": "online",  # For demo/learning - only need serving
    }
    logger.info(f"Event data to be pushed to feature store PUSH API {event_dict}")
    r = requests.post(
        f"http://{FEAST_ONLINE_SERVER_HOST}:{FEAST_ONLINE_SERVER_PORT}/push",
        data=json.dumps(push_data),
    )

    if r.status_code != 200:
        logger.error(f"Error: {r.status_code} {r.text}")