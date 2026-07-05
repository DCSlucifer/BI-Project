# Data Mining Results - Superstore

This document summarizes the most recent results produced by `DataMining/data_mining.py`. The script generates the analytical tables and visual outputs in `DataMining/outputs/`.

## Overview

The data mining component was conducted on the Superstore dataset with 9,994 order-line records. Its purpose is to complement the OLAP and dashboard analysis with predictive and behavioral insights.

Two algorithms were used:

1. **Decision Tree Classification**: a supervised model for predicting whether an order line is profitable and for extracting interpretable business rules.
2. **K-Means RFM Segmentation**: an unsupervised model for segmenting 793 customers based on recency, frequency, and monetary value.

---

## Algorithm 1: Decision Tree Classification

### Objective

The objective of the classification model is to predict whether an order line is profitable or loss-making:

```text
Profitable = 1 if Profit > 0
Loss       = 0 if Profit <= 0
```

The model uses the following predictors:

- Numeric variables: `Sales`, `Quantity`, and `Discount`.
- One-hot encoded categorical variables: `Category`, `Sub-Category`, `Region`, `Segment`, and `Ship Mode`.

### Model Performance

| Metric | Value |
| --- | ---: |
| Rows used | 9,994 |
| Class distribution | 80.6% Profit / 19.4% Loss |
| Baseline accuracy | 0.8063 |
| Decision Tree test accuracy | 0.9440 |
| Decision Tree macro F1-score | 0.9033 |
| 5-fold cross-validation accuracy | 0.9444 +/- 0.0020 |
| Cross-validation loss precision | 0.9370 |
| Cross-validation loss recall | 0.7645 |
| Random Forest benchmark accuracy | 0.9428 |

Confusion matrix on the test set:

| Actual / Predicted | Predicted Loss | Predicted Profit |
| --- | ---: | ---: |
| Actual Loss | 369 | 115 |
| Actual Profit | 25 | 1,990 |

The Decision Tree substantially outperforms the baseline accuracy of 0.8063. The model identifies profitable transactions with strong reliability, while the loss class remains more difficult because the target distribution is imbalanced. The loss recall of approximately 76% should be reported transparently, as it indicates that some loss-making records are still classified as profitable.

### Business Meaning of the Classification Output

The class distribution is important for interpretation. Since 80.6% of the order lines are profitable, a naive model that predicts every record as profitable would already achieve 80.63% accuracy. Therefore, the Decision Tree result should not be evaluated by accuracy alone. The improvement to 94.40% test accuracy, together with a macro F1-score of 90.33%, indicates that the model captures patterns beyond the majority-class tendency.

The confusion matrix also provides a practical interpretation. The model correctly identifies 369 loss-making order lines and 1,990 profitable order lines in the test set. However, it misses 115 loss-making order lines. From a business perspective, this means the model is useful as a warning system, but it should not be used as the only approval rule for discount decisions. It is more suitable as a decision-support layer that highlights suspicious transactions for review.

The 25 false positive cases, where profitable orders are predicted as loss-making, are less damaging operationally than missed loss cases. A false positive may trigger additional review, while a false negative may allow an unprofitable transaction to proceed. Therefore, the business value of the model is primarily in early risk detection rather than full automation.

### Validated Business Rule

The model is not evaluated only through aggregate accuracy. The script also extracts decision rules and validates them against the held-out test set.

| Rule | Predicted class | Test support | Correct | Incorrect | Precision |
| --- | --- | ---: | ---: | ---: | ---: |
| `Discount > 0.25 AND Category != Technology` | Loss | 318 | 316 | 2 | 99.37% |

This is the strongest validated business rule:

> When the discount exceeds 25% and the product category is not Technology, the order line is highly likely to be loss-making. The rule covers 318 records in the test set and achieves 99.37% precision.

Recommended managerial interpretation:

- Orders with `Discount > 25%` should be flagged for profitability review.
- High-discount transactions outside the Technology category require additional scrutiny before approval.
- The Decision Tree should be interpreted as an explainable rule-discovery model, while the Random Forest benchmark is used as a robustness comparison.

### Operational Use of the Loss Rule

The rule `Discount > 0.25 AND Category != Technology` is actionable because it can be implemented as a simple business rule in a sales approval workflow. For example, when a sales representative applies a discount greater than 25% to Furniture or Office Supplies, the system can require manager approval or display a profitability warning before the order is finalized.

This rule also supports discount policy design. The result suggests that high discounts are not uniformly harmful across all product categories; the risk is especially strong outside Technology. Therefore, the business should not adopt a single discount threshold for all products. Instead, it should define category-aware discount policies and monitor margin impact by product group.

The rule has high precision but partial coverage. It is very reliable when the condition is met, but it does not explain every loss-making order. Other loss causes may include low-margin sub-categories, small order values, or operational costs not represented directly in the dataset. Thus, the rule is best interpreted as a high-confidence loss-risk signal rather than a complete profitability model.

### Output Files

| File | Description |
| --- | --- |
| `DataMining/outputs/class_balance.png` | Target-class distribution between Profit and Loss |
| `DataMining/outputs/confusion_matrix.png` | Confusion matrix with counts and normalized proportions |
| `DataMining/outputs/decision_tree.png` | Interpretable decision tree visualization |
| `DataMining/outputs/feature_importance.png` | Top feature-importance values from the Random Forest benchmark |
| `DataMining/outputs/loss_rules.png` | Validated loss-risk rules |
| `DataMining/outputs/decision_rules.csv` | Complete set of extracted leaf rules |
| `DataMining/outputs/loss_rules.csv` | Filtered loss rules with support and precision |

---

## Algorithm 2: K-Means RFM Customer Segmentation

### Objective

