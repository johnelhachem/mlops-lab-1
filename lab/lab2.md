# Lab 2 - Model Training and Experiment Tracking with MLflow

## Question 1

**Look at `pyproject.toml` and `uv.lock`. What changed?**

`pyproject.toml` was updated to include the Lab 2 dependencies:

* `mlflow`
* `torch`
* `torchvision`
* `scikit-learn`

It also specifies the CPU-only PyTorch package source. `uv.lock` was updated with the resolved package versions and dependencies.

## Question 2

**What is `--backend-store-uri` used for? What is `--default-artifact-root` used for? What is the difference between the metadata MLflow stores and the artifacts it stores?**

`--backend-store-uri` specifies where MLflow stores tracking metadata such as experiments, runs, parameters, and metrics.

`--default-artifact-root` specifies where MLflow stores artifacts such as trained models and output files.

The metadata describes the experiment and run, while artifacts are the actual files produced by the run.

## Question 3

**Why shouldn't `mlflow.db` and `mlruns/` be tracked by git, and why shouldn't they be tracked by DVC either?**

`mlflow.db` and `mlruns/` are generated experiment-tracking files and can change after every run. They are not source code or datasets that need to be versioned with Git or DVC.

They should therefore be ignored using `.gitignore`.

## Question 4

**What happens the first time you call `set_experiment` with a name that doesn't exist yet? Check the MLflow UI.**

When `mlflow.set_experiment("food11")` was called for the first time, MLflow automatically created the `food11` experiment. It then appeared in the MLflow UI.

## Question 5

**What is the difference between `mlflow.log_param` and `mlflow.log_metric`? Why does `log_metric` take a `step` argument and `log_param` doesn't?**

`mlflow.log_param` records fixed run configuration values, such as learning rate, batch size, and number of epochs.

`mlflow.log_metric` records numerical results such as training loss, validation loss, and validation accuracy.

Metrics can change during training, so `step` identifies where the metric was recorded, such as the epoch number. Parameters describe the run configuration and therefore do not need a step.

## Question 6

**Open the run in the MLflow UI. Find the params, metric charts, and logged model artifact. Where does the model artifact actually live on disk?**

The MLflow UI shows the parameters, metric history, and logged model artifact.

For the best run, the run ID is:

```text
a10f90bf6bc64f8087fc818f083ab2fd
```

The model artifact is stored under:

```text
mlruns/1/a10f90bf6bc64f8087fc818f083ab2fd/artifacts/model/
```

## Question 7

**Which learning rate gave the best `val_accuracy`? Is higher always better?**

The learning rate `0.0001` gave the best final `val_accuracy`, with a value of `0.712`.

A higher learning rate is not always better. In these experiments, increasing the learning rate to `0.01` resulted in much lower validation accuracy (`0.088`).

## Question 8

**Use the parallel coordinates plot on the compare page to look at `lr`, `batch_size` and `val_accuracy` together. What pattern do you see?**

The `lr=0.0001` and `batch_size=32` combination achieved the highest validation accuracy (`0.712`).

The `lr=0.01` and `batch_size=32` combination performed much worse (`0.088`).

For `lr=0.001`, increasing the batch size from `32` to `64` reduced the final validation accuracy from `0.576` to `0.397`.

Therefore, in these four experiments, the smaller learning rate performed better, while the larger batch size did not improve the result.

## Question 9

**Sort the runs table by `val_accuracy` descending. Which run is the best one? Note its run ID, you'll need it in the next lab.**

The best run is:

```text
Run: bald-crow-558
Run ID: a10f90bf6bc64f8087fc818f083ab2fd
Final val_accuracy: 0.712
```

This run also reached a maximum validation accuracy of about `0.718` during the fifth epoch.
