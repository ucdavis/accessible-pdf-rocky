# Codecov Setup Instructions

## 1. Sign up for Codecov

1. Go to [codecov.io](https://codecov.io)
2. Sign in with your GitHub account
3. Authorize Codecov to access your repositories

## 2. Add your repository

1. Once logged in, click "Add new repository" or navigate to your organization
2. Find and select the `accessible-pdf-rocky` repository
3. Codecov will provide you with a repository upload token

## 3. Add CODECOV_TOKEN to GitHub Secrets

1. Go to your GitHub repository: <https://github.com/YOUR_USERNAME/accessible-pdf-rocky>
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `CODECOV_TOKEN`
5. Value: Paste the token from Codecov
6. Click **Add secret**

## 4. Verify the setup

1. Push your changes to trigger the CI workflow
2. Wait for the workflow to complete
3. Visit your Codecov dashboard to see the coverage reports

## What's configured

### Coverage uploads

- **Controller**: Python coverage from pytest (XML format)
- **HPC Runner**: Python coverage from pytest (XML format)
- **Frontend**: JavaScript/TypeScript coverage from Vitest (JSON format)
- **Workers**: JavaScript/TypeScript coverage from Vitest (JSON format)

### Flags

Each component uploads with its own flag, allowing you to track coverage per component:

- `controller`
- `hpc_runner`
- `frontend`
- `workers`

### Configuration

The `codecov.yml` file configures:

- Component management for separate tracking of each module
- Coverage status checks with 1% threshold
- PR comments with detailed coverage breakdown
- Flags for filtering coverage by component

## Optional: Add Codecov badge to README

Add this to your main README.md:

```markdown
[![codecov](https://codecov.io/gh/YOUR_USERNAME/accessible-pdf-rocky/branch/main/graph/badge.svg)](https://codecov.io/gh/YOUR_USERNAME/accessible-pdf-rocky)
```

Replace `YOUR_USERNAME` with your GitHub username or organization name.
