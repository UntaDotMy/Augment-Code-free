#!/usr/bin/env python3
"""
Release script for AugmentCode Free
Helps create releases with proper versioning
"""

import subprocess
import sys
import re
from pathlib import Path


def run_command(cmd, capture_output=True):
    """Run a command and return the result."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=capture_output, text=True, check=True)
        return result.stdout.strip() if capture_output else None
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {cmd}")
        print(f"Error: {e.stderr if capture_output else e}")
        return None


def get_latest_tag():
    """Get the latest git tag."""
    result = run_command("git describe --tags --abbrev=0 2>/dev/null")
    return result if result else "v0.0.0"


def parse_version(version_str):
    """Parse version string into major, minor, patch."""
    match = re.match(r'v?(\d+)\.(\d+)\.(\d+)', version_str)
    if match:
        return tuple(map(int, match.groups()))
    return (0, 0, 0)


def increment_version(version_tuple, increment_type):
    """Increment version based on type."""
    major, minor, patch = version_tuple
    
    if increment_type == "major":
        return (major + 1, 0, 0)
    elif increment_type == "minor":
        return (major, minor + 1, 0)
    elif increment_type == "patch":
        return (major, minor, patch + 1)
    else:
        raise ValueError(f"Invalid increment type: {increment_type}")


def format_version(version_tuple):
    """Format version tuple as string."""
    return f"v{version_tuple[0]}.{version_tuple[1]}.{version_tuple[2]}"


def get_commits_since_tag(tag):
    """Get commit messages since the given tag."""
    if tag == "v0.0.0":
        cmd = "git log --pretty=format:'%s'"
    else:
        cmd = f"git log {tag}..HEAD --pretty=format:'%s'"
    
    result = run_command(cmd)
    return result.split('\n') if result else []


def detect_version_type(commits):
    """Detect version increment type from commit messages."""
    commit_text = ' '.join(commits).lower()
    
    # Check for breaking changes or major updates
    if any(keyword in commit_text for keyword in ['breaking', 'major', 'breaking change', 'major update']):
        return "major"
    
    # Check for features or enhancements
    if any(keyword in commit_text for keyword in ['feat', 'feature', 'enhancement', 'add', 'new']):
        return "minor"
    
    # Default to patch for bug fixes and other changes
    return "patch"


def main():
    """Main release function."""
    print("🚀 AugmentCode Free Release Tool")
    print("=" * 40)
    
    # Check if we're in a git repository
    if not Path(".git").exists():
        print("❌ Error: Not in a git repository")
        sys.exit(1)
    
    # Get current information
    latest_tag = get_latest_tag()
    current_version = parse_version(latest_tag)
    commits = get_commits_since_tag(latest_tag)
    
    print(f"📋 Current version: {latest_tag}")
    print(f"📝 Commits since last tag: {len(commits)}")
    
    if len(commits) == 0 and latest_tag != "v0.0.0":
        print("⚠️  No changes since last tag. Nothing to release.")
        return
    
    # Auto-detect version type
    auto_type = detect_version_type(commits)
    print(f"🤖 Auto-detected increment: {auto_type}")
    
    # Show recent commits
    if commits:
        print("\n📝 Recent commits:")
        for i, commit in enumerate(commits[:5]):
            print(f"  {i+1}. {commit}")
        if len(commits) > 5:
            print(f"  ... and {len(commits) - 5} more")
    
    # Ask user for confirmation or override
    print(f"\n🎯 Version increment options:")
    print(f"  1. major (+1.0.0) - Breaking changes, major updates")
    print(f"  2. minor (+0.1.0) - New features, enhancements")
    print(f"  3. patch (+0.0.1) - Bug fixes, small changes")
    print(f"  4. auto ({auto_type}) - Use auto-detected type")
    
    choice = input(f"\nSelect increment type (1-4, default: 4): ").strip()
    
    if choice == "1":
        increment_type = "major"
    elif choice == "2":
        increment_type = "minor"
    elif choice == "3":
        increment_type = "patch"
    else:
        increment_type = auto_type
    
    # Calculate new version
    new_version_tuple = increment_version(current_version, increment_type)
    new_version = format_version(new_version_tuple)
    
    print(f"\n🎉 New version will be: {new_version} ({increment_type})")
    
    # Confirm release
    confirm = input("Create release? (y/N): ").strip().lower()
    if confirm not in ['y', 'yes']:
        print("❌ Release cancelled")
        return
    
    # Create and push tag
    print(f"\n🏷️  Creating tag {new_version}...")
    
    # Configure git if needed
    run_command('git config user.name "Release Script" 2>/dev/null', capture_output=False)
    run_command('git config user.email "release@local" 2>/dev/null', capture_output=False)
    
    # Create tag
    tag_message = f"Release {new_version} ({increment_type})"
    if not run_command(f'git tag -a "{new_version}" -m "{tag_message}"'):
        print("❌ Failed to create tag")
        return
    
    # Push tag
    if not run_command(f'git push origin "{new_version}"'):
        print("❌ Failed to push tag")
        return
    
    print(f"✅ Successfully created and pushed tag {new_version}")
    print(f"🚀 GitHub Actions will automatically build and create the release")
    print(f"📦 Check the Actions tab for build progress")


if __name__ == "__main__":
    main()
