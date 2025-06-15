#!/bin/bash

# Create the target directory if it doesn't exist
mkdir -p data/raw

# Download the file
curl -o data/raw/admission.csv https://assets-datascientest.s3.eu-west-1.amazonaws.com/MLOPS/bentoml/admission.csv