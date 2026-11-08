# Lab 5 - CI/CD with GitHub Actions

## Q1. Why should unit tests not load the real model?

A unit test should be fast and independent. It could fail because the MLflow server is down, the network is unavailable, or the model artifacts cannot be loaded, even when our code is correct.

## Q2. What does the fake model test prove?

It proves that the API accepts an image and returns the expected JSON with a category and confidence. It does not prove that our real model is accurate or that it predicts the correct food.

## Q3. Which validation check detected the duplicate?

The file hash check detected the duplicate between training and evaluation. A duplicate is dangerous because it causes data leakage and can give us an unrealistically high test accuracy. A corrupted image is easier to notice because it may cause an error.

## Q4. Where should data validation run?

We can run it locally before pushing the data, and in a data pipeline or self-hosted runner that has access to the DVC dataset.

## Q5. What happens when a unit test fails?

Because the smoke job uses `needs: test`, it is skipped when the test job fails. Without `needs`, both jobs could run independently, wasting time building an image for broken code.

## Q6. What happened when we ran CI twice?

One of our successful runs took about 1 minute and 24 seconds. The second run can be faster because uv and Docker reuse cached dependencies and image layers instead of downloading or building everything again.

## Q7. Why use the commit SHA instead of latest?

A commit SHA identifies the exact code used to build an image. The `latest` tag can change after another push. For example, one machine might pull `latest` before an update and another after it, so they run different versions.

## Q8. Why declare permissions explicitly?

We only give the GitHub token the permissions needed to push the Docker image to GHCR. If a workflow step is compromised, a token with too many permissions could be used to modify repository code or other resources.

## Q9. What happened with branch protection?

When we broke the test, the pull request showed a failed check and merging was blocked. After fixing the test, the checks passed and we merged it. This helps a team because GitHub checks the code automatically instead of depending on everyone testing locally.

## Q10. What did the model promotion gate decide?

Our champion was Version 3 with 72.73% accuracy on 550 test images. The standard error was about 1.90%, so the required improvement was about 3.80 percentage points. The promotion threshold was 76.53%.

Candidate Version 4 achieved 45.45%, so it became `challenger`.

Candidate Version 5 achieved 78.00%, so it passed the threshold and became the new `champion`.

## Q11. How can promotion run automatically?

We can run the promotion script after training in a local scheduled pipeline or on a self-hosted runner that can reach MLflow. Another solution is to use a hosted MLflow server, such as DagsHub, that GitHub Actions can access securely.

## Q12. Our CI/CD pipeline

```text
git push / pull request
          |
          v
   GitHub Actions
       (automatic)
          |
          v
   Test job
   - Install dependencies
   - Ruff lint
   - Pytest
          |
       If passed
          |
          v
   Smoke job
   - Build Docker image
   - Start container
   - Check /health
          |
       If main branch
          |
          v
   Push job
   - Push image to GHCR
   - Tag with commit SHA
          |
          v
   Image available in GHCR
          |
          v
   Manual deployment
   - Pull Docker image
   - Start application
          |
          v
   Running container
   - Load food11@champion
```

The code version is decided automatically by the Git commit SHA. The model version is decided separately by our MLflow promotion script using the accuracy threshold. Running the promotion script and deploying the new image are still manual in our current setup.
