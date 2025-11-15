{{ config(materialized='table') }}

WITH raw AS (
    SELECT DISTINCT *
    FROM {{ source('amz_review_rating', 'amz_review_rating_raw') }}
)

SELECT DISTINCT
    timestamp,
    parent_asin,
    -- 365 days
    COUNT(*) OVER (
        PARTITION BY parent_asin
        ORDER BY timestamp
        RANGE BETWEEN INTERVAL '365 days' PRECEDING AND '1 seconds' PRECEDING
    ) AS parent_asin_rating_cnt_365d,
    AVG(rating) OVER (
        PARTITION BY parent_asin
        ORDER BY timestamp
        RANGE BETWEEN INTERVAL '365 days' PRECEDING AND '1 seconds' PRECEDING
    ) AS parent_asin_rating_avg_prev_rating_365d,

    -- 90 days
    COUNT(*) OVER (
        PARTITION BY parent_asin
        ORDER BY timestamp
        RANGE BETWEEN INTERVAL '90 days' PRECEDING AND '1 seconds' PRECEDING
    ) AS parent_asin_rating_cnt_90d,
    AVG(rating) OVER (
        PARTITION BY parent_asin
        ORDER BY timestamp
        RANGE BETWEEN INTERVAL '90 days' PRECEDING AND '1 seconds' PRECEDING
    ) AS parent_asin_rating_avg_prev_rating_90d,

    -- 30 days
    COUNT(*) OVER (
        PARTITION BY parent_asin
        ORDER BY timestamp
        RANGE BETWEEN INTERVAL '30 days' PRECEDING AND '1 seconds' PRECEDING
    ) AS parent_asin_rating_cnt_30d,
    AVG(rating) OVER (
        PARTITION BY parent_asin
        ORDER BY timestamp
        RANGE BETWEEN INTERVAL '30 days' PRECEDING AND '1 seconds' PRECEDING
    ) AS parent_asin_rating_avg_prev_rating_30d,

    -- 7 days
    COUNT(*) OVER (
        PARTITION BY parent_asin
        ORDER BY timestamp
        RANGE BETWEEN INTERVAL '7 days' PRECEDING AND '1 seconds' PRECEDING
    ) AS parent_asin_rating_cnt_7d,
    AVG(rating) OVER (
        PARTITION BY parent_asin
        ORDER BY timestamp
        RANGE BETWEEN INTERVAL '7 days' PRECEDING AND '1 seconds' PRECEDING
    ) AS parent_asin_rating_avg_prev_rating_7d
FROM
    raw