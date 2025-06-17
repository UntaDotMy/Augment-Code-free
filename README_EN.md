# AugmentCode Free (***Modified***)

[中文](README.md) | **English**

AugmentCode Free is a simple GUI tool for cleaning AugmentCode-related data, helping you avoid account bans and enjoy free AugmentCode effortlessly.

> **Note**: This is a modified version of [vagmr/Augment-Code-free](https://github.com/vagmr/Augment-Code-free), extensively refactored and enhanced by **UntaDotMy**. Original project by **vagmr**, thanks for providing the foundation framework.

- **Smart Detection** - Auto-scan and verify all supported IDEs installed on the system with path accuracy
- **Cross-Platform Support** - Compatible with Windows, macOS, Linux
- **Dynamic Adaptation** - Automatically adjusts available operations based on selected IDE type
- **Multi-Language Support** - Chinese/English interface switching
- **Smart Path Verification** - Actual file system checking ensures all displayed paths exist


## Interface Preview

<div align="center">

### Main Interface
![Main Interface](docs/ui2.png)

### Operation Interface
![Operation Interface](docs/ui.png)

</div>

## Features

- 🖥️ **Modern GUI Interface**
  - Cross-platform desktop application based on webview
  - Intuitive interface design with responsive layout
  - Real-time operation feedback
  - **Complete Chinese/English bilingual interface switching** - No refresh needed, instant effect
  - Optimized notification system (no overlap)
  - **Smart Progress Dialogs** - Complex operations don't auto-close, users can review results in detail

- 🔍 **Smart IDE Detection (***Enhanced***)**
  - Automatically scan installed IDEs on the system
  - **Smart Path Verification** - Actually checks file system to ensure paths exist
  - Support for VSCode series (including VS Code Insiders) and JetBrains series
  - Cross-platform compatibility (Windows, macOS, Linux)
  - Dynamic operation interface adaptation
  - **One-Click Copy Paths** - Support for all verified paths

- 💙 **VSCode Series Support (***Enhanced***) (VSCode, VSCodium, Cursor, VS Code Insiders, etc.)**
  - Reset device ID and machine ID (Telemetry)
  - Clean specific records in SQLite database
  - Clean workspace storage files
  - Automatic backup of original data
  - **Smart Path Detection** - Automatically find and verify all related file paths
  - **VS Code Insiders Support** - Complete support for Insiders version

- 🧠 **JetBrains Series Support (***Enhanced***) (IDEA, PyCharm, GoLand, etc.)**
  - Reset PermanentDeviceId and PermanentUserId
  - Automatic file locking to prevent regeneration
  - Cross-platform file permission management
  - Support for all mainstream JetBrains IDEs
  - **Smart File Finding** - Automatically locate configuration files

- 🛡️ **Security Features (***Enhanced***)**
  - Automatic backup of important files before operations
  - File locking mechanism to prevent accidental modifications
  - Detailed operation logs and result feedback
  - **Path Verification** - Only display actually existing files and directories
  - **Safe Copy** - Prevents escaping issues when copying paths

- 🤖 **Full Automation Workflow (***New***)**
  - **One-Click Automation** - Complete automated workflow process
  - **Auto Signout** - Intelligent IDE process detection and closure
  - **Auto Cleaning** - Execute all necessary data cleaning operations
  - **Auto Restart** - Automatically restart IDE after cleaning
  - **Customizable Options** - Support selective execution of individual steps
  - **Detailed Progress Feedback** - Real-time display of each step's execution status
  - **Smart Result Display** - Complex operations don't auto-close after completion, users can review results in detail

- 🌐 **Complete Multi-Language Support (***Enhanced***)**
  - **Instant Language Switching** - Chinese/English switching without refresh, immediate effect
  - **Complete Translation Coverage** - All interface elements, progress info, error messages support translation
  - **Dynamic Content Translation** - Progress dialogs, result panels and other dynamic content update language in real-time
  - **No Hardcoded Text** - Complete elimination of hardcoded Chinese text, ensuring internationalization experience

## Installation

### Method 1: Download Executable (Recommended)

1. Download the latest version from [Releases](https://github.com/UntaDotMy/Augment-Code-free/releases) page
2. Choose the version for your system:
   - Windows: `AugmentFree_latest.exe`
   - Linux: `AugmentFree_latest` (Linux)
   - macOS: `AugmentFree_latest` (macOS)
3. Extract and run the corresponding executable

### Method 2: Run from Source

1. Ensure you have a suitable Python version installed
2. Clone this repository locally:
   ```bash
   git clone https://github.com/UntaDotMy/Augment-Code-free.git
   cd Augment-Code-free
   ```
3. Install dependencies:
   ```bash
   # Using uv (recommended)
   uv sync

   # Or using pip
   pip install -e .
   ```

### Method 3: Build Executable

If you want to build the executable yourself:

1. Clone the repository and install dependencies (see Method 2)
2. Install build dependencies:
   ```bash
   # Using uv
   uv sync --extra build

   # Or using pip
   pip install pyinstaller pillow
   ```
3. Run the build script:
   ```bash
   # Using Python script (recommended)
   python build.py

   # Windows users can also use
   build.bat
   ```
4. After building, the executable will be in the `dist/` directory

### Method 4: Automatic Versioning & Release System

The project supports intelligent automatic version management and releasing:

#### **🤖 Automatic Version Detection (Recommended)**:
The system automatically determines version type based on commit messages:
- **Major version (+1.0.0)**: Commits containing `BREAKING`, `major`, `breaking change`
- **Minor version (+0.1.0)**: Commits containing `feat`, `feature`, `enhancement`, `add`, `new`
- **Patch version (+0.0.1)**: Other commits (bug fixes, etc.)

```bash
# Just commit normally, system handles versioning automatically
git add .
git commit -m "feat: add new smart detection feature"
git push origin main
# System automatically creates v1.1.0 release
```

#### **📋 Manual Version Release**:
```bash
# Use release script (recommended)
python scripts/release.py

# Windows users
scripts/release.bat

# Or manually create tag
git tag v1.0.0
git push origin v1.0.0
```

#### **🎯 GitHub Actions Manual Trigger**:
1. Go to GitHub repository → **Actions**
2. Select **"Auto Release"** workflow
3. Click **"Run workflow"**
4. Choose version type (major/minor/patch)
5. Click **"Run workflow"**

#### **📊 Version Number Rules**:
- **v1.0.0** → **v2.0.0** (Major): Breaking changes, major updates
- **v1.0.0** → **v1.1.0** (Minor): New features, enhancements
- **v1.0.0** → **v1.0.1** (Patch): Bug fixes, small changes

#### **🎯 Commit Message Examples**:
```bash
# Major version update
git commit -m "BREAKING: redesign entire UI system"

# Minor version update
git commit -m "feat: add VS Code Insiders support"
git commit -m "enhancement: improve path detection"

# Patch version update
git commit -m "fix: resolve copy button issue"
git commit -m "docs: update README"
```

## Usage

### Using Executable

1. **Log out from AugmentCode plugin**
2. **Completely exit the selected editor**
3. **Run the application**:
   - Double-click `AugmentFree_latest.exe`
   - Or run in command line: `./AugmentFree_latest.exe`
4. **Select desired operations in the GUI interface**
5. **Restart the selected editor**
6. **Log in with a new email in AugmentCode plugin**

### Running from Source

1. **Log out from AugmentCode plugin**
2. **Completely exit the selected editor**
3. **Run the application**:
   ```bash
   # Using run.py script (recommended)
   python run.py

   # Or run module directly
   python -m augment_free.main
   ```
4. **Select desired operations in the GUI interface**
5. **Restart the selected editor**
6. **Log in with a new email in AugmentCode plugin**


### Development Environment Setup

1. Fork this repository
2. Clone your fork:
   ```bash
   git clone https://github.com/your-github-username/Augment-Code-free.git
   ```
3. Install development dependencies:
   ```bash
   uv sync --dev
   ```
4. Make your changes

## 🚀 Modified Version Improvements (Modified by UntaDotMy)

This modified version includes extensive refactoring and feature enhancements based on the original project:

### 🔧 **Core Improvements**
- **Smart Path Detection System** - Actual file system verification ensures all displayed paths exist
- **Full VS Code Insiders Support** - Complete detection and support for VS Code Insiders
- **Multi-Language Interface** - Dynamic Chinese/English switching without restart
- **Responsive UI Design** - Auto-adjusts layout based on window size

### 🎯 **User Experience Optimization**
- **Non-Overlapping Notifications** - Smart message stacking system prevents notification overlap
- **One-Click Copy Feature** - All verified paths support one-click copy to clipboard
- **Real-Time Status Updates** - Improved status checking mechanism prevents freezing
- **Auto-Refresh Persistence** - Maintains IDE display after detection, won't be overridden by auto-refresh
- **Smart Progress Management** - Complex operations (All Operations, Automation Workflows) don't auto-close after completion, users can review detailed results
- **Complete Translation Experience** - Instant language switching, all dynamic content updates in real-time, no hardcoded text

### 🛠️ **Technical Improvements**
- **Backend Path Verification** - Python backend actually checks file existence
- **Frontend Event Optimization** - Uses event listeners instead of inline events, avoiding escaping issues
- **Modular Refactoring** - Improved code structure and error handling
- **Cross-Platform Compatibility** - Enhanced Windows, macOS, Linux support

### 📦 **Build and Deployment**
- **GitHub Actions Auto-Build** - Automatically generates multi-platform executables
- **Multi-Platform Release** - Simultaneous release for Windows, Linux, macOS

> **Acknowledgments**: Thanks to the original author [vagmr](https://github.com/vagmr) for providing the excellent foundation framework. This modified version includes extensive improvements and feature enhancements based on their work.

## ⚠️ Disclaimer

**Use at Your Own Risk:** This tool is for educational and research purposes only. Users assume all risks associated with its use.

**Data Safety:** Please ensure important data is backed up before use. The author is not responsible for any data loss.

**Compliance:** Please comply with relevant software terms of use and local laws and regulations.

**No Warranty:** This software is provided "as is" without any express or implied warranties.

**Commercial Use:** All commercial sales are unrelated to the author. Please obtain from official channels.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) file for details.
