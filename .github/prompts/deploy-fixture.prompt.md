---
description: Deploy OpenFixture plugin to KiCAD with automatic cache clearing and validation. Use when deploying changes, updating plugin, or troubleshooting stale imports.
---

# Deploy OpenFixture to KiCAD

Deploy the OpenFixture plugin to your KiCAD installation with automated cache management.

## Workflow

1. Check if `sync_to_kicad_config.ps1` exists
   - If missing, copy from template and prompt user to edit with their KiCAD path
   - If exists, validate it has proper path configuration

2. Deploy plugin (auto-clears Python cache):
   ```powershell
   .\sync_to_kicad.ps1
   ```
   - Automatically clears `__pycache__` directories and `.pyc` files
   - Copy all required files from `src/` to KiCAD plugins directory
   - Verify files copied successfully

3. Post-deployment validation:
   - Check that `openfixture.py` exists in plugins directory
   - Verify `openfixture_support/` subdirectory structure
   - List all deployed files with timestamps

4. Provide next steps:
   - Restart KiCAD to load the updated plugin
   - Access via `Tools → External Plugins → OpenFixture Generator`

## Error Handling

- **Config file missing**: Guide user to create from template
- **Permission errors**: Check KiCAD isn't running and blocking file access
- **Path not found**: Verify KiCAD installation directory

## Success Criteria

✅ All required files copied to KiCAD plugins directory
✅ Files copied to KiCAD plugins directory  
✅ Directory structure matches expected layout  
✅ No cache files remaining
