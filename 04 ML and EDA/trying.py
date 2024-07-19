import xgboost as xgb

# Load the trained model
model = xgb.Booster()
model.load_model('04 ML and EDA/models/xgb_model.json')

# You can get feature names from the model if available
# Note: this assumes that the feature names were saved in the model during training
if model.feature_names:
    feature_names = model.feature_names
    print("Feature names:", feature_names)
else:
    print("Feature names are not available in the model.")