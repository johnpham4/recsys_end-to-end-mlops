from airflow.models import DagBag

db = DagBag()
print(f"Found {len(db.dags)} DAGs")
for dag_id in db.dags.keys():
    print(f"  - {dag_id}")
if db.import_errors:
    print("\nImport errors:")
    for file, error in db.import_errors.items():
        print(f"  {file}: {error}")
