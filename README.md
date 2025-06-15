# BentoML Exam Solution

This directory contains my solution for the DataScientest BentoML exam.

Here is how the solution is structured:

```bash       
├── Dockerfile.template
├── LICENSE
├── README.md
├── bento_image.tar
├── bentofile.yaml
├── data
│   ├── processed
│   │   ├── X_test.csv
│   │   ├── X_train.csv
│   │   ├── y_test.csv
│   │   └── y_train.csv
│   └── raw
│       └── admissions.csv
├── models
├── pytest.ini
├── requirements.txt
├── scripts
│   ├── download_raw.sh
│   ├── latest_docker_to_tar.sh
│   └── serve_model.sh
├── src
│   ├── prepare_data.py
│   ├── service.py
│   └── train_model.py
└── tests
    └── test_service.py
```

### Download raw data
```bash
curl -o data/raw/admission.csv https://assets-datascientest.s3.eu-west-1.amazonaws.com/MLOPS/bentoml/admission.csv
```

### Preprocess data
```bash
python src/prepare_data.py
```

### Training model and saving it to bento store
```bash
python src/train_model.py
```

### Start serving trained model with bentoml

```bash
./scripts/serve_model.sh
```

### How to create and run docker container

```bash
bentoml build
bentoml containerize ulmer_admission_service:latest
docker run -p 3000:3000 $(docker images ulmer_admission_service --format '{{.Repository}}:{{.Tag}}' | head -n 1)
```

### Compress latest docker container to tar file for distribution

```bash
docker save -o bento_image.tar $(docker images ulmer_admission_service --format '{{.Repository}}:{{.Tag}}' | head -n 1)
```

### Load docker image from tar file (if existent) and run it

```bash
docker load -i bento_image.tar
docker run -p 3000:3000 $(docker images ulmer_admission_service --format '{{.Repository}}:{{.Tag}}' | head -n 1)
```

### Run unit tests in a second terminal (service must be running in the first terminal)

```bash
pytest
```