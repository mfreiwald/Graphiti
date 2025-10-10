# Release Guide

This monorepo contains two independently versioned packages:
- **REST Server** (`graphiti-server/`)
- **Swift SDK** (`graphiti-swift/`)

## Versioning Strategy

We use [Semantic Versioning](https://semver.org/) (MAJOR.MINOR.PATCH) with package-specific prefixes:

- **Server releases**: `server/v1.0.0`, `server/v1.1.0`, etc.
- **Swift SDK releases**: `swift/v1.0.0`, `swift/v1.1.0`, etc.

This allows independent release cycles for each package.

## Release Process

### 1. REST Server Release

```bash
# 1. Update version in pyproject.toml
cd graphiti-server
# Edit pyproject.toml: version = "1.2.0"

# 2. Commit changes
git add pyproject.toml
git commit -m "chore(server): bump version to 1.2.0"
git push

# 3. Create and push tag
git tag server/v1.2.0
git push origin server/v1.2.0
```

**What happens:**
- GitHub Actions builds multi-arch Docker image (amd64, arm64)
- Publishes to GitHub Container Registry
- Creates GitHub Release with Docker pull instructions

**Docker image tags:**
- `ghcr.io/mfreiwald/Graphiti/graphiti-server:1.2.0`
- `ghcr.io/mfreiwald/Graphiti/graphiti-server:1.2`
- `ghcr.io/mfreiwald/Graphiti/graphiti-server:1`
- `ghcr.io/mfreiwald/Graphiti/graphiti-server:latest`

### 2. Swift SDK Release

```bash
# 1. No version file to update (SPM uses git tags)

# 2. Create and push tag
git tag swift/v1.2.0
git push origin swift/v1.2.0
```

**What happens:**
- GitHub Actions builds on macOS 26 and Linux (Swift 6.2)
- Runs tests on both platforms
- Generates documentation
- Creates GitHub Release with:
  - Source archive (`.zip`)
  - Documentation archive (`.tar.gz`)
  - Installation instructions

**Installation:**
Users add to their `Package.swift`:
```swift
dependencies: [
    .package(url: "https://github.com/mfreiwald/Graphiti", from: "1.2.0")
]
```

### 3. Manual Release (via GitHub UI)

Both workflows support manual triggering:

1. Go to **Actions** tab
2. Select workflow:
   - "Release REST Server" or
   - "Release Swift SDK"
3. Click **Run workflow**
4. Enter version (e.g., `1.2.0`)
5. Click **Run workflow**

## Version Bumping Guidelines

### MAJOR (x.0.0)
- Breaking API changes
- Removed endpoints/methods
- Changed response formats
- Incompatible updates

**Example:**
- Server: Remove deprecated endpoint
- Swift: Change method signatures

### MINOR (1.x.0)
- New features (backward compatible)
- New endpoints/methods
- New configuration options
- Deprecations (not removals)

**Example:**
- Server: Add new search endpoint
- Swift: Add new API methods

### PATCH (1.0.x)
- Bug fixes
- Documentation updates
- Performance improvements
- Security patches

**Example:**
- Server: Fix temperature configuration bug
- Swift: Fix memory leak

## Pre-release Versions

For testing before official release:

```bash
# Alpha
git tag server/v1.2.0-alpha.1
git tag swift/v1.2.0-alpha.1

# Beta
git tag server/v1.2.0-beta.1
git tag swift/v1.2.0-beta.1

# Release Candidate
git tag server/v1.2.0-rc.1
git tag swift/v1.2.0-rc.1
```

These create releases marked as "pre-release" on GitHub.

## Continuous Integration

### Pull Requests
Both packages are built and tested on every PR:
- **Server**: Docker build test
- **Swift**: macOS + Linux build and test

### Main Branch
On push to `main`:
- Server: Builds and pushes `latest` tag
- Swift: Builds and uploads documentation

## Checking Releases

### Server
```bash
# Check available versions
docker pull ghcr.io/mfreiwald/Graphiti/graphiti-server:latest

# List all tags
curl -H "Authorization: Bearer $GITHUB_TOKEN" \
  https://api.github.com/users/OWNER/packages/container/REPO%2Fgraphiti-server/versions
```

### Swift SDK
```bash
# List all tags
git ls-remote --tags https://github.com/mfreiwald/Graphiti | grep swift/

# View releases
open https://github.com/mfreiwald/Graphiti/releases
```

## Best Practices

1. **Always test before releasing**
   - Run tests locally
   - Test Docker image
   - Verify Swift package builds

2. **Write clear release notes**
   - Summarize changes
   - Highlight breaking changes
   - Include migration guide if needed

3. **Keep versions independent**
   - Server and Swift can have different versions
   - Only sync major versions if APIs change together

4. **Use semantic versioning strictly**
   - Makes it clear what changed
   - Helps users understand upgrade impact

5. **Tag from main branch**
   - Ensure all changes are merged
   - CI has passed
   - Code review complete

## Troubleshooting

### Release workflow failed
- Check Actions logs
- Verify tag format: `server/v1.0.0` or `swift/v1.0.0`
- Ensure version doesn't already exist

### Docker image not published
- Check GitHub token permissions
- Verify package visibility settings
- Check Registry settings in repo

### Swift package not found
- Verify tag is pushed to GitHub
- Check tag format: `swift/v1.0.0`
- Ensure repository is public or user has access

## Example Release Timeline

```
Day 1: Development
├── Feature branches merged to main
├── CI passes on main

Day 2: Prepare Release
├── Update CHANGELOG (if exists)
├── Update documentation
├── Test locally

Day 3: Release
├── Server: Tag server/v1.2.0
├── Swift: Tag swift/v1.0.5
├── Wait for CI to complete
├── Verify releases on GitHub
├── Test installation

Day 4: Announce
├── Update README if needed
├── Notify users
└── Monitor for issues
```
