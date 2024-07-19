import pickle
from sklearn.preprocessing import OrdinalEncoder
import numpy as np
# Load the OrdinalEncoder
with open('04 ML and EDA/models/no_stops_ordinal_encoder.pkl', 'rb') as file:
    no_stops_ordinal_encoder = pickle.load(file)

# Check the categories the encoder was trained on
print("Categories trained on:")
for i, category in enumerate(no_stops_ordinal_encoder.categories_):
    print(f"Feature {i}: {category}")
    print(type(category[0]))

print(no_stops_ordinal_encoder.transform(np.array('non-stop').reshape(-1, 1)))