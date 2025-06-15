#!/bin/bash

# Create the target directory if it doesn't exist
mkdir -p data/raw

# Download the file
curl -o data/raw/admissions.csv https://datascientest.s3-eu-west-1.amazonaws.com/examen_bentoml/admissions.csv