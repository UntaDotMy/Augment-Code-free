# Augment-Code-Free (***Modified***)

**中文** | [English](README_EN.md)

[![GitHub downloads](https://img.shields.io/github/downloads/UntaDotMy/Augment-Code-free/total)](https://github.com/UntaDotMy/Augment-Code-free/releases)

Augment-Code-Free 是一个用于清理 AugmentCode插件 相关数据的简易Gui工具，避免账号被禁用，让你轻松享受free的AugmentCode。

> **注意**: 此版本为 [vagmr/Augment-Code-free](https://github.com/vagmr/Augment-Code-free) 的修改版本，由 **UntaDotMy** 进行了大量重构和功能增强。原项目作者为 **vagmr**，感谢其提供的基础框架。

- **智能检测** - 自动扫描并验证系统中已安装的所有支持IDE，确保路径准确性
- **跨平台支持** - Windows、macOS、Linux 全平台兼容
- **动态适配** - 根据选择的IDE类型自动调整可用操作
- **多语言支持** - 中文/英文界面切换
- **智能路径验证** - 实际文件系统检查，确保所有显示的路径都真实存在

## 界面预览

<div align="center">

### 主界面
![主界面](docs/ui2.png)

### 操作界面
![操作界面](docs/ui.png)

</div>

## 功能特性

- 🖥️ **现代化 GUI 界面**
  - 基于 webview 的桌面应用程序
  - 直观的界面设计，响应式布局
  - 实时操作反馈
  - 中文/英文双语界面切换
  - 优化的消息提示系统（无重叠）

- 🔍 **智能 IDE 检测 (***增强***)**
  - 自动扫描系统中已安装的IDE
  - **智能路径验证** - 实际检查文件系统，确保路径存在
  - 支持 VSCode 系列（包括 VS Code Insiders）和 JetBrains 系列
  - 跨平台兼容（Windows、macOS、Linux）
  - 动态操作界面适配
  - **一键复制路径** - 支持所有验证过的路径

- 💙 **VSCode 系列支持 (***增强***) (vscode，vscodium,cursor,VS Code Insiders等)**
  - 重置设备 ID 和机器 ID（Telemetry）
  - 清理 SQLite 数据库中的特定记录
  - 清理工作区存储文件
  - 自动备份原始数据
  - **智能路径检测** - 自动查找并验证所有相关文件路径
  - **支持 VS Code Insiders** - 完整支持 Insiders 版本

- 🧠 **JetBrains 系列支持 (***增强***) (idea,pycharm,goland等)**
  - 重置 PermanentDeviceId 和 PermanentUserId
  - 自动文件锁定防止重新生成
  - 跨平台文件权限管理
  - 支持所有主流 JetBrains IDE
  - **智能文件查找** - 自动定位配置文件

- 🛡️ **安全特性 (***增强***)**
  - 操作前自动备份重要文件
  - 文件锁定机制防止意外修改
  - 详细的操作日志和结果反馈
  - **路径验证** - 只显示实际存在的文件和目录
  - **安全复制** - 防止路径复制时的转义问题


## 安装说明

### 方式一：直接下载可执行文件（推荐）

1. 从 [Releases](https://github.com/UntaDotMy/Augment-Code-free/releases) 页面下载最新版本
2. 选择适合你系统的版本：
   - Windows: `AugmentFree_latest.exe`
   - Linux: `AugmentFree_latest` (Linux)
   - macOS: `AugmentFree_latest` (macOS)
3. 解压并运行对应的可执行文件

### 方式二：从源码运行

1. 确保你的系统已安装合适的python版本
2. 克隆此仓库到本地：
   ```bash
   git clone https://github.com/UntaDotMy/Augment-Code-free.git
   cd Augment-Code-free
   ```
3. 安装依赖：
   ```bash
   # 使用 uv（推荐）
   uv sync

   # 或使用 pip
   pip install -e .
   ```

### 方式三：构建可执行文件

如果你想自己构建可执行文件：

1. 克隆仓库并安装依赖（参考方式二）
2. 安装构建依赖：
   ```bash
   # 使用 uv
   uv sync --extra build

   # 或使用 pip
   pip install pyinstaller pillow
   ```
3. 运行构建脚本：
   ```bash
   # 使用 Python 脚本（推荐）
   python build.py

   # Windows 用户也可以使用
   build.bat
   ```
4. 构建完成后，可执行文件将在 `dist/` 目录中

### 方式四：自动版本发布系统

项目支持智能自动版本管理和发布：

#### **🤖 自动版本检测（推荐）**：
系统会根据提交信息自动确定版本类型：
- **主版本 (+1.0.0)**: 包含 `BREAKING`、`major`、`breaking change` 的提交
- **次版本 (+0.1.0)**: 包含 `feat`、`feature`、`enhancement`、`add`、`new` 的提交
- **补丁版本 (+0.0.1)**: 其他提交（bug修复等）

```bash
# 只需正常提交，系统自动处理版本
git add .
git commit -m "feat: add new smart detection feature"
git push origin main
# 系统自动创建 v1.1.0 版本
```

#### **📋 手动版本发布**：
```bash
# 使用发布脚本（推荐）
python scripts/release.py

# Windows 用户
scripts/release.bat

# 或手动创建标签
git tag v1.0.0
git push origin v1.0.0
```

#### **🎯 GitHub Actions 手动触发**：
1. 进入 GitHub 仓库 → **Actions**
2. 选择 **"Auto Release"** 工作流
3. 点击 **"Run workflow"**
4. 选择版本类型（major/minor/patch）
5. 点击 **"Run workflow"**

#### **📊 版本号规则**：
- **v1.0.0** → **v2.0.0** (主版本): 重大更新、破坏性变更
- **v1.0.0** → **v1.1.0** (次版本): 新功能、增强功能
- **v1.0.0** → **v1.0.1** (补丁版本): Bug修复、小改动

#### **🎯 提交信息示例**：
```bash
# 主版本更新
git commit -m "BREAKING: redesign entire UI system"

# 次版本更新
git commit -m "feat: add VS Code Insiders support"
git commit -m "enhancement: improve path detection"

# 补丁版本更新
git commit -m "fix: resolve copy button issue"
git commit -m "docs: update README"
```

> **💡 提示**: 系统会在每次推送到 main 分支时自动检查是否需要创建新版本。如果有新的提交，会根据提交信息自动确定版本类型并创建发布。

#### **🔧 构建系统优化**：
- 使用 pip 和 requirements.txt 以提高稳定性
- 简化 PyInstaller 命令减少超时
- 添加依赖缓存加速构建
- 增强错误处理和回退机制
- 修复许可证分类器冲突问题
- 修复平台特定可执行文件命名冲突
- 改进缓存路径配置

## 使用方法

### 使用可执行文件

1. **Augment插件退出原有账号**
2. **完全退出选择的编辑器**
3. **运行应用程序**：
   - 双击 `AugmentFree_latest.exe`
   - 或在命令行中运行：`./AugmentFree_latest.exe`
4. **在 GUI 界面中选择需要的操作**
5. **重新启动选择的编辑器**
6. **在 Augment 插件中使用新的邮箱进行登录**

### 从源码运行

1. **Augment插件退出原有账号**
2. **完全退出选择的编辑器**
3. **运行应用程序**：
   ```bash
   # 使用 run.py 脚本（推荐）
   python run.py

   # 或直接运行模块
   python -m augment_free.main
   ```
4. **在 GUI 界面中选择需要的操作**
5. **重新启动选择的编辑器**
6. **在 Augment 插件中使用新的邮箱进行登录**



### 开发环境设置

1. Fork 此仓库
2. 克隆你的fork：
   ```bash
   git clone https://github.com/你的github用户名/Augment-Code-free.git
   ```
3. 安装开发依赖：
   ```bash
   uv sync --dev
   ```
4. 进行修改

## 🚀 修改版本改进 (Modified by UntaDotMy)

此修改版本在原项目基础上进行了大量重构和功能增强：

### 🔧 **核心改进**
- **智能路径检测系统** - 实际文件系统验证，确保所有显示路径真实存在
- **VS Code Insiders 完整支持** - 新增对 VS Code Insiders 的完整检测和支持
- **多语言界面** - 中文/英文动态切换，无需重启
- **响应式UI设计** - 根据窗口大小自动调整布局

### 🎯 **用户体验优化**
- **无重叠消息提示** - 智能消息堆叠系统，避免通知重叠
- **一键复制功能** - 所有验证路径支持一键复制到剪贴板
- **实时状态更新** - 改进的状态检查机制，避免卡顿
- **自动刷新保持** - 检测到IDE后保持显示，不会被自动刷新覆盖

### 🛠️ **技术改进**
- **后端路径验证** - Python后端实际检查文件存在性
- **前端事件优化** - 使用事件监听器替代内联事件，避免转义问题
- **模块化重构** - 改进的代码结构和错误处理
- **跨平台兼容性** - 增强的Windows、macOS、Linux支持

### 📦 **构建和部署**
- **GitHub Actions自动构建** - 自动生成多平台可执行文件
- **多平台发布** - Windows、Linux、macOS 三平台同时发布

> **致谢**: 感谢原作者 [vagmr](https://github.com/vagmr) 提供的优秀基础框架，本修改版本在其基础上进行了大量改进和功能增强。

## ⚠️ 免责声明

**使用风险自负：** 本工具仅供学习和研究目的使用，使用者需自行承担使用风险。

**数据安全：** 使用前请确保重要数据已备份，作者不对任何数据丢失负责。

**合规使用：** 请遵守相关软件的使用条款和当地法律法规。

**无担保：** 本软件按"现状"提供，不提供任何明示或暗示的担保。

**商业使用：** 所有商业售卖行为均与本人无关。

## 许可证

此项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。