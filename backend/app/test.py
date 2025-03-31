# test.py
from .models import dropout_model
from .schema import StudentInput
import pandas as pd

dropout_model.load_pretrained()
result = dropout_model.predict(pd.DataFrame([...]))
