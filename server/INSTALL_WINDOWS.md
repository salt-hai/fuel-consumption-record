# Windows 环境安装指南

## 前端安装

```bash
cd client
pnpm install
pnpm dev
```

## 后端安装

### 方法一：使用 pip（推荐）

```bash
cd server
pip install -r requirements.txt
```

### 方法二：如果 bcrypt 安装失败

安装预编译的 bcrypt：

```bash
pip install bcrypt==4.0.1
pip install -r requirements.txt
```

### 方法三：使用 Docker（最简单）

无需安装 Python 环境：

```bash
# 在项目根目录
docker-compose up -d
```

## 常见问题

### 1. 缺少 C++ 编译工具

如果看到 "Microsoft Visual C++ 14.0 or greater is required" 错误：

**快速解决**：安装预编译版本
```bash
pip install https://github.com/cgohlke/pybind11/releases/download/v2.10.4/pydantic_core-2.10.4-cp311-cp311-win_amd64.whl
```

**永久解决**：安装 [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
- 下载后运行安装程序
- 勾选 "使用 C++ 的桌面开发"
- 安装

### 2. bcrypt 编译失败

```bash
# 使用预编译版本
pip install bcrypt==4.0.1
```

### 3. DLL 加载失败

确保安装了 [Microsoft Visual C++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe)

## 使用虚拟环境（推荐）

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
.\venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 运行服务
uvicorn main:app --reload
```
