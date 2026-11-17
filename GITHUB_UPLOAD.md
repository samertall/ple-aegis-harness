# Upload this project to a fresh GitHub repository (PowerShell)

The ChatGPT GitHub connection can read/write existing repositories but cannot create a new repository here. No matching existing PLE repository was found. The steps below are therefore still required.

1. Create a **public empty repository** named `ple-aegis-harness` under your GitHub account (GitHub > New Repository). Do **not** add a README or license on GitHub; this project already includes both.
2. Extract the provided ZIP and open PowerShell inside the extracted `ple-aegis-harness` directory.
3. Run:

```powershell
git init
git branch -M main
git add .
git commit -m "Initial Aegis PLE harness"
git remote add origin https://github.com/samertall/ple-aegis-harness.git
git push -u origin main
```

4. **This initial push is not a valid competition submission** because the benchmark `artifacts/` are not yet generated. Complete official validation and a 29-task dev run as described in README.
5. After evaluation artifacts are present, commit and push again:

```powershell
git add -A
git commit -m "Aegis PLE with validated dev artifacts"
git push
git rev-parse HEAD
```

6. Copy the 40-character SHA from the final command to the Kaggle Writeup. Verify that the repo on GitHub has the real unpacked artifacts, then submit through Kaggle.

A direct check on November 17, 2026 confirmed that `samertall/ple-aegis-harness` was **not found**. This environment's connected GitHub actions can edit existing repositories but cannot create a repository. Create it at https://github.com/new (repository name `ple-aegis-harness`), then publish. The local Git commit in this package is **not** yet a published commit and must not be inserted in a Kaggle submission as a verified GitHub SHA.
