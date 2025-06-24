# GitHub Pages Setup Instructions

The GitHub Actions workflow is configured to automatically build and deploy the MkDocs documentation to GitHub Pages. The following steps complete the setup:

## 1. Enable GitHub Pages in Repository Settings

1. Go to the repository on GitHub: `https://github.com/lancereinsmith/trunk8`
2. Click on **Settings** tab
3. Scroll down to **Pages** in the left sidebar
4. Under **Source**, select **GitHub Actions**
5. Click **Save**

## 2. Commit and Push the Workflow

The workflow file is located at `.github/workflows/docs.yml`. The actions are triggered on a push of the repository to main.


## 3. Monitor the Deployment

1. Once pushed, to the **Actions** tab in the GitHub repository
2. There should be a "Documentation" workflow running
3. Once it completes successfully, the docs will be available at:
   `https://lancereinsmith.github.io/trunk8/`

## 4. Update Site URL

Update the `site_url` in `mkdocs.yml` to reflect the GitHub Pages URL:

```yaml
site_url: https://lancereinsmith.github.io/trunk8/
```

## Features of This Setup

- **Automatic deployment** on every push to main branch
- **Secure deployment** using GitHub's official Pages actions
- **Build artifacts** are properly handled
- **Git history** is preserved for the git-revision-date plugin
- **Concurrent deployment protection** to avoid conflicts

## Troubleshooting

If the deployment fails:

1. Check the Actions tab for error messages
2. Ensure all documentation files are properly formatted
3. Verify that the `docs` extra dependencies are installed correctly

Your documentation will be automatically updated every time you push changes to the `docs/` directory or `mkdocs.yml` file. 