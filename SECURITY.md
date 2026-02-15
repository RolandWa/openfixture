# Security Guidelines

## 🔒 Overview

This document outlines security practices for the OpenFixture project to prevent sensitive personal data from being committed to the repository.

## ⚠️ Security Issues Addressed

### 1. Personal File Paths
**Issue**: Hardcoded user-specific paths in scripts containing:
- Usernames
- Company names
- OneDrive/personal directory structures

**Solution**: Configuration template system with external config files.

### 2. Configuration Files
Personal configuration files are now excluded from version control using `.gitignore`.

---

## 🛡️ Security Best Practices

### For Users

#### Setting Up Personal Configuration

1. **Copy the template file**:
   ```powershell
   Copy-Item sync_to_kicad_config.ps1.template sync_to_kicad_config.ps1
   ```

2. **Edit with your personal paths**:
   ```powershell
   notepad sync_to_kicad_config.ps1
   ```

3. **Never commit the config file**:
   - The `.gitignore` file automatically excludes `sync_to_kicad_config.ps1`
   - This keeps your personal paths private

#### Configuration File Location

Your personal config file should contain:
```powershell
# Your personal KiCad plugins directory
$PluginsDir = "C:\Users\YOUR_USERNAME\AppData\Roaming\kicad\9.0\3rdparty\plugins"
```

**DO NOT**:
- ❌ Commit `sync_to_kicad_config.ps1`
- ❌ Hardcode personal paths in tracked scripts
- ❌ Include company-specific directory structures
- ❌ Share config files with embedded credentials

**DO**:
- ✅ Use the template system
- ✅ Keep config files local only
- ✅ Use environment variables when possible
- ✅ Document config requirements in templates

---

## 📋 Files Excluded from Git

The `.gitignore` file prevents the following from being committed:

### Configuration Files (Security Critical)
- `sync_to_kicad_config.ps1` - Personal KiCad paths
- `*_config_local.ps1` - Any local configuration
- `*_local.toml` - Local TOML configurations
- `*.local.*` - Any file marked as local

### Personal Data
- User-specific paths and settings
- IDE configurations (`.vscode/`, `.idea/`)
- System files (`Thumbs.db`, `.DS_Store`)

### Generated Files
- Python bytecode (`__pycache__/`, `*.pyc`)
- Build artifacts (`build/`, `dist/`)
- Fixture output directories (`fixture*/`)
- DXF exports (except examples)
- Log files (`*.log`)

### Temporary/Backup Files
- `*Copy*.py`, `*Copy*.bat`, etc.
- `*_backup.*`, `*_old.*`
- `*.bak`, `*.tmp`

---

## 🔍 Security Review Checklist

Before committing changes:

- [ ] No personal file paths in committed code
- [ ] No usernames or company-specific paths
- [ ] Configuration templates updated (`.template` files)
- [ ] `.gitignore` covers new sensitive file types
- [ ] No credentials or API keys
- [ ] No personal email addresses in code
- [ ] Documentation uses generic examples

---

## 🛠️ Auto-Detection Features

The `sync_to_kicad.ps1` script now includes:

1. **Config file detection**: Checks for `sync_to_kicad_config.ps1`
2. **Auto-path detection**: Attempts to find KiCad plugins directory automatically
3. **Helpful error messages**: Guides users to create config if needed

### Default Search Paths

The script searches these locations automatically:
- `%APPDATA%\kicad\9.0\3rdparty\plugins` (Windows)
- `%APPDATA%\kicad\8.0\3rdparty\plugins` (Windows)
- `~/.local/share/kicad/9.0/3rdparty/plugins` (Linux)
- `~/.local/share/kicad/8.0/3rdparty/plugins` (Linux)

---

## 📝 For Contributors

### Adding New Configuration Options

When adding features that require personal paths:

1. **Add to template**: Update `sync_to_kicad_config.ps1.template`
2. **Document requirement**: Add to this SECURITY.md file
3. **Update .gitignore**: Add exclusion patterns if needed
4. **Use relative paths**: When possible, use `$PSScriptRoot` or `$RepoDir`

### Example: Secure Configuration Pattern

```powershell
# BAD - Hardcoded personal path
$MyPath = "C:\Users\JohnDoe\Documents\Project"

# GOOD - External configuration
if (Test-Path $ConfigFile) {
    . $ConfigFile  # Load $MyPath from here
} else {
    # Use generic default or auto-detect
    $MyPath = Join-Path $PSScriptRoot "default_location"
}
```

---

## 🚨 Reporting Security Issues

If you find sensitive data committed to the repository:

1. **Do not create a public issue**
2. **Contact the maintainers privately**
3. **Document the issue**: What data, where found
4. **Suggest fix**: How to prevent future occurrences

For this project:
- Check commit history for exposed data
- Use `git filter-branch` or BFG Repo-Cleaner if needed
- Update `.gitignore` to prevent recurrence

---

## ✅ Verification

### Check for Personal Data

```powershell
# Search for personal usernames
git grep -i "YourUsername"

# Search for company names
git grep -i "CompanyName"

# Check for Windows user paths
git grep "C:\\Users\\"

# List what would be committed
git status --ignored
```

### Verify .gitignore

```powershell
# Test if sensitive files are ignored
git check-ignore sync_to_kicad_config.ps1

# Should output: sync_to_kicad_config.ps1
```

---

## 📚 Additional Resources

- [Git Best Practices](https://git-scm.com/book/en/v2/Git-Tools-Rewriting-History)
- [GitHub Security Best Practices](https://docs.github.com/en/code-security)
- [Removing Sensitive Data from Git](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)

---

**Last Updated**: February 15, 2026  
**Version**: 2.0
