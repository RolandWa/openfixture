# Deploy Unified Repository Files to KiCAD-Plugin Repository
# Copies all repository-related files to the separate repository location
#
# Date: February 20, 2026

param(
    [string]$TargetRepo = "..\KiCAD-Plugin",
    [switch]$DryRun = $false
)

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Deploy to KiCAD-Plugin Repository" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$ErrorActionPreference = "Stop"

# Check if target exists
if (-not (Test-Path $TargetRepo)) {
    Write-Host "❌ Target repository not found: $TargetRepo" -ForegroundColor Red
    Write-Host "`nPlease clone the repository first:" -ForegroundColor Yellow
    Write-Host "  git clone https://github.com/RolandWa/KiCAD-Plugin.git" -ForegroundColor White
    Write-Host "`nOr specify correct path with -TargetRepo parameter" -ForegroundColor Yellow
    exit 1
}

Write-Host "Target: $TargetRepo" -ForegroundColor Yellow
if ($DryRun) {
    Write-Host "Mode: DRY RUN (no files will be copied)" -ForegroundColor Yellow
} else {
    Write-Host "Mode: LIVE (files will be copied)" -ForegroundColor Green
}
Write-Host ""

# Define files and directories to copy
$FilesToCopy = @(
    # Core repository files
    @{
        Source = "kicad-repository.json"
        Target = "kicad-repository.json"
        Description = "Main repository index"
    },
    @{
        Source = "REPOSITORY_README.md"
        Target = "README.md"
        Description = "Repository README (renamed)"
    },
    @{
        Source = "REPOSITORY_SETUP.md"
        Target = "REPOSITORY_SETUP.md"
        Description = "Maintenance guide"
    },
    @{
        Source = "DEPLOYMENT_GUIDE.md"
        Target = "DEPLOYMENT_GUIDE.md"
        Description = "Deployment instructions"
    },
    @{
        Source = "SETUP_COMPLETE.md"
        Target = "SETUP_COMPLETE.md"
        Description = "Setup summary"
    },
    @{
        Source = "PCM_SETUP.md"
        Target = "docs/PCM_SETUP.md"
        Description = "PCM installation guide"
    },
    @{
        Source = "PCM_QUICKREF.md"
        Target = "docs/PCM_QUICKREF.md"
        Description = "Quick reference"
    }
)

# Directories to copy
$DirectoriesToCopy = @(
    @{
        Source = "packages"
        Target = "packages"
        Description = "Plugin metadata"
    },
    @{
        Source = "scripts"
        Target = "scripts"
        Description = "Helper scripts"
    },
    @{
        Source = "resources"
        Target = "resources"
        Description = "Icons and resources"
    }
)

# Copy individual files
Write-Host "📋 Copying files..." -ForegroundColor Yellow
$FileCopyCount = 0

foreach ($file in $FilesToCopy) {
    $sourcePath = $file.Source
    $targetPath = Join-Path $TargetRepo $file.Target
    
    if (Test-Path $sourcePath) {
        Write-Host "  ✅ $($file.Description)" -ForegroundColor Green
        Write-Host "     $sourcePath → $($file.Target)" -ForegroundColor Gray
        
        if (-not $DryRun) {
            # Create target directory if needed
            $targetDir = Split-Path $targetPath -Parent
            if ($targetDir -and -not (Test-Path $targetDir)) {
                New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
            }
            
            Copy-Item $sourcePath $targetPath -Force
        }
        $FileCopyCount++
    } else {
        Write-Host "  ⚠️  Skipped: $($file.Description) (not found)" -ForegroundColor Yellow
        Write-Host "     $sourcePath" -ForegroundColor Gray
    }
}

# Copy directories
Write-Host "`n📁 Copying directories..." -ForegroundColor Yellow
$DirCopyCount = 0

