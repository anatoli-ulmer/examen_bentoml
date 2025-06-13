import pandas as pd
import sklearn
import os
from pathlib import Path
from sklearn.model_selection import train_test_split

project_dir = Path(__file__).resolve().parent.parent
raw_path = os.path.join(project_dir, 'data', 'raw', 'admission.csv')
processed_dir = os.path.join(project_dir, 'data', 'processed')

def main():
    
    print(f"reading raw data from: {raw_path}")
    df = pd.read_csv(raw_path)
    df = df.drop("Serial No.", axis=1)
    
    target = "Chance of Admit "
    X = df.drop(target, axis=1)
    y = df[target]
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.2,
        random_state=42,
        shuffle=True
    )
    
    print(f"saving data to: {processed_dir}")
    os.makedirs(processed_dir, exist_ok=True)
    X_train.to_csv(os.path.join(processed_dir, "X_train.csv"), index=False)
    X_test.to_csv(os.path.join(processed_dir, "X_test.csv"), index=False)

    y_train.to_csv(os.path.join(processed_dir, "y_train.csv"))
    y_test.to_csv(os.path.join(processed_dir, "y_test.csv"))
    # # If y is a Series, convert it to a DataFrame to ensure correct column name
    y_train.to_frame(name="Chance of Admit").to_csv(os.path.join(processed_dir, "y_train.csv"), index=False)
    y_test.to_frame(name="Chance of Admit").to_csv(os.path.join(processed_dir, "y_test.csv"), index=False)


if __name__ == "__main__":
    main()