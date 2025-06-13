# train_model.py
import pandas as pd
import os
from pathlib import Path
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import bentoml

project_dir = Path(__file__).resolve().parent.parent
processed_dir = os.path.join(project_dir, 'data', 'processed')

def load_data():
    X_train = pd.read_csv(os.path.join(processed_dir, 'X_train.csv'))
    X_test = pd.read_csv(os.path.join(processed_dir, 'X_test.csv'))
    y_train = pd.read_csv(os.path.join(processed_dir, 'y_train.csv')).squeeze()
    y_test = pd.read_csv(os.path.join(processed_dir, 'y_test.csv')).squeeze()
    return X_train, X_test, y_train, y_test
    

def main():    
    print(f"reading processed data from: {processed_dir}")   
    X_train, X_test, y_train, y_test = load_data()
    
    print(f"training models")
    models = {
        "linear_regression": LinearRegression(),
        "decision_tree": DecisionTreeRegressor(random_state=42),
        "random_forest": RandomForestRegressor(n_estimators=100, random_state=42)
    }

    results = []
    best_model_name = None
    best_model_score = float("inf")  # or `-float("inf")` for metrics where higher is better
    best_model = None

    for name, model in models.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        
        mse = mean_squared_error(y_test, y_pred)
        rmse = mse ** 0.5
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        results.append({
            "Model": name,
            "MAE": mae,
            "MSE": mse,
            "RMSE": rmse,
            "R^2": r2
        })
        
        # Select model with lowest RMSE
        if rmse < best_model_score:
            best_model_score = rmse
            best_model_name = name
            best_model = model
    
    print(f"comparing results:")
    results_df = pd.DataFrame(results)
    print(results_df.sort_values(by="RMSE"))
    print(f"Best model: {best_model_name} (RMSE: {best_model_score:.4f})")

    print(f"Saving best model to bento store: admission_{best_model_name}")
    bentoml.sklearn.save_model(f"admission_{best_model_name}", best_model)

if __name__ == "__main__":
    main()