# AugmentCode Free

**中文** | [English](README_EN.md)

AugmentCode Free 是一个用于清理 AugmentCode 相关数据的简易Gui工具，避免账号为禁用，让你轻松享受free的AugmentCode。

## 界面预览

<div align="center">

### 主界面
![主界面](docs/ui2.png)

### 操作界面
![操作界面](docs/ui.png)

</div>

## 功能特性

- 🖥️ **现代化 GUI 界面**
  - 基于 webview 的跨平台桌面应用
  - 直观的界面设计
  - 实时操作反馈

- 📝 **Telemetry ID 管理**
  - 重置设备 ID 和机器 ID
  - 自动备份原始数据
  - 生成新的随机 ID

- 🗃️ **数据库清理**
  - 清理 SQLite 数据库中的特定记录
  - 自动备份数据库文件
  - 删除包含 'augment' 关键字的记录

- 💾 **工作区存储管理**
  - 清理工作区存储文件
  - 自动备份工作区数据


## 安装说明

### 方式一：直接下载可执行文件（推荐）

1. 从 [Releases](https://github.com/vagmr/Augment-free/releases) 页面下载最新版本
2. 解压并运行 `AugmentFree_latest.exe`

### 方式二：从源码运行

1. 确保你的系统已安装合适的python版本
2. 克隆此仓库到本地：
   ```bash
   git clone https://github.com/vagmr/Augment-free.git
   cd Augment-free
   ```
3. 安装依赖：
   ```bash
   # 使用 uv（推荐）
   uv sync

   # 或使用 pip
   pip install -e .
   ```

## 使用方法

### 使用可执行文件

1. **AugmentCode插件退出原有账号**
2. **完全退出 VS Code或vscodium**
3. **运行应用程序**：
   - 双击 `AugmentFree_latest.exe`
   - 或在命令行中运行：`./AugmentFree_latest.exe`
4. **在 GUI 界面中选择需要的操作**
5. **重新启动 VS Code或vscodium**
6. **在 AugmentCode 插件中使用新的邮箱进行登录**

### 从源码运行

1. **AugmentCode插件退出原有账号**
2. **完全退出 VS Code或vscodium**
3. **运行应用程序**：
   ```bash
   # 使用 run.py 脚本（推荐）
   python run.py

   # 或直接运行模块
   python -m augment_free.main
   ```
4. **在 GUI 界面中选择需要的操作**
5. **重新启动 Vs Code或vscodium**
6. **在 AugmentCode 插件中使用新的邮箱进行登录**



### 开发环境设置

1. Fork 此仓库
2. 克隆您的 fork：
   ```bash
   git clone https://github.com/your-username/Augment-free.git
   ```
3. 安装开发依赖：
   ```bash
   uv sync --dev
   ```
4. 进行您的修改

## 许可证

此项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。