# Data Mining Results - Superstore

## Algorithm 1: Decision Tree Classification

Goal: predict whether an order line is profitable (`Profit > 0`) using sales, quantity, discount, category, sub-category, region, segment, and ship mode.

Results:

- Rows used: 9,994
- Target class balance: 80.6% profitable, 19.4% unprofitable
- Decision Tree accuracy: 0.9440
- Random Forest accuracy: 0.9428
- Decision Tree confusion matrix:

| Actual / Predicted | Loss | Profit |
| --- | ---: | ---: |
| Loss | 369 | 115 |
| Profit | 25 | 1990 |

Interpretation: The classification model predicts profitable order lines with high accuracy. The most important drivers are expected to include discount, sales value, quantity, and product/category-related fields. In business terms, this model helps identify order lines that are likely to lose money before they are fulfilled. High-discount transactions and specific product sub-categories should be reviewed carefully because discounting can reduce or eliminate profit.

Recommended action: use the model as a profitability warning signal. Orders predicted as unprofitable should trigger a review of discount level, product category, and shipping or pricing policy before approval.

Charts/tables:

- `DataMining/outputs/decision_tree.png`
- `DataMining/outputs/feature_importance.png`

## Algorithm 2: K-Means RFM Customer Segmentation

Goal: segment customers using RFM features:

- Recency: days since last order
- Frequency: number of distinct orders
- Monetary: total sales

Results:

| Cluster | Recency | Frequency | Monetary | Count | Suggested Segment |
| ---: | ---: | ---: | ---: | ---: | --- |
| 0 | 72.7 | 8.5 | 3,322.2 | 298 | Loyal regular customers |
| 1 | 101.2 | 4.7 | 1,669.7 | 335 | Mid-value occasional customers |
| 2 | 123.7 | 8.3 | 9,479.5 | 64 | VIP high-value customers |
| 3 | 559.5 | 3.7 | 1,470.2 | 96 | At-risk / inactive customers |

Interpretation: K-Means separates customers into four meaningful business groups. Cluster 2 contains the highest-value customers with very high monetary value and strong order frequency; this group should be prioritized for retention and premium offers. Cluster 0 contains loyal regular customers who buy frequently with moderate sales value. Cluster 1 is the largest group, with moderate recency and lower purchase frequency, making it suitable for cross-sell and reactivation campaigns. Cluster 3 is the most at-risk group because customers have not ordered recently and have relatively low monetary value.

Recommended action:

- VIP high-value customers: retention, loyalty rewards, and personalized offers.
- Loyal regular customers: cross-sell and bundle recommendations.
- Mid-value occasional customers: targeted promotions to increase frequency.
- At-risk customers: win-back campaigns with limited-time offers.

Charts/tables:

- `DataMining/outputs/elbow.png`
- `DataMining/outputs/segments.png`
- `DataMining/outputs/rfm_profile.csv`
- `DataMining/outputs/rfm_customers.csv`
