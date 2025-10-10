# GitHub Actions Setup Summary

## ✅ Was wurde erstellt

### 1. Build Workflows (CI)

#### `.github/workflows/server-build.yml`
- **Trigger**: Push/PR mit Server-Änderungen
- **Aktionen**:
  - Docker Multi-Arch Build (amd64, arm64)
  - Push zu GitHub Container Registry
  - Layer Caching für schnellere Builds
  - Test-Image auf PRs

#### `.github/workflows/swift-build.yml`
- **Trigger**: Push/PR mit Swift-Änderungen
- **Aktionen**:
  - macOS 26 Build & Test
  - Linux (Swift 6.2) Build & Test
  - Dokumentation generieren
  - Artifacts hochladen

### 2. Release Workflows

#### `.github/workflows/server-release.yml`
- **Trigger**: Tag `server/v*.*.*` oder manuell
- **Aktionen**:
  - Version in `pyproject.toml` aktualisieren
  - Multi-Arch Docker Image bauen
  - Zu GHCR pushen mit Tags: `1.0.0`, `1.0`, `1`, `latest`
  - GitHub Release erstellen

#### `.github/workflows/swift-release.yml`
- **Trigger**: Tag `swift/v*.*.*` oder manuell
- **Aktionen**:
  - macOS & Linux Build/Test
  - Dokumentation generieren
  - Source & Docs Archive erstellen
  - GitHub Release erstellen

### 3. Dokumentation

- **`.github/RELEASE.md`**: Kompletter Release-Guide
- **`.github/workflows/README.md`**: Workflow-Übersicht
- **Haupt-README.md**: Update mit Release-Infos

## 🎯 Versioning-Strategie

### Unabhängige Versionen pro Package

```
server/v1.0.0  → REST Server Version 1.0.0
swift/v1.0.0   → Swift SDK Version 1.0.0
```

### Semantic Versioning

- **MAJOR**: Breaking changes
- **MINOR**: Neue Features (backward compatible)
- **PATCH**: Bug fixes

## 🚀 So verwendest du es

### 1. Entwicklung

```bash
# Feature Branch erstellen
git checkout -b feature/my-feature

# Änderungen in graphiti-server/ oder graphiti-swift/
git add .
git commit -m "feat: add new feature"
git push

# Pull Request erstellen
# → CI läuft automatisch
```

### 2. Release erstellen

#### Server Release

```bash
# 1. Version in pyproject.toml aktualisieren
cd graphiti-server
# Edit: version = "1.2.0"

# 2. Committen
git add pyproject.toml
git commit -m "chore(server): bump to 1.2.0"
git push

# 3. Tag erstellen
git tag server/v1.2.0
git push origin server/v1.2.0

# ✅ GitHub Actions erstellt automatisch:
# - Docker Image: ghcr.io/mfreiwald/Graphiti/graphiti-server:1.2.0
# - GitHub Release mit Docs
```

#### Swift SDK Release

```bash
# 1. Tag erstellen (keine Version-File nötig)
git tag swift/v1.2.0
git push origin swift/v1.2.0

# ✅ GitHub Actions erstellt automatisch:
# - Source Archive (.zip)
# - Documentation Archive (.tar.gz)
# - GitHub Release
```

### 3. Verwendung der Releases

#### Server nutzen

```bash
# Latest Version
docker pull ghcr.io/mfreiwald/Graphiti/graphiti-server:latest

# Spezifische Version
docker pull ghcr.io/mfreiwald/Graphiti/graphiti-server:1.2.0

# Starten
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=sk-... \
  -e NEO4J_URI=bolt://neo4j:7687 \
  ghcr.io/mfreiwald/Graphiti/graphiti-server:1.2.0
```

#### Swift SDK nutzen

```swift
// Package.swift
dependencies: [
    .package(url: "https://github.com/mfreiwald/Graphiti", from: "1.2.0")
]
```

## ⚙️ Repository-Setup nötig

### 1. GitHub Packages aktivieren

**Settings → Actions → General**
- ✅ Workflow permissions: **Read and write permissions**
- ✅ Allow GitHub Actions to create and approve pull requests

### 2. Secrets (optional)

Die `GITHUB_TOKEN` wird automatisch bereitgestellt.

Für Custom Registry:
```
Settings → Secrets → Actions
DOCKER_USERNAME=...
DOCKER_PASSWORD=...
```

