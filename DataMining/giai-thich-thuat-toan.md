# Data Mining Algorithm Explanation - Superstore

This document explains the two data mining algorithms used in the Superstore BI final project. It is written as an academic defense note: the emphasis is not only on what the models produced, but also on why the methods are appropriate, how they were validated, and how the results should be interpreted in a business intelligence context.

The project uses two complementary data mining approaches:

1. **Decision Tree Classification**: a supervised learning method used to classify order lines as profitable or loss-making and to extract interpretable business rules.
2. **K-Means RFM Segmentation**: an unsupervised learning method used to segment customers based on recency, frequency, and monetary behavior.

This combination is methodologically balanced because it covers both major branches of data mining: supervised prediction and unsupervised pattern discovery.

---

## 1. Decision Tree Classification

### 1.1 Problem Formulation

The classification task predicts whether an individual order line is profitable:

```text
Profitable = 1 if Profit > 0
Loss       = 0 if Profit <= 0
```

The target variable is derived from `Profit`, while `Profit` itself is not used as an input feature. The selected predictors are variables that are available at the order-line level:

- Numeric predictors: `Sales`, `Quantity`, and `Discount`.
- Categorical predictors: `Category`, `Sub-Category`, `Region`, `Segment`, and `Ship Mode`.

The categorical predictors are transformed through one-hot encoding. The train/test split uses a 75/25 ratio with stratification, which preserves the original class distribution in both training and testing subsets.

### 1.2 Rationale for Selecting a Decision Tree

A Decision Tree is appropriate for this project for four reasons.

First, it is interpretable. Unlike many black-box models, a Decision Tree produces explicit if-then decision rules. This is important in a BI project because the objective is not only to predict loss risk, but also to explain which business conditions lead to loss.

Second, it can model non-linear relationships and interactions between predictors. For example, the effect of discount may depend on the product category or sub-category.

Third, it does not require numerical standardization. Tree-based models split variables by thresholds and are not distance-based, unlike K-Means.

Fourth, it is lightweight and suitable for a small educational dataset. The implemented model is intentionally constrained with `max_depth = 4` and `min_samples_leaf = 30` to reduce overfitting and keep the decision rules readable.

### 1.3 Validation Strategy

The model is evaluated using several layers of evidence:

- **Baseline accuracy**: the accuracy obtained by always predicting the majority class.
- **Hold-out test set**: a 25% test set not used for training.
- **Confusion matrix**: a direct view of correct and incorrect predictions for Profit and Loss classes.
- **Macro F1-score**: a more balanced metric than accuracy when the classes are imbalanced.
- **5-fold stratified cross-validation**: used to verify that performance is stable across different splits.
- **Random Forest benchmark**: used as a robustness comparison against an ensemble model.
- **Validated decision rules**: extracted tree rules are checked against the held-out test set.

This validation design is important because the target distribution is imbalanced: approximately 80.6% of records are profitable and 19.4% are loss-making. Therefore, accuracy alone is not sufficient.

### 1.4 Model Results

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

The model improves substantially over the baseline accuracy of 0.8063. However, the confusion matrix shows an important limitation: the model still misses 115 actual loss-making records. This is why the loss recall of approximately 76% must be discussed transparently during the defense.

### 1.5 Validated Business Rule

The strongest extracted rule is:

```text
Discount > 0.25 AND Category != Technology -> Loss
```

| Rule | Predicted class | Test support | Correct | Incorrect | Precision |
| --- | --- | ---: | ---: | ---: | ---: |
| `Discount > 0.25 AND Category != Technology` | Loss | 318 | 316 | 2 | 99.37% |

This rule is highly meaningful for business interpretation. It indicates that when a product is discounted by more than 25% and is not in the Technology category, the corresponding order line is very likely to be loss-making. The rule covers 318 test records and correctly classifies 316 of them.

### 1.6 Role of the Random Forest Benchmark

The Random Forest benchmark achieves an accuracy of 0.9428, which is very close to the Decision Tree accuracy of 0.9440. This result supports the use of the simpler Decision Tree. If the ensemble model does not materially outperform the single tree, the more interpretable model is preferable for an academic BI project because it provides clearer business rules.

### 1.7 Strengths and Limitations

Strengths:

