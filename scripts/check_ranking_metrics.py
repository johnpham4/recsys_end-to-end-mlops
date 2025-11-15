import pandas as pd
import evidently.metrics

# Check available ranking metrics
print("Available metrics containing 'NDCG', 'Recall', 'Precision', 'Personalization':")
all_metrics = [x for x in dir(evidently.metrics) if not x.startswith('_') and x[0].isupper()]
for metric in sorted(all_metrics):
    if any(keyword in metric for keyword in ['NDCG', 'Recall', 'Precision', 'Personalization', 'FBeta', 'Ranking', 'Rec']):
        print(f"  - {metric}")

print("\n\nAll available metrics:")
for metric in sorted(all_metrics):
    print(f"  - {metric}")
