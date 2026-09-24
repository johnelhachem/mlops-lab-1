# Lab 3 Answers

## Question 1
My model was first registered as **Version 1**.  
A logged model belongs to one MLflow run, while a registered model is managed under a name and version in the Model Registry.

## Question 2
MLflow now uses aliases like **champion** and **challenger** instead of fixed stages.  
An alias is flexible because I can move it to a newer model version without changing my code.

## Question 3
I use `models:/food11@champion` so my code is not tied to one `.pth` file.  
To serve a newer model, I only need to move the `champion` alias to the new version.

## Question 4
I copy `pyproject.toml` and `uv.lock` first so Docker can cache the dependency installation.  
If I only change `serve.py`, Docker can reuse the dependency layer and rebuild faster.

## Question 5
The multi-stage image has a content size of **427 MB**, while the single-stage image is **458 MB**, so the multi-stage build saves about **31 MB**.  
The biggest layer is the Python virtual environment containing PyTorch, torchvision, MLflow, and the other dependencies.

## Question 6
Without `.dockerignore`, Docker sends unnecessary files like `data/`, `.git/`, `.venv/`, and `mlruns/` during the build.  
This makes the build slower and larger.

## Question 7
Inside the container, `127.0.0.1` points to the container itself, not my Windows host.  
`host.docker.internal` lets the container reach the MLflow server running on my host machine.

## Question 8
Yes, the model still worked after starting a new container from the same image without rebuilding.  
This shows that the app and dependencies are inside the image, while the model is loaded from MLflow at runtime.

## Question 9
The Docker image still needs to be pushed to a container registry such as Docker Hub or GitHub Container Registry.  
Using a fixed version tag is also better than using only `latest`.
