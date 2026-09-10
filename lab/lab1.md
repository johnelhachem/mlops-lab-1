# Lab 1

## Solution adopted for the DVC data issue

I adopted **Solution 2: Reduce the data folder size**.

Because uploading the complete Food-11 dataset to DagsHub caused technical difficulties, I kept the full dataset locally in a separate `data_full/` folder and added it to `.gitignore`.

The `data/` folder contains only a small sample while keeping the required `training`, `evaluation`, and `validation` structure. This smaller dataset was tracked using DVC and successfully pushed to DagsHub. The processed and mini datasets were then generated from this sample and tracked through the updated `data.dvc` file.

---

## Question 1 — What do the files created by `uv init` contain?

When `uv init` is executed, it creates the initial structure needed for a Python project.

* **`pyproject.toml`** contains the project's main configuration, including its name, version, Python requirements, and dependencies.
* **`.python-version`** specifies the Python version associated with the project.
* **`README.md`** is created as a basic documentation file for the project.
* **`src/mlops_lab_1/__init__.py`** creates the Python package structure inside the `src` directory, where the project's source code can be placed.

At the beginning, `uv.lock` is not necessarily present. It is generated when dependencies are resolved, such as after installing a package with `uv add pillow`.

**In simple terms:** `uv init` creates the basic structure and configuration files for a Python project, while dependency-related files are completed as packages are added.

---

## Question 2 — What files are created by `dvc init` and what should be pushed?

Running `dvc init` creates the files and directories required for DVC to operate.

* **`.dvc/config`** contains project-level DVC configuration, such as the configured remote.
* **`.dvc/.gitignore`** prevents DVC's internal files from being tracked by Git.
* **`.dvcignore`** specifies files or directories that DVC should ignore.
* **`.dvc/cache/`** is used by DVC to store local copies of tracked data using hashes.
* **`.dvc/tmp/`** contains temporary files used internally by DVC.

Small configuration files such as `.dvc/config` and `.dvcignore` can be committed to Git when they do not contain sensitive information. The cache and temporary directories should not be committed because they are local and may contain large amounts of data.

**In simple terms:** Git stores the small DVC configuration and metadata, while DVC handles the actual dataset files.

---

## Question 3 — Where are the credentials stored, and should they be pushed?

DVC credentials should be stored outside the repository so that sensitive information does not become part of Git history.

When credentials are configured globally, they are saved in the user's machine-level DVC configuration rather than inside the project repository. DVC also supports local configuration files, which are kept separate from the project configuration and excluded from Git.

The remote URL itself can normally be stored in `.dvc/config`, but usernames, passwords, and access tokens should never be committed or pushed to GitHub.

**In simple terms:** configuration such as the remote address can be shared, but authentication credentials must remain private.

---

## Question 4 — What happened to `.gitignore`?

After running:

```text
dvc add data
```

DVC automatically added the `data` directory to `.gitignore`.

This prevents Git from treating the actual dataset files as regular files that should be committed. Instead, Git tracks the DVC pointer file while DVC is responsible for managing the dataset itself.

**In simple terms:** the dataset is excluded from normal Git tracking, while DVC keeps track of its contents and version.

---

## Question 5 — What is the `.dvc` file?

When `dvc add data` is executed, DVC creates a file called `data.dvc`.

It acts as a pointer describing the version of the `data` directory being tracked. It contains information such as:

```text
outs:
- md5: <hash>.dir
  size: <bytes>
  nfiles: <count>
  hash: md5
  path: data
```

The **MD5 hash** identifies the current contents of the dataset. If the contents change, the hash also changes. The **size** represents the amount of data, while **`nfiles`** indicates how many files are included. The **path** tells DVC which directory the pointer refers to.

This small pointer file is committed to Git instead of the actual images. When the dataset needs to be restored, DVC can use the information in `data.dvc` to retrieve the corresponding data from its storage.

**In simple terms:** `data.dvc` is a small version-controlled pointer that tells DVC which version of the actual dataset belongs to the current Git commit.

---

## Question 6 — What can be seen on GitHub and DagsHub?

The project's source code and configuration files are available on GitHub, including the Python source files, project configuration, README, and DVC metadata.

The actual `data` directory is not stored directly in GitHub. Instead, GitHub contains the `data.dvc` file, which acts as a pointer to the dataset managed by DVC.

The small sample dataset was successfully pushed to the DagsHub DVC remote using `dvc push`, so the actual DVC-managed data is stored there.

The complete Food-11 dataset is kept locally in `data_full/` and is listed in `.gitignore`, so it is not uploaded to GitHub.

**In simple terms:**

**GitHub →** source code + DVC pointer and configuration
**DagsHub →** small DVC-tracked dataset
**Laptop →** complete `data_full` dataset

---

## Question 7 — What happens after cloning the repository into a new folder?

After cloning the repository into a completely new directory, the `data` folder is not present because Git only retrieves the files that were committed to the repository.

The repository contains `data.dvc`, but not the actual image files. To retrieve the dataset associated with that pointer, DVC provides the following command:

```text
dvc pull
```

This command reads the DVC metadata and downloads the corresponding data from the configured remote.

**In simple terms:** `git clone` retrieves the project and the DVC pointer, while `dvc pull` is needed to obtain the actual dataset.

---

## Question 8 — Do you still see `food11_processed` and `food11_processed_mini`?

No.

After checking out an earlier commit and then running:

```text
git checkout <old-commit-hash>
dvc checkout
```

the `data` directory returns to the version associated with that older commit. Since the processed datasets had not yet been added at that point, the folders:

```text
food11_processed
food11_processed_mini
```

are no longer present.

This happens because Git restores the older version of `data.dvc`, and `dvc checkout` then synchronizes the actual data on disk with that older DVC version.

To return to the latest version, the following commands are used:

```text
git checkout main
dvc checkout
```

The processed folders then reappear because the `main` branch contains the newer `data.dvc` version.

This demonstrates the relationship between Git and DVC: Git controls the version of the project and its DVC pointer, while DVC restores the corresponding version of the actual data.
