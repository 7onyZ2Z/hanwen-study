# Hanwen Study (瀚文学习自监督看板) 📚

Hanwen Study 是一个全栈开发的学习进度追踪与任务管理系统。它帮助用户规划学习任务、可视化监控学习进度，并提供每日打卡功能以培养持续学习的习惯。

项目采用前后端分离架构，完美适配桌面端与移动端访问，支持 Docker 一键部署。

## ✨ 主要功能

*   **📊 数据看板 (Dashboard)**
    *   **可视化进度**: 通过 ECharts 环形图直观展示整体学习完成度。
    *   **每日打卡**: 记录总学习天数与连续打卡天数，激励持续学习。
    *   **响应式设计**: PC 端展示侧边栏图表，移动端自动切换为纵向流式布局。

*   **📝 任务管理 (Task Management)**
    *   **任务 CRUD**: 轻松创建、编辑、删除学习任务。
    *   **详细追踪**: 设定任务总集数与当前进度，自动计算完成百分比。
    *   **个性化**: 支持为不同任务设置专属颜色标签。
    *   **快捷跳转**: 支持绑定网课链接，一键直达学习页面。

*   **🛡️ 用户与权限**
    *   **身份认证**: 完整的注册与登录流程 (JWT Authentication)。
    *   **后台管理**: 管理员可查看所有用户及其学习进度，并具备修改权限。

## 🛠️ 技术栈

### 前端 (Frontend)
*   **Vue 3** (Composition API)
*   **Vite** - 极速构建工具
*   **Element Plus** - 现代化 UI 组件库
*   **ECharts** - 强大的数据可视化库
*   **Pinia** - 状态管理
*   **Axios** - 网络请求

### 后端 (Backend)
*   **FastAPI** - 高性能 Python Web 框架
*   **SQLAlchemy** - ORM 框架
*   **SQLite** - 轻量级数据库 (易于部署与迁移)
*   **Pydantic** - 数据验证

### 部署 (Deployment)
*   **Docker & Docker Compose** - 容器化编排
*   **Nginx** - 反向代理与静态资源服务

## 🚀 快速开始

### 方式一：Docker 一键部署 (推荐)

确保本地已安装 Docker 和 Docker Compose。

1.  **克隆仓库**
    ```bash
    git clone https://github.com/your-username/hanwen_study.git
    cd hanwen_study
    ```

2.  **启动服务**
    ```bash
    docker compose up -d --build
    ```

3.  **访问应用**
    *   打开浏览器访问: `http://localhost:4000` (或服务器 IP)
    *   默认后端端口已映射至内部 `9000`

---

### 方式二：本地开发环境搭建

#### 后端 (Backend)

1.  进入后端目录:
    ```bash
    cd backend
    ```

2.  创建并激活虚拟环境 (可选):
    ```bash
    python -m venv venv
    source venv/bin/activate  # Windows: venv\Scripts\activate
    ```

3.  安装依赖:
    ```bash
    pip install -r requirements.txt
    ```

4.  启动后端服务 (默认端口 9000):
    ```bash
    uvicorn main:app --reload --port 9000
    ```

#### 前端 (Frontend)

1.  进入前端目录:
    ```bash
    cd frontend
    ```

2.  安装依赖:
    ```bash
    npm install
    ```

3.  启动开发服务器:
    ```bash
    npm run dev
    ```

4.  访问本地开发地址 (通常为 `http://localhost:5173`)。

## 📂 项目结构

```
hanwen_study/
├── backend/                # FastAPI 后端源码
│   ├── main.py             # 入口文件
│   ├── models.py           # 数据库模型
│   ├── schemas.py          # Pydantic 模式
│   ├── crud.py             # 数据库操作
│   └── ...
├── frontend/               # Vue 3 前端源码
│   ├── src/
│   │   ├── views/          # 页面组件 (Dashboard, TaskManage...)
│   │   ├── stores/         # Pinia 状态管理
│   │   └── ...
├── docker-compose.yml      # Docker 编排文件
└── README.md
```

## 📄 许可证

本项目采用 MIT 许可证开源。详情请参阅 [LICENSE](LICENSE) 文件。