- Produces interpretable if-then rules.
- Supports both numerical and categorical predictors after encoding.
- Handles non-linear decision boundaries.
- Requires limited preprocessing.
- Provides feature importance and visual tree evidence.

Limitations:

- May overfit if the tree is not constrained.
- Can be sensitive to small changes in training data.
- Decision boundaries are axis-aligned and may be less smooth than other models.
- The imbalanced target distribution makes loss recall more difficult.
- A high-precision loss rule does not capture every loss-making transaction.

Possible improvements:

- Tune tree depth and leaf size through grid search.
- Apply class weighting or resampling to improve loss recall.
- Test additional features such as profit margin proxies, shipping cost if available, or product-level profitability indicators.
- Compare with logistic regression, gradient boosting, or calibrated probability models.

---

## 2. K-Means RFM Customer Segmentation

### 2.1 Problem Formulation

The segmentation task groups customers according to purchasing behavior. The model uses RFM features:

- **Recency**: the number of days since the customer's most recent purchase.
- **Frequency**: the number of distinct orders placed by the customer.
- **Monetary**: the total sales value generated by the customer.

The snapshot date is defined as one day after the maximum order date in the dataset. The final segmentation dataset contains 793 customers.

### 2.2 Rationale for Selecting RFM and K-Means

RFM is a standard customer analytics framework. It is suitable because it translates raw transaction history into three business-oriented indicators: how recently a customer purchased, how often the customer purchased, and how much revenue the customer generated.

K-Means is appropriate because it is a simple, widely used unsupervised clustering method. It is useful when the objective is to discover natural customer groups without predefined labels.

The combination of RFM and K-Means is therefore suitable for a BI project because it creates actionable customer segments that can support marketing and retention decisions.

### 2.3 Need for Standardization

K-Means is distance-based and uses Euclidean distance. The three RFM variables are measured on different scales:

- Recency is measured in days.
- Frequency is measured in order counts.
- Monetary is measured in sales value.

Without standardization, the Monetary variable would dominate the distance calculation because it has a much larger numerical scale. The model therefore applies `StandardScaler` before clustering. This gives each variable comparable influence in the clustering process.

### 2.4 Cluster Selection

The model uses `k = 4`. This choice is supported by:

- The Elbow Method, which evaluates the reduction in within-cluster inertia as `k` increases.
- The Silhouette score, which evaluates how well-separated the clusters are.
- Business interpretability, because four clusters produce distinct and explainable customer groups.

The Silhouette score for `k = 4` is **0.3554**. This indicates a moderate segmentation structure, which is acceptable for behavioral customer data where boundaries between groups are rarely perfectly separated.

The K-Means model uses `n_init = 10` and `random_state = 42`. Multiple initializations reduce sensitivity to random centroid starts, while the random state ensures reproducibility.

### 2.5 Segmentation Results

| Cluster | Segment label | Recency | Frequency | Monetary | Count |
| ---: | --- | ---: | ---: | ---: | ---: |
| 0 | Trung thanh / Active | 72.7 | 8.5 | 3,322.2 | 298 |
| 1 | Pho thong / Trung binh | 101.2 | 4.7 | 1,669.7 | 335 |
| 2 | VIP / Champions | 123.7 | 8.3 | 9,479.5 | 64 |
| 3 | Roi bo / Lost | 559.5 | 3.7 | 1,470.2 | 96 |

The cluster labels and colors are intentionally kept stable to remain consistent with previous project notes and visual outputs.

### 2.6 Business Interpretation

**Cluster 2 - VIP / Champions**

This group has the highest monetary value and a high purchase frequency. Although the group is relatively small, it contributes substantial revenue. It should be prioritized for retention programs, premium services, loyalty benefits, and personalized offers.

**Cluster 0 - Trung thanh / Active**

This group has the lowest recency and the highest frequency, indicating recent and repeated purchasing behavior. It is a strong active customer group and can be targeted for cross-selling and progression toward VIP status.

**Cluster 1 - Pho thong / Trung binh**

This is the largest segment. It has moderate recency and lower monetary value. The recommended action is to increase engagement through targeted promotions, bundles, or category-specific offers.

**Cluster 3 - Roi bo / Lost**

This group has very high recency, indicating long inactivity. Win-back campaigns may be used, but promotional cost should be controlled because the monetary value is not high.

