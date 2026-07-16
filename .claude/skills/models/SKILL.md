---
name: models
description: Guidelines and instructions for the Models Layer.
---

# Models Layer Guidelines

When working on the Models Layer for TerraPulse, strictly adhere to the following rules:

1. **Sequential Evaluation**: Machine learning models (like Price Prediction using LightGBM) and rule-based models (Affordability, Safety, Livability) must be versioned and stored in `models_layer/registry/models`.
2. **Promotion Rule**: A model is only promoted to active (`is_active=True`) if it strictly outperforms the current active model in its specific metric.
3. **Scoring Formulas**:
   - **Affordability**: `Score = max(0, 100 - (Price / 10000) * 0.6 - (Deprivation * 10) * 0.4)`
   - **Safety**: `Score = max(0, 100 - (Crime / Population * 1000) * 2)`
