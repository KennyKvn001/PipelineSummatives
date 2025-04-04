import pandas as pd

print(f"Pandas version: {pd.__version__}")
print(f"DataFrame: {pd.DataFrame}")
df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
print(df)
