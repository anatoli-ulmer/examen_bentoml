import requests
import pytest
from time import sleep
from datetime import datetime, timedelta
import sys
import os
import warnings

warnings.filterwarnings(
    "ignore",
    message=".*Subclassing `GenerateSchema` is not supported.*",
    category=UserWarning,
    module="_bentoml_sdk._pydantic"
)

# Add the 'src' directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from service import create_jwt_token

# The URL of the login and prediction endpoints
login_url = "http://127.0.0.1:3000/login"
predict_url = f"http://127.0.0.1:3000/predict"

# Données de connexion
credentials = {
    "username": "user123",
    "password": "password123"
}

test_data = {
    "gre_score": 337,
    "toefl_score": 118,
    "university_rating": 4,
    "sop": 4.5,
    "lor": 4.5,
    "cgpa": 9.65,
    "research": 1
}


def test_auth_fails_without_token():
    # Verify that authentication fails if the JWT token is missing or invalid.
    response = requests.post(
        predict_url,
        headers={
            "Content-Type": "application/json"
        },
        json=test_data
    )
    assert response.status_code == 401
    assert response.json()['detail'] == 'Missing authentication token'
    
    
def test_auth_fails_with_empty_token():
    # Verify that authentication fails if the JWT token is missing or invalid.
    response = requests.post(
        predict_url,
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer {None}"
        },
        json=test_data
    )
    assert response.status_code == 401
    assert response.json()['detail'] == 'Invalid token'
    
    
def test_auth_fails_with_invalid_token():
    # Verify that authentication fails if the JWT token is missing or invalid.
    response = requests.post(
        predict_url,
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer invalid.token.value"
        },
        json=test_data
    )
    assert response.status_code == 401
    assert response.json()['detail'] == 'Invalid token'
    
    
def test_auth_failes_with_expired_token():
    # Verify that authentication fails if the JWT token has expired.
    expired_token = create_jwt_token(credentials["username"], timedelta(seconds=1))
    sleep(1)
    
    response = requests.post(
        predict_url,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {expired_token}"
        },
        json=test_data
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Token has expired"
    
    
def test_login_successful_returns_jwt():
    # Verify that authentication succeeds with returning a JWT token.
    login_response = requests.post(
        login_url,
        headers={"Content-Type": "application/json"},
        json=credentials
    )
    assert login_response.status_code == 200
    assert "token" in login_response.json()
    

def test_login_fails_with_wrong_credentials():
    # Verify that the API does not return a JWT token for incorrect user credentials.
    login_response = requests.post(
        login_url,
        headers={"Content-Type": "application/json"},
        json={"username": "wronguser", "password": "wrongpw"}
    )
    assert login_response.status_code == 200
    assert not "token" in login_response.json()


def test_prediction_succeeds_with_valid_token_and_input():
    # Verify that authentication succeeds with a valid JWT token.
    login_response = requests.post(
        login_url,
        headers={"Content-Type": "application/json"},
        json=credentials
    )
    token = login_response.json().get("token")
    response = requests.post(
        predict_url,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        },
        json=test_data
    )
    assert response.status_code == 200
    assert 'prediction' in response.json()
    
    
# def test_login_successful_returns_jwt(): ...
# def test_login_fails_with_wrong_credentials(): ...
# def test_prediction_fails_without_token(): ...
# def test_prediction_succeeds_with_valid_token_and_input(): ...
    # Verify that authentication succeeds with a valid JWT token.
    # login_response = requests.post(
    #     login_url,
    #     headers={"Content-Type": "application/json"},
    #     json=credentials
    # )
    # assert login_response.status_code == 200
    # assert "token" in login_response.json()
    # token = login_response.json().get("token")
    # response = requests.post(
    #     predict_url,
    #     headers={
    #         "Content-Type": "application/json",
    #         "Authorization": f"Bearer {token}"
    #     },
    #     json=test_data
    # )
    # assert response.status_code == 200
# test_prediction_fails_with_invalid_input


if __name__ == "__main__":
    test_auth_fails_without_token()
    test_auth_fails_with_empty_token()
    test_auth_fails_with_invalid_token()
    test_auth_failes_with_expired_token()
    
    test_login_successful_returns_jwt()
    test_login_fails_with_wrong_credentials()
    
    test_prediction_succeeds_with_valid_token_and_input()