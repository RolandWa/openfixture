---
description: Deploy OpenFixture plugin to KiCAD with automatic cache clearing and validation. Use when deploying changes, updating plugin, or troubleshooting stale imports.
---

# Deploy OpenFixture to KiCAD

Deploy the OpenFixture plugin to your KiCAD installation with automated cache management.

## Workflow

1. Check if `sync_to_kicad_config.ps1` exists
   - If missing, copy from template and prompt user to edit with their KiCAD path
   - If exists, validate it has proper path configuration

2. Run pre-deployment test:
   ```powershell
   .\test_functionality.ps1
   ```
   - If tests fail, report errors and halt deployment

3. Clear Python cache to prevent stale imports:
   - Delete `__pycache__` directories in both source and KiCAD plugin directories
   - Remove `.pyc` files

4. Deploy plugin:
   ```powershell
   .\sync_to_kicad.ps1
   ```
   - Copy all required files to KiCAD plugins directory
   - Verify files copied successfully

5. Post-deployment validation:
   - Check that `openfixture.py` exists in plugins directory
   - Verify `openfixture_support/` subdirectory structure
   - List all deployed files with timestamps

6. Provide next steps:
   - Restart KiCAD to load the updated plugin
   - Access via `Tools → External Plugins → OpenFixture Generator`

## Error Handling

- **Config file missing**: Guide user to create from template
- **Test failures**: Show specific test that failed and suggested fix
- **Permission errors**: Check KiCAD isn't running and blocking file access
- **Path not found**: Verify KiCAD installation directory

## Success Criteria

✅ All tests pass  
✅ Files copied to KiCAD plugins directory  
✅ Directory structure matches expected layout  
✅ No cache files remaining
