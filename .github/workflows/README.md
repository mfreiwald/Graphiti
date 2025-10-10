# GitHub Actions Workflows

This directory contains CI/CD workflows for the monorepo.

## Workflows

### Build Workflows (Continuous Integration)

#### `server-build.yml`
Builds and tests the REST Server on every push/PR.

**Triggers:**
- Push to `main` or `develop` (with server changes)
- Pull requests to `main` (with server changes)
- Manual dispatch

**Actions:**
- Builds Docker image (multi-arch: amd64, arm64)
- Pushes to GitHub Container Registry (on main/develop)
- Tags: `latest`, branch name, commit SHA
- Caches layers for faster builds

#### `swift-build.yml`
Builds and tests the Swift SDK on macOS and Linux.

**Triggers:**
- Push to `main` or `develop` (with Swift changes)
- Pull requests to `main` (with Swift changes)
- Manual dispatch

**Actions:**
- **macOS 26**: Build, test, generate docs
- **Linux (Swift 6.2)**: Build and test
- Upload documentation artifacts

### Release Workflows

#### `server-release.yml`
Releases a new version of the REST Server.

**Triggers:**
- Push tag: `server/v*.*.*` (e.g., `server/v1.2.0`)
- Manual dispatch with version input

**Actions:**
- Updates `pyproject.toml` version
- Builds and pushes Docker image with version tags
- Creates GitHub Release with Docker instructions

**Docker tags created:**
- `1.2.0` (full version)
- `1.2` (major.minor)
- `1` (major)
- `latest`

#### `swift-release.yml`
Releases a new version of the Swift SDK.

**Triggers:**
- Push tag: `swift/v*.*.*` (e.g., `swift/v1.2.0`)
- Manual dispatch with version input

**Actions:**
- Builds on macOS 26 and Linux (Swift 6.2)
- Runs full test suite
- Generates documentation
- Creates source and docs archives
- Creates GitHub Release

## Usage

### Development Workflow

1. **Work on feature branch**
   ```bash
   git checkout -b feature/my-feature
   # Make changes to graphiti-server/ or graphiti-swift/
   git push
   ```

2. **Create Pull Request**
   - CI automatically runs
   - Server: Docker build test
   - Swift: macOS + Linux build/test

3. **Merge to main**
   - CI builds and pushes `latest` images/artifacts

### Release Workflow

See [RELEASE.md](../RELEASE.md) for detailed release process.

**Quick release:**
```bash
# Server
git tag server/v1.2.0 && git push origin server/v1.2.0

# Swift SDK
git tag swift/v1.0.5 && git push origin swift/v1.0.5
```

## Path Filtering

Workflows only run when relevant files change:

- **Server workflows**: Trigger on `graphiti-server/**` changes
- **Swift workflows**: Trigger on `graphiti-swift/**` changes

This prevents unnecessary builds when only one package changes.

## Secrets Required

### `GITHUB_TOKEN`
Automatically provided by GitHub Actions. Used for:
- Pushing to GitHub Container Registry
- Creating releases

**Permissions required:**
- `contents: write` (for releases)
- `packages: write` (for Docker registry)

Configure in: **Settings → Actions → General → Workflow permissions**

## Monitoring

### Check workflow status
```bash
# View all workflows
gh workflow list

# View runs for a workflow
gh run list --workflow=server-build.yml

# View specific run
gh run view <run-id>
```

### Check Docker images
```bash
# List packages
gh api /user/packages/container/graphiti/graphiti-server/versions

# Pull image
docker pull ghcr.io/mfreiwald/Graphiti/graphiti-server:latest
```

## Troubleshooting

### Workflow not triggering
- Check path filters match changed files
- Verify branch name (main/develop)
- Check workflow file syntax

### Docker build fails
- Check Dockerfile syntax
- Verify base image exists
- Check dependencies in pyproject.toml

### Swift build fails
- Verify Swift 6.2 compatibility
- Check Package.swift syntax
- Test locally: `swift build && swift test`

### Release fails
- Check tag format: `server/v1.0.0` or `swift/v1.0.0`
- Verify version doesn't already exist
- Check permissions (contents: write)

## Local Testing

### Test Server build
```bash
cd graphiti-server
docker build -t test-server .
docker run --rm test-server python -c "import graphiti_server"
```

### Test Swift build
```bash
cd graphiti-swift
swift build -c release
swift test

# Linux test
docker run --rm -v $(pwd):/workspace -w /workspace swift:6.2 swift build
```

## Performance

### Build times
- **Server**: ~2-3 minutes (with cache)
- **Swift macOS**: ~5-7 minutes
- **Swift Linux**: ~3-5 minutes

### Caching
- Docker: Layer caching via GitHub Actions cache
- Swift: Package dependency caching

### Optimization tips
- Use `cache-from: type=gha` for Docker
- Minimize Dockerfile layers
- Use `.dockerignore` to exclude unnecessary files
