# Incident ERR-013: GitHub Pre-Receive Hook Large File Rejection (423 MB `archive.zip`)

- **Incident ID**: `ERR-013`
- **Severity**: **P2 — Medium** (Git Remote Deployment Blocker)
- **Component**: Git VCS / CI/CD Deployment (`git push origin main:main`)
- **Status**: **RESOLVED**
- **Date**: 2026-10-27

---

## 1. Incident Summary

During `git push origin main:main` to the remote repository `https://github.com/itsjustayush/ZipText-ZTAR-.git`, GitHub's pre-receive hook declined the push with error `GH001: Large files detected`. The file `resources/archive.zip` was 423.95 MB, which exceeded GitHub's strict 100.00 MB limit.

---

## 2. Exact Error Output

```text
> git push origin main:main
remote: error: Trace: e4f1cdb5dc0486019b7d2d7d2d37b96d882c607bf967ac8849fbe1327fbbb449        
remote: error: See https://gh.io/lfs for more information.        
remote: error: File resources/archive.zip is 423.95 MB; this exceeds GitHub's file size limit of 100.00 MB        
remote: error: GH001: Large files detected. You may want to try Git Large File Storage - https://git-lfs.github.com.        
To https://github.com/itsjustayush/ZipText-ZTAR-.git
 ! [remote rejected] main -> main (pre-receive hook declined)
error: failed to push some refs to 'https://github.com/itsjustayush/ZipText-ZTAR-.git'
```

---

## 3. Root Cause Analysis

1. **Commit History Retention**: In commit `21682c1` (`feat: add test datasets, archive samples, and validation classifiers`), `resources/archive.zip` (444,540,604 bytes) was committed.
2. Even though a subsequent commit `3be256f` deleted the file from the working tree (`git rm resources/archive.zip`), Git commit history is immutable by default.
3. When pushing the local branch `main` to `origin/main` (which was at `8c11274`), Git attempted to transfer the entire commit graph, including the 444 MB blob object contained in commit `21682c1`.
4. GitHub's remote hook inspects all incoming pack objects, detecting that `21682c1` contained a blob exceeding 100 MB.

---

## 4. Fix Applied

1. Executed `git filter-branch` to rewrite the unpushed commit range (`origin/main..HEAD`), purging `resources/archive.zip` from all intermediate commit trees:
   ```bash
   git filter-branch --force --index-filter "git rm --cached --ignore-unmatch resources/archive.zip" --prune-empty origin/main..HEAD
   ```
2. Expired all reflogs and pruned dangling large packfile objects:
   ```bash
   Remove-Item -Path ".git\refs\original" -Recurse -Force
   git reflog expire --expire=now --all
   git gc --prune=now
   ```
3. Updated `.gitignore` to permanently exclude large archives and downloaded corpora:
   ```gitignore
   # Large test archives / raw corpora
   *.zip
   *.tar
   *.tar.gz
   fixtures/canterbury/
   resources/*.zip
   ```
4. Executed `git push origin main:main`, successfully synchronizing all 8 commits to GitHub.

---

## 5. Verification & Prevention

- Ran `git push origin main:main` -> Exited with code 0: `8c11274..894e24a  main -> main`.
- All automated unit tests in `pytest` verified green (39/39 passing).
- `.gitignore` now prevents any `.zip` or `.tar.gz` from being tracked in git staging.
