import pandas as pd
from loguru import logger

df = pd.read_parquet("./data/holdout.parquet")

user_id = df["user_id"].iloc[0]

logger.info(f"Random holdout user_id: <user_id>{user_id}</user_id>")