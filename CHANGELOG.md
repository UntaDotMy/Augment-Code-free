# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- 

### Enhanced
- 

### Fixed
- 

### Technical
- 

## [v1.2.2] - 2025-06-17

### Added
-

### Enhanced
-

### Fixed
-

### Technical
-
## [v1.2.3] - 2025-06-17

### Added
- 🌐 **Global Storage Path Display** - Added global storage path to system information panel
  - Shows global storage directory path for all detected VSCode-based IDEs
  - Includes path in both regular system info and detected IDEs display
  - Added translation support for "Global Storage Path" in English and Chinese
  - Uses globe icon (🌐) to distinguish from other storage paths

### Enhanced
- 🤖 **Complete Automation Workflow** - Enhanced automation to include global storage cleaning
  - Automation now cleans both workspace storage AND global storage directories
  - Fixed incomplete automation that was causing "2 error(s)" in workflow completion
  - Added comprehensive progress reporting for all storage cleaning operations
  - Updated automation descriptions to reflect complete storage cleaning coverage

### Fixed
- 🔧 **IDE Detector Bug** - Fixed missing global_storage_path in IDE information
  - Global storage path was being detected but lost during IDE info serialization
  - Added global_storage_path to IDEInfo.to_dict() method for proper data persistence
  - Ensures automation workflow has access to all required storage paths
- 🎨 **UI Progress Reporting** - Fixed missing global storage results in automation display
  - Added global storage cleaning results to automation progress dialogs
  - Updated result display functions to show all storage operations
  - Enhanced translation coverage for global storage progress messages

### Technical
- 🏗️ **API Enhancement** - Added global storage path to system information API
- 🌐 **Translation Updates** - Added missing translation keys for global storage operations
- 📊 **Progress Display** - Enhanced JavaScript functions to handle global storage results
- 🔧 **Import Updates** - Added clean_global_storage import to automation module

## [v1.2.2] - 2025-06-17

### Added
- 

### Enhanced
- 

### Fixed
- 

### Technical
-
## [v1.2.1] - 2025-06-17

### Fixed
- 🔧 **GitHub Actions Workflow** - Fixed YAML syntax error in build.yml
  - Resolved line 206 syntax issue with changelog extraction
  - Simplified Python script approach to avoid YAML conflicts
  - Ensured proper workflow execution for auto-release system
## [v1.2.1] - 2025-06-17

### Added
- 🧹 **Simplified Architecture** - Removed unnecessary account information features
  - Focused exclusively on Augment-related data cleaning operations
  - Eliminated external API dependencies for better reliability
  - Streamlined user interface without account display sections

### Enhanced
- 🎯 **Core Functionality Focus** - Concentrated on essential IDE cleaning operations
  - Improved application startup performance by removing account loading
  - Cleaner header layout without account information clutter
  - Better resource utilization with reduced feature complexity

### Fixed
- 🗑️ **Removed Non-functional Features** - Eliminated account information display
  - Account data was not available in IDE databases as expected
  - Removed incomplete account extraction functionality
  - Fixed potential errors from missing account data sources

### Technical
- 🏗️ **Code Cleanup** - Removed account-related modules and dependencies
  - Deleted account.py handler and related functions
  - Cleaned up JavaScript account management code
  - Removed account-related CSS styles and HTML elements
  - Updated translations to remove account-specific text
  - Simplified API core by removing account endpoints

## [v1.2.0] - 2025-06-17

### Added
- 🤖 **Full Automation Workflow** - Complete 4-step automation process
  - Auto Signout: Intelligent IDE process detection and closure
  - Auto Cleaning: Comprehensive data cleaning (telemetry, database, workspace)
  - Auto Signin Preparation: Ready IDE for new Augment login
  - Auto Restart: Automatic IDE restart after cleaning
- ⚙️ **Customizable Automation Options** - Selective step execution with user-friendly modal
- 🔄 **Smart Process Management** - Cross-platform IDE process handling with graceful shutdown
- 🌐 **Complete Translation System** - Fixed missing English translations in automation modal
- 📦 **Enhanced Build System** - Updated all build scripts to include automation dependencies
- 🤖 Automatic versioning system based on commit messages
- 📋 Release script for manual version management
- 🚀 Auto-release workflow for GitHub Actions
- 🔍 Smart IDE detection with actual file system verification
- 💙 Complete VS Code Insiders support
- 🌐 Multi-language interface (Chinese/English)
- 📋 One-click path copying functionality
- 🎯 Non-overlapping toast notification system

### Enhanced
- 🛠️ **Process Management** - Added psutil dependency for reliable IDE process control
- 🎨 **User Interface** - New automation section with step-by-step progress display
- 📊 **Results Display** - Detailed automation results with individual step status
- 🔧 **Build Scripts** - Updated build.bat, build.py, build.sh, and GitHub Actions
- 🌐 **Internationalization** - Complete translation coverage for all automation features
- 🛠️ Backend path verification system
- ⚙️ Frontend event handling optimization
- 🏗️ Modular code refactoring
- 🌍 Cross-platform compatibility improvements
- 📦 GitHub Actions build system with multi-platform support

### Fixed
- 🌐 **Translation Issues** - Fixed missing English translations in automation options modal
- 📦 **Dependency Management** - Added psutil to requirements and build configurations
- 🔧 **Build System** - Updated all build scripts to include automation module
- 🎯 **Virtual Environment** - Fixed psutil installation in uv-managed environments
- 🔧 Path copying with correct backslashes
- 🌐 Language switching status issues
- ⚠️ RuntimeWarning on application startup
- 🔄 Auto-refresh override of detected IDEs
- 🎨 Toast notification overlap problems

### Technical
- 🔧 **New Dependencies** - Added psutil>=5.9.0 for process management
- 🏗️ **API Extensions** - New automation handlers and core API methods
- 🎨 **CSS Enhancements** - Automation section styling with responsive design
- 📱 **JavaScript Functions** - Complete automation workflow implementation
- 🔧 PyInstaller build optimizations
- 🎯 Pillow dependency for icon conversion
- 📊 Semantic versioning implementation
- 🤖 Intelligent commit message parsing
- 🚀 Automated release pipeline
---

## About This Modified Version

**Modified by UntaDotMy** - This version includes extensive refactoring and feature enhancements based on the original project by [vagmr](https://github.com/vagmr/Augment-Code-free).

### Key Improvements Over Original:
- Complete rewrite of IDE detection system
- Smart path verification with actual file system checks
- Multi-language support with dynamic switching
- Enhanced user interface with responsive design
- Automated build and release system
- Comprehensive error handling and user feedback

### Attribution
- **Original Project**: [vagmr/Augment-Code-free](https://github.com/vagmr/Augment-Code-free)
- **Modified by**: UntaDotMy
- **License**: MIT (maintained from original)
