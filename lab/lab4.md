# Lab 4 - Orchestrating the App with Docker Compose

## Q1. What happens without a volume?

Without a volume, MLflow data is stored inside the container. If we remove the container and create a new one, the data is lost and the registry starts empty.

## Q2. Why use a named volume instead of a bind mount?

A named volume is managed by Docker and makes data persistence easier. A bind mount would also work, but it depends on a specific folder on the host machine.

## Q3. Why does `http://mlflow:5000` work in Compose?

Docker Compose creates a network for all services. Containers can communicate using their service names, so `mlflow` resolves to the MLflow container.

## Q4. Why use an environment variable for `INFERENCE_URL`?

It makes the frontend more flexible. We can change the inference server address without changing the Python code, whether we run it inside or outside Compose.

## Q5. Why doesn't inference publish a port?

Inference only needs to communicate with the frontend inside the Docker network. It doesn't need a port published to the host machine.

## Q6. What happens if MLflow isn't ready?

Inference may fail because it tries to load the model before MLflow is ready. `depends_on` controls startup order, not readiness. We can check the error with `docker compose logs inference`.

## Q7. Which services have published ports?

MLflow publishes port 5000 and the frontend publishes port 8501. Inference uses port 8000 internally, which matches our Compose configuration.

## Q8. Does inference use the new model after promotion?

Not immediately, because FastAPI loads the model once at startup. After moving the `champion` alias to version 3, we ran `docker compose restart inference` to load it.

## Q9. Why does restarting work without rebuilding?

The Docker image contains the application code and dependencies, while the model is fetched from MLflow at startup. Restarting loads the promoted version without rebuilding the image.

## Q10. What happens with `down` and `down -v`?

After `docker compose down` and `docker compose up`, our model and `champion` alias were still available. With `docker compose down -v`, the volume was deleted and the models disappeared. We restored the data from a backup.

## Q11. What is needed for scaling and high availability?

We would need an orchestrator like Kubernetes for multiple inference replicas, load balancing, and recovery after machine failures. MLflow would also need shared storage and a reliable database.

## Practical Result

We connected MLflow, FastAPI, and Streamlit using Docker Compose. We tested image predictions, promoted model version 3, restarted inference without rebuilding, and verified data persistence with a named volume.