foreach ($dir in $DirectoriesToCopy) {
    $sourcePath = $dir.Source
    $targetPath = Join-Path $TargetRepo $dir.Target
    
    if (Test-Path $sourcePath) {
        $fileCount = (Get-ChildItem $sourcePath -Recurse -File).Count
        Write-Host "  ✅ $($dir.Description) ($fileCount files)" -ForegroundColor Green
        Write-Host "     $sourcePath → $($dir.Target)" -ForegroundColor Gray
        
        if (-not $DryRun) {
            # Remove target directory if it exists
            if (Test-Path $targetPath) {
                Remove-Item $targetPath -Recurse -Force
            }
            
            # Copy directory
            Copy-Item $sourcePath $targetPath -Recurse -Force
        }
        $DirCopyCount++
    } else {
        Write-Host "  ⚠️  Skipped: $($dir.Description) (not found)" -ForegroundColor Yellow
        Write-Host "     $sourcePath" -ForegroundColor Gray
    }
}

# Create additional structure files if needed
Write-Host "`n📝 Creating additional files..." -ForegroundColor Yellow

# Create .gitignore if it doesn't exist
$gitignorePath = Join-Path $TargetRepo ".gitignore"
if (-not (Test-Path $gitignorePath) -and -not $DryRun) {
    $gitignoreContent = @"
# Build artifacts
dist/
*.zip
!examples/*.zip

# Python
__pycache__/
*.py[cod]
*.so
.Python

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Personal config
*_config_local.*
*.local.*
sync_to_kicad_config.ps1

# Logs
*.log
"@
    $gitignoreContent | Set-Content $gitignorePath -Encoding UTF8
    Write-Host "  ✅ Created .gitignore" -ForegroundColor Green
} else {
    Write-Host "  ℹ️  .gitignore already exists" -ForegroundColor Gray
}

# Summary
Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "📊 Summary" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Cyan

Write-Host "  Files copied: $FileCopyCount" -ForegroundColor White
Write-Host "  Directories copied: $DirCopyCount" -ForegroundColor White
Write-Host "  Target: $TargetRepo" -ForegroundColor White

if ($DryRun) {
    Write-Host "`n⚠️  DRY RUN - No files were actually copied" -ForegroundColor Yellow
    Write-Host "   Run without -DryRun to perform actual copy" -ForegroundColor Gray
} else {
    Write-Host "`n✅ Deployment complete!" -ForegroundColor Green
    
    Write-Host "`n📋 Next steps:" -ForegroundColor Cyan
    Write-Host "  1. cd $TargetRepo" -ForegroundColor White
    Write-Host "  2. Review copied files" -ForegroundColor White
    Write-Host "  3. git add ." -ForegroundColor White
    Write-Host "  4. git commit -m 'Initial repository setup'" -ForegroundColor White
    Write-Host "  5. git push origin main" -ForegroundColor White
    Write-Host ""
    
    Write-Host "📚 Documentation:" -ForegroundColor Cyan
    Write-Host "  - README.md           - Repository overview" -ForegroundColor White
    Write-Host "  - DEPLOYMENT_GUIDE.md - How to build and release plugins" -ForegroundColor White
    Write-Host "  - REPOSITORY_SETUP.md - How to maintain and add plugins" -ForegroundColor White
    Write-Host ""
}

# Show repository structure
Write-Host "📁 Repository structure:" -ForegroundColor Cyan
Write-Host @"

KiCAD-Plugin/
├── README.md                      # Repository homepage
├── kicad-repository.json          # Main PCM index
├── REPOSITORY_SETUP.md            # Maintenance guide
├── DEPLOYMENT_GUIDE.md            # Deployment guide
├── SETUP_COMPLETE.md              # Setup summary
│
├── docs/
│   ├── PCM_SETUP.md              # PCM installation guide
│   └── PCM_QUICKREF.md           # Quick reference
│
├── packages/
│   ├── openfixture/
│   │   ├── metadata.json         # OpenFixture metadata
│   │   ├── icon.png              # Plugin icon
│   │   └── README.md             # Plugin docs
│   │
│   └── emc_auditor/
│       ├── metadata.json         # EMC Auditor metadata
│       ├── icon.png              # Plugin icon
│       └── README.md             # Plugin docs
│
├── scripts/
│   └── add_new_plugin.ps1        # Helper to add plugins
│
└── .gitignore                     # Git exclusions

"@ -ForegroundColor Gray

Write-Host ""
