import numpy as np
import bentoml
from bentoml.io import NumpyNdarray, JSON
from pydantic import BaseModel, Field
from starlette.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import jwt
from datetime import datetime, timedelta
import json

# Secret key and algorithm for JWT authentication
JWT_SECRET_KEY = "your_jwt_secret_key_here"
JWT_ALGORITHM = "HS256"

# User credentials for authentication
USERS = {
    "user123": "password123",
    "user456": "password456"
}

predict_route = "predict"

class JWTAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        if request.url.path == f"/{predict_route}":
            token = request.headers.get("Authorization")
            if not token:
                return JSONResponse(status_code=401, content={"detail": "Missing authentication token"})

            try:
                token = token.split()[1]  # Remove 'Bearer ' prefix
                payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            except jwt.ExpiredSignatureError:
                return JSONResponse(status_code=401, content={"detail": "Token has expired"})
            except jwt.InvalidTokenError:
                return JSONResponse(status_code=401, content={"detail": "Invalid token"})

            request.state.user = payload.get("sub")

        response = await call_next(request)
        return response

# Pydantic model to validate input data
class InputModel(BaseModel):
    gre_score: int
    toefl_score: int
    university_rating: int
    sop: float
    lor: float
    cgpa: float
    research: int
    

def load_latest_admission_tag():
    models = bentoml.models.list()
    admission_models = [m for m in models if m.tag.name.startswith("admission_")]
    if not admission_models:
        raise ValueError("No model starting with 'admission_' found.")

    latest = max(admission_models, key=lambda m: m.info.creation_time)
    return latest.tag


admission_model_tag = str(load_latest_admission_tag()).split(":")[0]

# Get the model from the Model Store
model_runner = bentoml.sklearn.get(f"{admission_model_tag}:latest").to_runner()

# Create a service API
model_service = bentoml.Service(f"ulmer_admission_service", runners=[model_runner])

# Add the JWTAuthMiddleware to the service
model_service.add_asgi_middleware(JWTAuthMiddleware)

# Create an API endpoint for the service
@model_service.api(input=JSON(), output=JSON())
def login(credentials: dict) -> dict:
    username = credentials.get("username")
    password = credentials.get("password")

    if username in USERS and USERS[username] == password:
        token = create_jwt_token(username)
        return {"token": token}
    else:
        # Convert JSONResponse to dict before returning
        response = JSONResponse(status_code=401, content={"detail": "Invalid credentials"})
        return json.loads(response.body.decode("utf-8"))

# Create an API endpoint for the service
@model_service.api(
    input=JSON(pydantic_model=InputModel),
    output=JSON(),
    route=predict_route
)
async def classify(input_data: InputModel, ctx: bentoml.Context) -> dict:
    request = ctx.request
    user = request.state.user if hasattr(request.state, 'user') else None

    # Convert the input data to a numpy array
    input_series = np.array([input_data.gre_score, input_data.toefl_score, input_data.university_rating, input_data.sop,
                             input_data.lor, input_data.cgpa, input_data.research])

    result = await model_runner.predict.async_run(input_series.reshape(1, -1))

    return {
        "prediction": result.tolist(),
        "user": user
    }

# Function to create a JWT token
def create_jwt_token(user_id: str, expiration_time: timedelta=timedelta(hours=1)):
    expiration = datetime.utcnow() + expiration_time
    payload = {
        "sub": user_id,
        "exp": expiration
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token