The objective of the segmentation model is to group customers according to RFM behavior:

- **Recency**: the number of days since the customer's most recent purchase.
- **Frequency**: the number of distinct orders placed by the customer.
- **Monetary**: the total sales value generated by the customer.

Because K-Means uses Euclidean distance, the RFM variables were standardized with `StandardScaler`. The number of clusters was kept at `k = 4` and was supported by the Elbow Method and Silhouette analysis.

### Segmentation Results

| Cluster | Segment label | Recency | Frequency | Monetary | Count |
| ---: | --- | ---: | ---: | ---: | ---: |
| 0 | Trung thanh / Active | 72.7 | 8.5 | 3,322.2 | 298 |
| 1 | Pho thong / Trung binh | 101.2 | 4.7 | 1,669.7 | 335 |
| 2 | VIP / Champions | 123.7 | 8.3 | 9,479.5 | 64 |
| 3 | Roi bo / Lost | 559.5 | 3.7 | 1,470.2 | 96 |

The Silhouette score for `k = 4` is **0.3554**.

The original segment labels and colors are retained for consistency with the previous project notes:

- Cluster 0: `Trung thanh / Active`
- Cluster 1: `Pho thong / Trung binh`
- Cluster 2: `VIP / Champions`
- Cluster 3: `Roi bo / Lost`

### Business Meaning of the RFM Output

The RFM segmentation separates customers by value and engagement level. The segmentation is meaningful because each cluster suggests a different managerial action rather than simply describing statistical groups.

`VIP / Champions` has the highest monetary value, with an average Monetary value of 9,479.5. Although this segment contains only 64 customers, it represents the most valuable group and should be protected from churn. These customers are suitable for premium retention programs, early access campaigns, and personalized product recommendations.

`Trung thanh / Active` has the lowest Recency value and the highest Frequency value. This indicates that these customers purchase recently and repeatedly. They are not as high-value as the VIP group, but they are strongly engaged. The main business opportunity is to increase their basket value through cross-selling and category expansion.

`Pho thong / Trung binh` is the largest group with 335 customers. This segment has moderate recency, lower frequency, and lower monetary value. Because it is large, even a small improvement in purchase frequency can generate meaningful revenue growth. This segment is suitable for targeted promotions, bundle offers, and category-specific campaigns.

`Roi bo / Lost` has a very high Recency value of 559.5 days, which indicates long inactivity. This segment should not receive expensive retention campaigns by default. A selective win-back strategy is more appropriate: low-cost email campaigns, limited-time offers, or reactivation tests. If response rates are low, the business should avoid excessive spending on this group.

### Business Interpretation

- **Cluster 2 - VIP / Champions**: This group has the highest monetary value and a high purchase frequency. It should be prioritized for retention, loyalty incentives, and premium offers.
- **Cluster 0 - Trung thanh / Active**: This group purchases recently and frequently, with moderate-to-high monetary value. It is suitable for cross-selling and progression toward VIP status.
- **Cluster 1 - Pho thong / Trung binh**: This is the largest and most average segment, with moderate recency and lower spending. Targeted promotions may increase purchase frequency.
- **Cluster 3 - Roi bo / Lost**: This group has very high recency, indicating long inactivity. Win-back campaigns should be used selectively and with controlled promotional cost.

### Recommended Business Actions by Segment

| Segment | Main interpretation | Recommended action | Business objective |
| --- | --- | --- | --- |
| `VIP / Champions` | Highest monetary value and strong purchase frequency | Loyalty program, premium support, personalized recommendations | Protect high-value revenue |
| `Trung thanh / Active` | Recent and frequent buyers with moderate-to-high value | Cross-sell, upsell, category expansion | Increase average customer value |
| `Pho thong / Trung binh` | Largest average-value group | Targeted promotions and bundles | Increase purchase frequency at scale |
| `Roi bo / Lost` | Long inactive customers | Low-cost win-back campaigns | Test reactivation without overspending |

### Limitations of the Segmentation Output

The Silhouette score of 0.3554 indicates moderate cluster separation rather than perfectly distinct groups. This is expected in customer behavior data because purchasing patterns often overlap. Therefore, the clusters should be used as decision-support segments, not as absolute labels.

The Monetary variable is based on Sales rather than Profit. This follows the conventional RFM definition and measures revenue contribution. However, a profit-based segmentation could be added in future work if the business objective shifts from revenue growth to margin optimization.

### Output Files

| File | Description |
| --- | --- |
| `DataMining/outputs/elbow_silhouette.png` | Combined Elbow and Silhouette evidence for selecting `k` |
| `DataMining/outputs/elbow.png` | Elbow chart retained for compatibility with earlier report versions |
| `DataMining/outputs/rfm_profile.png` | Heatmap of cluster-level RFM profiles |
| `DataMining/outputs/segments.png` | Frequency-versus-Monetary scatter plot with segment labels |
| `DataMining/outputs/rfm_profile.csv` | Cluster profile table |
| `DataMining/outputs/rfm_customers.csv` | Customer-level cluster assignments |
| `DataMining/outputs/model_summary.txt` | Summary of model metrics and outputs |

---

## Suggested Academic Presentation Statement

The Decision Tree model is used not only for classification but also for interpretable rule extraction. The strongest validated rule is `Discount > 0.25 AND Category != Technology`, which predicts a loss-making order line with 99.37% precision on the test set. For customer segmentation, K-Means is applied to standardized RFM variables, resulting in four stable groups: `Trung thanh / Active`, `Pho thong / Trung binh`, `VIP / Champions`, and `Roi bo / Lost`. The `VIP / Champions` segment has the highest monetary value, whereas the `Roi bo / Lost` segment has the highest recency and therefore requires selective win-back actions.
