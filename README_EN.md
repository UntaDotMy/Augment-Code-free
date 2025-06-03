# AugmentCode Free

[中文](README.md) | **English**

AugmentCode Free is a simple GUI tool for cleaning AugmentCode-related data, helping you avoid account bans and enjoy free AugmentCode effortlessly.

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
  - Intuitive interface design
  - Real-time operation feedback

- 📝 **Telemetry ID Management**
  - Reset device ID and machine ID
  - Automatic backup of original data
  - Generate new random IDs

- 🗃️ **Database Cleaning**
  - Clean specific records in SQLite database
  - Automatic database file backup
  - Remove records containing 'augment' keywords

- 💾 **Workspace Storage Management**
  - Clean workspace storage files
  - Automatic workspace data backup

## Installation

### Method 1: Download Executable ( Windows Recommended)

1. Download the latest version from [Releases](https://github.com/vagmr/Augment-free/releases) page
2. Extract and run `AugmentFree_latest.exe`

### Method 2: Run from Source

1. Ensure you have a suitable Python version installed
2. Clone this repository locally:
   ```bash
   git clone https://github.com/vagmr/Augment-free.git
   cd Augment-free
   ```
3. Install dependencies:
   ```bash
   # Using uv (recommended)
   uv sync

   # Or using pip
   pip install -e .
   ```

## Usage

### Using Executable

1. **Log out from AugmentCode plugin**
2. **Completely exit VS Code or VSCodium**
3. **Run the application**:
   - Double-click `AugmentFree_latest.exe`
   - Or run in command line: `./AugmentFree_latest.exe`
4. **Select desired operations in the GUI interface**
5. **Restart VS Code or VSCodium**
6. **Log in with a new email in AugmentCode plugin**

### Running from Source

1. **Log out from AugmentCode plugin**
2. **Completely exit VS Code or VSCodium**
3. **Run the application**:
   ```bash
   # Using run.py script (recommended)
   python run.py

   # Or run module directly
   python -m augment_free.main
   ```
4. **Select desired operations in the GUI interface**
5. **Restart VS Code or VSCodium**
6. **Log in with a new email in AugmentCode plugin**


### Development Environment Setup

1. Fork this repository
2. Clone your fork:
   ```bash
   git clone https://github.com/your-github-username/Augment-free.git
   ```
3. Install development dependencies:
   ```bash
   uv sync --dev
   ```
4. Make your changes

## ⚠️ Disclaimer

**Use at Your Own Risk:** This tool is for educational and research purposes only. Users assume all risks associated with its use.

**Data Safety:** Please ensure important data is backed up before use. The author is not responsible for any data loss.

**Compliance:** Please comply with relevant software terms of use and local laws and regulations.

**No Warranty:** This software is provided "as is" without any express or implied warranties.

**Commercial Use:** All commercial sales are unrelated to the author. Please obtain from official channels.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) file for details.
