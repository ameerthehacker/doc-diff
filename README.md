# Document Diff Tool

A comprehensive template hydration and diff tracking system that allows you to:
- Hydrate templates with placeholder replacements
- Track user modifications with precise source mapping
- Generate git-like visual diffs showing exactly what changed

## Overview

This tool provides a complete workflow for template-based document generation with change tracking:

1. **Template Hydration**: Replace placeholders in templates with actual content
2. **Source Mapping**: Track where each piece of content came from
3. **User Modifications**: Allow users to modify the generated content
4. **Diff Analysis**: Precisely track what users changed and map it back to original templates

## Quick Start

### Step 1: Hydrate the Template

Run the template hydration to generate your base documents:

```bash
python3 main.py
```

**What this does:**
- Reads `playground/template.md` (contains placeholders like `[OVERVIEW]()` and `[TRANSFORMATION]()`)
- Replaces placeholders with actual content (data pipeline documentation in this example)
- Generates the following files in `out/` directory:

| File | Description |
|------|-------------|
| `generated-doc.md` | The hydrated document with placeholders replaced |
| `generated-doc.map` | Source map JSON tracking which parts came from which placeholders |

**Example template (`playground/template.md`):**
```markdown
# Introduction
[OVERVIEW]()

# Transformation Steps
[TRANSFORMATION]()
```

**Generated output** will have actual content replacing `[OVERVIEW]()` and `[TRANSFORMATION]()` placeholders.

### Step 2: Create User-Modified Version

1. Copy the generated document to create a user-modified version:
```bash
cp out/generated-doc.md out/generated-doc-user-modified.md
```

2. Edit `out/generated-doc-user-modified.md` with any changes you want:
   - Add new content
   - Modify existing text
   - Restructure sections
   - Insert comments or notes

**Example modifications:**
- Add personal comments like "you know I'm kind of a data engineer myself"
- Change technical terms or add explanations
- Insert new steps or modify existing ones

### Step 3: Run Diff Analysis

Analyze what changed between the generated and user-modified versions:

```bash
python3 diff.py
```

**What this does:**
- Compares `generated-doc.md` vs `generated-doc-user-modified.md`
- Maps changes back to original template placeholders using the source map
- Shows a beautiful git-like diff in the console with color coding:
  - 🟢 **Green**: Inserted text (`+added content`)
  - 🔴 **Red**: Removed text (`-deleted content`) 
  - 🟡 **Yellow**: Replaced text
- Generates detailed JSON report for programmatic use

**Output files:**

| File | Description |
|------|-------------|
| `diff-report.json` | Detailed JSON with all modifications, positions, and operations |

## Console Output

The diff analysis shows a comprehensive report:

```
=== DIFF REPORT ===

[1] Placeholder: [OVERVIEW]()
Operations: 1
  1. Insert ', you know I'm kind of a data engineer myself'

Original content
--------------------------------------------------
[OVERVIEW]()

Transformed Content
--------------------------------------------------
... (content before) ...
processing capabilities+, you know I'm kind of a data engineer myself, ensuring
... (content after) ...

=== SUMMARY ===
📊 Modified placeholders: 2
🔧 Total operations: 5
📈 Operation breakdown:
   insert: 2
   replace: 3
```

## JSON Report Structure

The `diff-report.json` contains programmatically usable diff data:

```json
{
  "total_modifications": 2,
  "modifications": [
    {
      "original_content": {
        "start": 15,
        "end": 27,
        "content": "[OVERVIEW]()"
      },
      "user_modifications": [
        {
          "operation": "insert",
          "position_in_generated": 225,
          "length": 0,
          "remove": "",
          "insert": ", you know I'm kind of a data engineer myself",
          "description": "Insert ', you know I'm kind of a data engineer myself'"
        }
      ]
    }
  ]
}
```

## Key Features

### 🎯 **Precise Tracking**
- Character-level precision for all modifications
- Maps every change back to original template placeholders
- Handles complex text insertions, deletions, and replacements

### 🎨 **Visual Diff Display**
- Git-like color coding in terminal
- Context-aware display showing surrounding content
- Clear operation descriptions for each change

### 🔧 **Apply-able Diffs**
- JSON contains exact positions and operations
- Operations sorted for safe sequential application
- Can reconstruct user modifications programmatically

### 📊 **Source Mapping**
- Full traceability from final document back to template
- Tracks which placeholders were modified by users
- Maintains position accuracy despite content changes

## File Structure

```
.
├── README.md
├── main.py                 # Template hydration engine
├── diff.py                 # Diff analysis tool
├── diff_display.py         # Console display utilities
├── playground/
│   └── template.md         # Your template with placeholders
└── out/                    # Generated files (created after running main.py)
    ├── generated-doc.md    # Hydrated template
    ├── generated-doc.map   # Source map
    ├── generated-doc-user-modified.md  # Your modified version
    └── diff-report.json    # Diff analysis results
```

## Use Cases

### 📝 **Document Template Systems**
- Generate contracts, reports, or documentation from templates
- Track user customizations and approvals
- Maintain audit trail of changes

### 🔄 **Content Management**
- Template-based content generation
- User personalization tracking
- Change review and approval workflows

### 🏗️ **Code Generation**
- Template-based code scaffolding
- Track developer modifications to generated code
- Understand deviation from templates

## Advanced Usage

### Custom Templates
1. Modify `playground/template.md` with your own placeholders
2. Update the replacement content in `main.py`
3. Run the hydration and diff workflow

### Integration
- Use the JSON output for automated processing
- Build approval workflows around the diff data
- Create dashboards showing template usage patterns

## Requirements

- Python 3.6+
- No external dependencies (uses only standard library)
- Terminal with ANSI color support for best visual experience

## Tips

- **Start small**: Begin with simple templates to understand the workflow
- **Use descriptive placeholders**: Make placeholder names clear (`[USER_NAME]()` vs `[PLACEHOLDER1]()`)
- **Test modifications**: Try different types of edits to see how they're tracked
- **Check the JSON**: The diff report contains detailed data for programmatic use

---

**Happy template diffing!** 🚀
