import pandas as pd

input_file = "data/2019-Oct.csv"
output_file = "data/2019-Oct-sample.csv"

df = pd.read_csv(
    input_file,
    nrows=100_000,
    low_memory=False
)

df.to_csv(
    output_file,
    index=False
)

print(f"Sample created successfully: {len(df):,} rows")
print(f"Saved to: {output_file}")