import sys
import pandas as pd
import numpy as np
import os

def check_inputs():
    # 1. Parameter Count Check
    if len(sys.argv) != 5:
        print("Error: Wrong number of parameters.")
        print("Usage: python <program.py> <InputDataFile> <Weights> <Impacts> <ResultFileName>")
        sys.exit(1)

    input_file = sys.argv[1]
    weights = sys.argv[2]
    impacts = sys.argv[3]
    result_file = sys.argv[4]

    # 2. File Not Found Check
    if not os.path.isfile(input_file):
        print(f"Error: File '{input_file}' not found.")
        sys.exit(1)

    try:
        df = pd.read_csv(input_file)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

    # 3. Column Count Check (>=3 columns)
    if df.shape[1] < 3:
        print("Error: Input file must contain three or more columns.")
        sys.exit(1)

    # 4. Non-numeric Check
    data_df = df.iloc[:, 1:]
    # Check if all values in the selected columns are numeric
    try:
        data_df = data_df.apply(pd.to_numeric)
    except ValueError:
        print("Error: From 2nd to last columns must contain numeric values only.")
        sys.exit(1)

    # Process weights and impacts
    try:
        weight_list = [float(w) for w in weights.split(',')]
        impact_list = impacts.split(',')
    except ValueError:
        print("Error: Weights must be numeric and separated by commas.")
        sys.exit(1)

    # 5. Matching Counts Check
    if len(weight_list) != len(impact_list) or len(weight_list) != data_df.shape[1]:
        print("Error: Number of weights, impacts, and columns (from 2nd to last) must be the same.")
        sys.exit(1)

    # 6. Impact Validation
    if not all(i in ['+', '-'] for i in impact_list):
        print("Error: Impacts must be either '+' or '-'.")
        sys.exit(1)

    return df, data_df, weight_list, impact_list, result_file

def topsis_logic(df, data_df, weights, impacts):
    # Vector Normalization
    normalized_df = data_df.copy()
    rss = np.sqrt((data_df**2).sum()) 
    normalized_df = normalized_df / rss

    # Weighted Normalization
    weighted_df = normalized_df * weights

    # Ideal Best and Worst
    ideal_best = []
    ideal_worst = []

    for i, col in enumerate(weighted_df.columns):
        if impacts[i] == '+':
            ideal_best.append(weighted_df[col].max())
            ideal_worst.append(weighted_df[col].min())
        else:
            ideal_best.append(weighted_df[col].min())
            ideal_worst.append(weighted_df[col].max())

    # Euclidean Distance
    S_plus = np.sqrt(((weighted_df - ideal_best) ** 2).sum(axis=1))
    S_minus = np.sqrt(((weighted_df - ideal_worst) ** 2).sum(axis=1))

    # Topsis Score
    score = S_minus / (S_plus + S_minus)
    
    # Append to original DF
    df['Topsis Score'] = score
    df['Rank'] = score.rank(ascending=False)
    
    return df

def main():
    df, data_df, weights, impacts, result_file = check_inputs()
    result_df = topsis_logic(df, data_df, weights, impacts)
    result_df.to_csv(result_file, index=False)
    print(f"Result saved to {result_file}")

if __name__ == "__main__":
    main()