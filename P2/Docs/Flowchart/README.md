# AndyLibrary Flowchart Documentation

This directory contains all flowchart-related files for the AndyLibrary project, organized by file type and purpose.

## Directory Structure

```
Docs/Flowchart/
├── README.md                    # This file
├── HTML/                        # Interactive HTML flowcharts
│   └── AndyLibrary_Fixed_Registration_Process.html
├── Mermaid/                     # Mermaid source files (.mmd)
│   └── AndyLibrary_Fixed_Registration_Process.mmd
├── Images/                      # Generated images (PNG, SVG exports)
│   └── AndyLibrary_Process_Flowchart.png
├── Documentation/               # Supporting documentation
│   ├── AndyLibrary_Process_Flowchart.md
│   ├── USER_FLOW_DIAGRAM.md
│   ├── VISUAL_USER_FLOW_CHART.md
│   ├── AndyLibrary_User_Flow_Documentation.md
│   └── AndyLibrary_Executive_Summary.md
└── Archive/                     # Deprecated/older versions
    ├── AndyLibrary_Detailed_Registration_Process.html
    ├── AndyLibrary_Enhanced_Professional_Flowchart.html
    ├── AndyLibrary_Interactive_Professional_Flowchart.html
    └── [other deprecated files]
```

## Active Files

### Current Production Flowchart
- **HTML**: `HTML/AndyLibrary_Fixed_Registration_Process.html`
- **Mermaid Source**: `Mermaid/AndyLibrary_Fixed_Registration_Process.mmd`

This is the latest working version with:
- ✅ Clean Mermaid syntax (no parsing errors)
- ✅ Interactive zoom/pan functionality
- ✅ SVG/PNG export capabilities
- ✅ Comprehensive registration process details
- ✅ Professional styling for management presentations

## Features

### Interactive HTML Flowchart Features
- **Zoom/Pan**: Navigate large diagrams easily
- **Export Options**: Download as SVG or PNG
- **Professional Styling**: Management-ready presentation quality
- **Detailed Process Documentation**: Complete registration workflow

### Process Coverage
- User authentication flow
- Registration form validation (client & server-side)
- Email verification system
- Database operations
- Error handling and recovery
- SMTP configuration details

## Usage

### Viewing the Flowchart
Open `HTML/AndyLibrary_Fixed_Registration_Process.html` in any modern web browser.

### Regenerating Files
Run the Python script from the project root:
```bash
python create_fixed_registration_flowchart.py
```

### Editing Mermaid Source
Edit `Mermaid/AndyLibrary_Fixed_Registration_Process.mmd` and regenerate the HTML file.

## File Naming Convention

- **Active files**: Clear, descriptive names without version numbers
- **Archive files**: Original names preserved for reference
- **Generated files**: Organized by type (HTML, Mermaid, Images, etc.)

## Maintenance Notes

- Keep only the latest working version in main directories
- Archive deprecated versions for reference
- Update this README when adding new flowcharts
- Maintain consistent naming conventions