### 2.7 Strengths and Limitations

Strengths:

- RFM is easy to explain and widely accepted in customer analytics.
- K-Means is efficient and reproducible.
- The resulting clusters are actionable for marketing and retention strategy.
- The model supports clear visualizations such as scatter plots and RFM heatmaps.

Limitations:

- The number of clusters must be chosen before fitting the model.
- K-Means assumes roughly compact and spherical clusters.
- It is sensitive to outliers, especially in Monetary.
- It works only with numerical variables unless categorical variables are transformed.
- Cluster boundaries may not represent strict business categories.

Possible alternatives:

- Hierarchical clustering for dendrogram-based interpretation.
- Gaussian Mixture Models for probabilistic cluster membership.
- DBSCAN for density-based clusters and outlier detection.
- RFM scoring rules as a non-machine-learning baseline.

---

## 3. Relationship to the BI Pipeline

The data mining component complements the SQL Server, SSIS, SSAS, Power BI, and Excel components. The warehouse and cube answer descriptive analytical questions such as what happened, where it happened, and which product or customer group contributed most. The data mining models extend the project by addressing predictive and exploratory questions:

- The Decision Tree identifies the conditions under which order lines are likely to become loss-making.
- K-Means identifies customer segments that require different business actions.

This makes the final BI solution more complete because it combines ETL, dimensional modeling, OLAP analysis, dashboards, and machine learning-based insight generation.

---

## 4. Common Defense Questions and Suggested Answers

**Question: Why use Decision Tree instead of only Random Forest?**

Random Forest is used as a benchmark, but the Decision Tree is retained because it has comparable accuracy and is more interpretable. In this project, rule explanation is more valuable than a small potential gain in predictive performance.

**Question: Is 94.40% accuracy reliable given the class imbalance?**

Accuracy should not be interpreted alone. The baseline accuracy is already 80.63% because most order lines are profitable. Therefore, macro F1-score, loss precision, loss recall, and the confusion matrix are also reported.

**Question: What is the most important business rule from the model?**

The strongest validated rule is `Discount > 0.25 AND Category != Technology -> Loss`, with 99.37% precision on the test set.

**Question: Why is K-Means applied after standardization?**

K-Means uses Euclidean distance. Without standardization, Monetary would dominate the distance calculation because it has a much larger scale than Recency and Frequency.

**Question: Why select four clusters?**

Four clusters are supported by Elbow and Silhouette analysis and produce business-interpretable segments: active customers, average customers, VIP customers, and lost customers.

**Question: Why use Sales as Monetary instead of Profit?**

Sales measures customer revenue contribution, which is the conventional Monetary definition in RFM analysis. Profit-based segmentation could be explored as an extension if the objective changes from revenue value to margin value.

---

## 5. Evidence Files to Include in the Report

Decision Tree outputs:

- `DataMining/outputs/class_balance.png`
- `DataMining/outputs/confusion_matrix.png`
- `DataMining/outputs/decision_tree.png`
- `DataMining/outputs/feature_importance.png`
- `DataMining/outputs/loss_rules.png`
- `DataMining/outputs/decision_rules.csv`
- `DataMining/outputs/loss_rules.csv`

K-Means RFM outputs:

- `DataMining/outputs/elbow_silhouette.png`
- `DataMining/outputs/elbow.png`
- `DataMining/outputs/rfm_profile.png`
- `DataMining/outputs/segments.png`
- `DataMining/outputs/rfm_profile.csv`
- `DataMining/outputs/rfm_customers.csv`
- `DataMining/outputs/model_summary.txt`

---

## 6. Short Academic Defense Statement

The data mining component uses two complementary algorithms. The Decision Tree is a supervised classification model used to predict whether an order line is profitable or loss-making and, more importantly, to extract interpretable rules. The strongest validated rule is that order lines with `Discount > 0.25` and a non-Technology category are predicted as loss-making with 99.37% precision. The K-Means model is an unsupervised segmentation method applied to standardized RFM features for 793 customers. It identifies four stable customer segments: `Trung thanh / Active`, `Pho thong / Trung binh`, `VIP / Champions`, and `Roi bo / Lost`. Together, these methods extend the BI system from descriptive reporting to predictive and behavioral analysis.
