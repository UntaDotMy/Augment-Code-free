#!/usr/bin/env python3
"""
Release preparation script for AugmentCode Free.

This script helps prepare releases by:
1. Moving unreleased changes to a versioned section in CHANGELOG.md
2. Creating a new unreleased section
3. Updating version information
"""

import re
import sys
from datetime import datetime
from pathlib import Path


def update_changelog(version: str) -> bool:
    """
    Update CHANGELOG.md by moving unreleased changes to a versioned section.
    
    Args:
        version: The version number (e.g., "v1.2.3")
        
    Returns:
        bool: True if successful, False otherwise
    """
    changelog_path = Path("CHANGELOG.md")
    
    if not changelog_path.exists():
        print("❌ CHANGELOG.md not found")
        return False
    
    try:
        # Read current changelog
        with open(changelog_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Get current date
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        # Check if there's an unreleased section
        if "## [Unreleased]" not in content:
            print("⚠️ No unreleased section found in CHANGELOG.md")
            return False
        
        # Extract unreleased content
        unreleased_pattern = r"## \[Unreleased\]\s*\n(.*?)(?=\n## |\n---|\Z)"
        match = re.search(unreleased_pattern, content, re.DOTALL)
        
        if not match:
            print("⚠️ Could not extract unreleased content")
            return False
        
        unreleased_content = match.group(1).strip()
        
        if not unreleased_content:
            print("⚠️ No unreleased changes found")
            return False
        
        # Create new versioned section
        versioned_section = f"""## [{version}] - {current_date}

{unreleased_content}

"""
        
        # Create new unreleased section
        new_unreleased = """## [Unreleased]

### Added
- 

### Enhanced
- 

### Fixed
- 

### Technical
- 

"""
        
        # Replace the unreleased section with new unreleased + versioned sections
        new_content = re.sub(
            r"## \[Unreleased\].*?(?=\n## |\n---|\Z)",
            new_unreleased + versioned_section.rstrip(),
            content,
            flags=re.DOTALL
        )
        
        # Write updated changelog
        with open(changelog_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        
        print(f"✅ Updated CHANGELOG.md with version {version}")
        print(f"📅 Release date: {current_date}")
        return True
        
    except Exception as e:
        print(f"❌ Error updating changelog: {e}")
        return False


def main():
    """Main function."""
    if len(sys.argv) != 2:
        print("Usage: python scripts/prepare-release.py <version>")
        print("Example: python scripts/prepare-release.py v1.2.3")
        sys.exit(1)
    
    version = sys.argv[1]
    
    # Validate version format
    if not re.match(r"^v\d+\.\d+\.\d+", version):
        print("❌ Invalid version format. Use format: v1.2.3")
        sys.exit(1)
    
    print(f"🚀 Preparing release {version}")
    
    # Update changelog
    if update_changelog(version):
        print("✅ Release preparation completed")
        print(f"📋 Review CHANGELOG.md and commit the changes")
        print(f"🏷️ Then create and push tag: git tag {version} && git push origin {version}")
    else:
        print("❌ Release preparation failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