### 3. Package Visibility

**Packages → graphiti-server → Package settings**
- Setze Visibility auf **Public** (oder Private je nach Bedarf)

## 📊 Workflow-Übersicht

```
┌─────────────────────────────────────────────────────────┐
│                    Development                           │
└──────────────┬──────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────┐
│  Push/PR → Build Workflows (CI)                         │
│  • server-build.yml → Docker Build & Test               │
│  • swift-build.yml  → macOS + Linux Build & Test        │
└──────────────┬──────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────┐
│  Merge to main → Deploy latest                          │
│  • Docker: ghcr.io/.../graphiti-server:latest           │
│  • Docs: Artifacts uploaded                             │
└──────────────┬──────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────┐
│  Tag push → Release Workflows                           │
│  • server/v1.0.0 → server-release.yml                   │
│  • swift/v1.0.0  → swift-release.yml                    │
└──────────────┬──────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────┐
│  GitHub Release + Docker Images/Artifacts               │
│  • Docker: versioned tags (1.0.0, 1.0, 1, latest)       │
│  • Swift: Source + Docs archives                        │
└─────────────────────────────────────────────────────────┘
```

## 🔍 Monitoring

### Check Workflow Status

```bash
# GitHub CLI
gh workflow list
gh run list --workflow=server-build.yml
gh run view <run-id>

# Web
https://github.com/mfreiwald/Graphiti/actions
```

### Check Releases

```bash
# Server releases
gh release list --repo mfreiwald/Graphiti | grep server

# Swift releases
gh release list --repo mfreiwald/Graphiti | grep swift
```

### Check Docker Images

```bash
# List versions
gh api /users/OWNER/packages/container/REPO%2Fgraphiti-server/versions

# Pull & test
docker pull ghcr.io/mfreiwald/Graphiti/graphiti-server:latest
docker run --rm ghcr.io/mfreiwald/Graphiti/graphiti-server:latest --version
```

## 🎨 Best Practices

### 1. Branch Protection
- Require PR reviews
- Require CI to pass
- No force push to main

### 2. Release Checklist
- [ ] Tests lokal laufen
- [ ] CHANGELOG aktualisiert (optional)
- [ ] Version-Nummer korrekt
- [ ] Tag-Format: `server/v1.0.0` oder `swift/v1.0.0`
- [ ] CI ist grün auf main

### 3. Version Bumping
- Bug fix: `1.0.0` → `1.0.1`
- New feature: `1.0.0` → `1.1.0`
- Breaking change: `1.0.0` → `2.0.0`

### 4. Pre-Release Testing
```bash
# Test mit alpha/beta tags
git tag server/v1.2.0-beta.1
git push origin server/v1.2.0-beta.1
```

## 🐛 Troubleshooting

### Build schlägt fehl
- Logs in Actions Tab anschauen
- Lokal testen: `docker build` / `swift build`
- Dependencies prüfen

### Docker Push schlägt fehl
- Token permissions prüfen
- Package visibility prüfen
- Registry settings prüfen

### Release nicht sichtbar
- Tag-Format prüfen: `server/v1.0.0`
- Workflow-Logs anschauen
- Permissions prüfen (contents: write)

## 📝 Anpassungen

### mfreiwald/Graphiti ersetzen

In allen Files ersetzen:
```bash
# Find & Replace
find . -type f -name "*.yml" -o -name "*.md" | xargs sed -i '' 's/OWNER\/REPO/dein-username\/dein-repo/g'
```

### Custom Registry (statt GHCR)

Edit workflows, ersetze:
```yaml
env:
  REGISTRY: docker.io  # oder dein Registry
  IMAGE_NAME: username/graphiti-server
```

### Custom Branches

Edit workflows, ersetze:
```yaml
branches: [main, develop]
# zu:
branches: [master, dev, staging]
```

## ✨ Was kommt als nächstes?

Optional hinzufügen:
- [ ] Code coverage reporting
- [ ] Security scanning (Dependabot, Snyk)
- [ ] Performance benchmarks
- [ ] Automated CHANGELOG generation
- [ ] Slack/Discord notifications
- [ ] Deploy to staging/production

---

**Fertig!** 🎉 Das Mono-Repo ist jetzt vollständig mit CI/CD ausgestattet.
