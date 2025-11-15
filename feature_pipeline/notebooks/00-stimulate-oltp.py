import os
import sys
import time

import papermill as pm
from loguru import logger

sys.path.insert(0, "../../")

run_timestamp = int(time.time())
output_dir = f"output/{run_timestamp}"
os.makedirs(output_dir, exist_ok=True)
logger.info(f"{run_timestamp=}")
logger.info(f"Notebook outputs will be saved to {output_dir}")

pm.execute_notebook(
    "001-simulate-oltp.ipynb", f"{output_dir}/001-simulate-oltp.ipynb"
)