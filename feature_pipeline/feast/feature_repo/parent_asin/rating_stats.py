from datetime import timedelta

from feast import (
    Entity,
    FeatureService,
    FeatureView,
    Field,
    PushSource,
)

from feast.infra.offline_stores.contrib.postgres_offline_store.postgres_source import (
    PostgreSQLSource,
)

from feast.types import Float32, Int64

# Define an entity for the driver. You can think of an entity as a primary key used to
# fetch features.
parent_asin = Entity(name="parent_asin", join_keys=["parent_asin"])

# Read data from parquet files. Parquet is convenient for local development mode. For
# production, you can use your favorite DWH, such as BigQuery. See Feast documentation
# for more info.
parent_asin_rating_stats_source = PostgreSQLSource(
    name="parent_asin_rating_stats_source",
    query="SELECT * FROM feature_store_offline.parent_asin_rating_stats",
    timestamp_field="timestamp",
)

schema = [
    Field(name="parent_asin_rating_cnt_365d", dtype=Int64),
    Field(name="parent_asin_rating_avg_prev_rating_365d", dtype=Float32),
    Field(name="parent_asin_rating_cnt_90d", dtype=Int64),
    Field(name="parent_asin_rating_avg_prev_rating_90d", dtype=Float32),
    Field(name="parent_asin_rating_cnt_30d", dtype=Int64),
    Field(name="parent_asin_rating_avg_prev_rating_30d", dtype=Float32),
    Field(name="parent_asin_rating_cnt_7d", dtype=Int64),
    Field(name="parent_asin_rating_avg_prev_rating_7d", dtype=Float32),
]

# Define the new Feature View for parent_asin rating stats
parent_asin_rating_stats_fv = FeatureView(
    name="parent_asin_rating_stats",
    entities=[parent_asin],
    ttl=timedelta(
        days=10000
    ),  # Define this to be very long for demo purpose otherwise null data
    schema=schema,
    online=True,
    source=parent_asin_rating_stats_source,
    tags={"domain": "parent_asin_rating"},
)

# This groups features into a model version
driver_activity_v1 = FeatureService(
    name="parent_asin_rating_v1",
    features=[
        parent_asin_rating_stats_fv
    ],
)

# Defines a way to push data (to be available offline, online or both) into Feast.
parent_asin_rating_stats_push_source = PushSource(
    name="parent_asin_rating_stats_push_source",
    batch_source=parent_asin_rating_stats_source,
)

# Defines a slightly modified version of the feature view from above, where the source
# has been changed to the push source. This allows fresh features to be directly pushed
# to the online store for this feature view.
parent_asin_rating_stats_fresh_fv = FeatureView(
    name="parent_asin_rating_stats_fresh",
    entities=[parent_asin],
    ttl=timedelta(days=1),
    schema=schema,
    online=True,
    source=parent_asin_rating_stats_push_source,  # Changed from above
    tags={"domain": "parent_asin_rating"},
)

# Fresh source
parent_asin_activity_v1_fresh = FeatureService(
    name="parent_asin_rating_v1_fresh",
    features=[
        parent_asin_rating_stats_fresh_fv,
    ],
)
