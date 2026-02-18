# Publishing Guide

## Python Package (PyPI)

### First Time Setup

1. **Install build tools:**
```bash
pip install build twine
```

2. **Configure PyPI credentials:**
```bash
# Create ~/.pypirc
[pypi]
username = your-username
password = your-password

[testpypi]
username = your-username
password = your-password
repository = https://test.pypi.org/legacy/
```

Or use environment variables:
```bash
export TWINE_USERNAME=your-username
export TWINE_PASSWORD=your-password
```

### Build and Publish

**Test PyPI (recommended first):**
```bash
cd a2a-protocol
python -m build
twine upload --repository testpypi dist/*
```

**PyPI (production):**
```bash
python -m build
twine upload dist/*
```

### Install from PyPI
```bash
pip install a2a-protocol
```

---

## npm Package

### First Time Setup

1. **Login to npm:**
```bash
npm login
```

2. **Or use token:**
```bash
# Add to ~/.npmrc
# //registry.npmjs.org/:_authToken=YOUR_TOKEN
```

### Build and Publish

```bash
cd typescript
npm install
npm run build
npm publish
```

### Install from npm
```bash
npm install @mentessaas/a2a-protocol
```

---

## Go Package

The Go package is automatically available via:

```bash
go get github.com/mentessaas/a2a-protocol/go/a2a
```

No manual publishing needed - Go modules work via GitHub.

---

## Rust Package

Not published to crates.io yet. To publish:

```bash
cd rust
cargo login
cargo publish
```

---

## Quick Publish Commands

```bash
# Python
cd a2a-protocol && python -m build && twine upload dist/*

# npm
cd typescript && npm run build && npm publish

# Go (automatic via GitHub)
# No command needed - works via go get

# Rust (optional)
cd rust && cargo publish
```
