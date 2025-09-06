# File: README.md
# Path: OurLibrary/Scripts/README.md  
# Standard: AIDEV-PascalCase-2.3
# Created: 2025-08-21
# Last Modified: 2025-08-21 05:08PM

# OurLibrary Scripts Directory

## Structure

This Scripts directory contains:

- **Project-specific scripts** - Custom utilities for this project only
- **Common/** - Symlinked shared utilities from BaseTree
  - `GitHub/` - GitHub integration scripts
  - `FinderDisplay/` - File search and display utilities  
  - `System/` - System management scripts
  - `Tools/` - General development tools

## Adding Project Scripts

Add your project-specific scripts directly to this folder:

```bash
Scripts/
├── my_custom_tool.py        # ← Project-specific
├── data_processor.py        # ← Project-specific  
├── deploy_ourlibrary.py     # ← Project-specific
└── Common/                  # ← Shared utilities (symlinked)
```

## Design Standard v2.3 Compliance

All scripts in this directory should follow **Design Standard v2.3**:

- Assume scripts may be symlinked
- Use PROJECT_TOOL pattern (work in current directory)
- Include context validation
- Document symlink behavior in headers

## Usage Examples

```bash
# Run shared GitHub utility
python Scripts/Common/GitHub/GitHubInitialCommit.py

# Run project-specific script  
python Scripts/my_custom_tool.py

# Both work correctly in project context!
```

---

*Project-specific scripts stay private to OurLibrary. Shared utilities are accessible but remain centrally managed.*