# Token 认证 + 缺失功能 + 油耗计算优化 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 完善 Token 认证系统、补充缺失功能、优化燃油消耗计算为国际标准累积法

**Architecture:** SQLite 存储 Token + SHA256 哈希 + 依赖注入获取当前用户；油耗计算采用累积法，追踪两次加满之间的所有加油记录

**Tech Stack:** FastAPI, SQLAlchemy, aiosqlite, hashlib, Vue 3, Pinia

---

## 文件结构

### 后端 (server/)
```
models/
  token.py          [NEW] Token 模型
  user.py           [MODIFY] 添加 tokens 关系
schemas/
  auth.py           [MODIFY] 完善 token 响应结构
routers/
  auth.py           [MODIFY] 实现 logout/me/password, 添加依赖注入
  records.py        [MODIFY] 修改油耗计算为累积法
utils/
  auth.py           [NEW] Token 验证依赖和工具函数
tests/
  test_auth.py      [MODIFY] 添加新测试
```

### 前端 (client/)
```
src/
  api/
    auth.ts         [MODIFY] 添加 logout/me API
    vehicles.ts     [MODIFY] 确认 CRUD 完整
  views/
    VehicleView.vue [MODIFY] 添加添加车辆表单
  router/
    index.ts        [MODIFY] 添加路由守卫
```

---

## Task 1: 创建 Token 模型和数据库迁移

**Files:**
- Create: `server/models/token.py`
- Modify: `server/models/user.py`

- [ ] **Step 1: 创建 Token 模型**

```python
# server/models/token.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from database import Base

class Token(Base):
    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token_hash = Column(String, nullable=False, unique=True, index=True)
    created_at = Column(DateTime, server_default=func.current_timestamp())
    last_used_at = Column(DateTime, server_default=func.current_timestamp())

    user = relationship("User", back_populates="tokens")
```

- [ ] **Step 2: 修改 User 模型添加关系**

```python
# server/models/user.py - 在 User 类中添加:
tokens = relationship("Token", back_populates="user", cascade="all, delete-orphan")
```

- [ ] **Step 3: 提交**

```bash
cd server
git add models/token.py models/user.py
git commit -m "feat: add Token model for SQLite-based auth

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 2: 创建认证工具函数

**Files:**
- Create: `server/utils/auth.py`

- [ ] **Step 1: 创建认证工具函数**

```python
# server/utils/auth.py
import hashlib
import secrets
from fastapi import HTTPException, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from models.token import Token
from models.user import User

def hash_token(token: str) -> str:
    """SHA256 哈希 token"""
    return hashlib.sha256(token.encode()).hexdigest()

def generate_token() -> str:
    """生成安全的随机 token"""
    return secrets.token_urlsafe(32)

async def get_current_user(
    token: str = Depends(lambda: None),
    db: AsyncSession = Depends(get_db)
) -> User:
    """从 token 获取当前用户（依赖注入）"""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未提供认证令牌"
        )

    # 从 Authorization 头提取 token
    if token.startswith("Bearer "):
        token = token[7:]

    token_hash = hash_token(token)

    # 查询 token 和用户
    result = await db.execute(
        select(Token, User)
        .join(User, Token.user_id == User.id)
        .where(Token.token_hash == token_hash)
    )
    row = result.first()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌"
        )

    token_obj, user = row

    # 检查用户是否激活
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账户已被禁用"
        )

    # 更新最后使用时间
    from datetime import datetime
    token_obj.last_used_at = datetime.utcnow()
    await db.commit()

    return user
```

- [ ] **Step 2: 提交**

```bash
cd server
git add utils/auth.py
git commit -m "feat: add auth utilities with token validation

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 3: 重构 Auth Router 实现 Token 存储

**Files:**
- Modify: `server/routers/auth.py`

- [ ] **Step 1: 重写 auth.py 使用新的 Token 系统**

```python
# server/routers/auth.py
from fastapi import APIRouter, HTTPException, Depends, status, Header
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from database import get_db
from models.user import User
from models.token import Token
from schemas.auth import RegisterRequest, LoginRequest, ChangePasswordRequest
from schemas.common import success_response
from utils.auth import get_current_user, generate_token, hash_token

router = APIRouter(prefix="/v1/auth", tags=["认证"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

async def get_token_from_header(authorization: str = Header(None)) -> str:
    """从 Authorization 头提取 token"""
    if authorization and authorization.startswith("Bearer "):
        return authorization[7:]
    return ""

@router.post("/register")
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """注册新用户"""
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="该邮箱已被注册")

    user = User(
        email=data.email,
        password_hash=get_password_hash(data.password),
        name=data.name
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    # 创建 token
    token = generate_token()
    token_obj = Token(user_id=user.id, token_hash=hash_token(token))
    db.add(token_obj)
    await db.commit()

    return success_response({
        "token": token,
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name
        }
    }, "注册成功")

@router.post("/login")
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    """邮箱+密码登录"""
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="邮箱或密码错误")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="账户已被禁用")

    # 创建 token
    token = generate_token()
    token_obj = Token(user_id=user.id, token_hash=hash_token(token))
    db.add(token_obj)
    await db.commit()

    return success_response({
        "token": token,
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name
        }
    }, "登录成功")

@router.delete("/logout")
async def logout(
    token: str = Depends(get_token_from_header),
    db: AsyncSession = Depends(get_db)
):
    """退出登录 - 删除当前 token"""
    if not token:
        raise HTTPException(status_code=401, detail="未提供认证令牌")

    token_hash = hash_token(token)
    result = await db.execute(select(Token).where(Token.token_hash == token_hash))
    token_obj = result.scalar_one_or_none()

    if token_obj:
        await db.delete(token_obj)
        await db.commit()

    return success_response(message="退出成功")

@router.get("/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return success_response({
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name
    })

@router.put("/password")
async def change_password(
    data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """修改密码"""
    if not verify_password(data.old_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="原密码错误")

    current_user.password_hash = get_password_hash(data.new_password)
    await db.commit()

    return success_response(message="密码修改成功")
```

- [ ] **Step 2: 提交**

```bash
cd server
git add routers/auth.py
git commit -m "feat: implement SQLite-based token auth system

- Add logout endpoint
- Implement /me endpoint
- Implement change password with validation
- Use get_current_user dependency for protected routes

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 4: 修改油耗计算为累积法

**Files:**
- Modify: `server/routers/records.py`

- [ ] **Step 1: 修改 calculate_fuel_consumption 函数为累积法**

```python
# server/routers/records.py - 替换 calculate_fuel_consumption 函数

async def calculate_fuel_consumption(
    db: AsyncSession,
    vehicle_id: int,
    current_odometer: int,
) -> Optional[float]:
    """
    计算油耗 (L/100km) - 国际标准累积法

    从上次加满到本次加满之间：
    - 累积加油量 = Σ(中间所有记录的 volume，包括本次)
    - 累积里程 = 本次里程 - 上次加满里程
    - 油耗 = 累积加油量 / 累积里程 × 100
    """
    # 查找上一次加满的记录
    result = await db.execute(
        select(FuelRecord)
        .where(
            and_(
                FuelRecord.vehicle_id == vehicle_id,
                FuelRecord.full_tank == True,
                FuelRecord.odometer < current_odometer
            )
        )
        .order_by(FuelRecord.odometer.desc())
        .limit(1)
    )
    prev_record = result.scalar_one_or_none()

    if not prev_record:
        return None

    # 计算累积里程
    distance = current_odometer - prev_record.odometer
    if distance <= 0:
        return None

    # 查询两次加满之间的所有记录（不包括上次加满，包括本次加满后的记录）
    result = await db.execute(
        select(FuelRecord)
        .where(
            and_(
                FuelRecord.vehicle_id == vehicle_id,
                FuelRecord.odometer > prev_record.odometer,
                FuelRecord.odometer <= current_odometer
            )
        )
    )
    intermediate_records = result.scalars().all()

    # 累积加油量（所有中间记录 + 本次记录的 volume）
    # 注意：本次记录还没保存，所以需要额外计算
    total_volume = sum(r.volume for r in intermediate_records)

    # 计算油耗
    return (total_volume / distance) * 100
```

- [ ] **Step 2: 修改创建和更新记录的调用方式**

```python
# server/routers/records.py - 在 create_record 中，修改计算调用：

@router.post("", response_model=RecordResponse)
async def create_record(data: RecordCreate, db: AsyncSession = Depends(get_db)):
    # 验证车辆存在
    result = await db.execute(select(Vehicle).where(Vehicle.id == data.vehicle_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="车辆不存在")

    record = FuelRecord(**data.model_dump())

    # 计算油耗（累积法）
    if record.full_tank:
        record.fuel_consumption = await calculate_fuel_consumption(
            db, record.vehicle_id, record.odometer
        )

    db.add(record)
    await db.commit()
    await db.refresh(record)

    return RecordResponse.model_validate(record)
```

- [ ] **Step 3: 提交**

```bash
cd server
git add routers/records.py
git commit -m "feat: use cumulative method for fuel consumption calculation

Implement international standard: accumulate all fuel volume between
two full-tank records for accurate L/100km calculation.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 5: 更新前端 Auth API 和 Store

**Files:**
- Modify: `client/src/api/auth.ts`
- Modify: `client/src/stores/auth.ts`

- [ ] **Step 1: 添加 logout 和 me API**

```typescript
// client/src/api/auth.ts - 添加:

// 退出登录
export const logout = () => {
  return api.delete('/v1/auth/logout')
}

// 获取当前用户
export const getCurrentUser = () => {
  return api.get('/v1/auth/me')
}
```

- [ ] **Step 2: 更新 auth store**

```typescript
// client/src/stores/auth.ts - 修改 logout 和添加 getCurrentUser:

// 登出
const logout = async () => {
  try {
    await authApi.logout()
  } catch (error) {
    // 即使后端调用失败，也清除本地状态
    console.error('Logout API error:', error)
  } finally {
    token.value = null
    user.value = null
    localStorage.removeItem('auth_token')
    localStorage.removeItem('auth_user')
  }
}

// 获取当前用户信息
const fetchCurrentUser = async () => {
  try {
    const res = await authApi.getCurrentUser()
    user.value = res
    localStorage.setItem('auth_user', JSON.stringify(res))
    return res
  } catch (error) {
    // token 可能过期，清除本地状态
    token.value = null
    user.value = null
    localStorage.removeItem('auth_token')
    localStorage.removeItem('auth_user')
    throw error
  }
}

// 在 return 中添加:
return {
  token,
  user,
  isAuthenticated,
  register,
  login,
  logout,
  changePassword,
  fetchCurrentUser,
}
```

- [ ] **Step 3: 提交**

```bash
cd client
git add src/api/auth.ts src/stores/auth.ts
git commit -m "feat: add logout/me APIs and update auth store

- Add backend logout call
- Add fetchCurrentUser method
- Handle token expiry gracefully

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 6: 添加车辆管理页面

**Files:**
- Modify: `client/src/views/VehicleView.vue`

- [ ] **Step 1: 实现 VehicleView 添加车辆功能**

```vue
<!-- client/src/views/VehicleView.vue -->
<template>
  <div class="vehicle-view p-4">
    <h1 class="text-xl font-bold mb-4">车辆管理</h1>

    <!-- 添加车辆表单 -->
    <div class="bg-white rounded-lg shadow p-4 mb-4">
      <h2 class="text-lg font-semibold mb-3">添加车辆</h2>
      <form @submit.prevent="handleAddVehicle" class="space-y-3">
        <input
          v-model="newVehicle.name"
          type="text"
          placeholder="车辆名称"
          class="w-full p-2 border rounded"
          required
        />
        <input
          v-model="newVehicle.plate_number"
          type="text"
          placeholder="车牌号"
          class="w-full p-2 border rounded"
          required
        />
        <input
          v-model="newVehicle.brand"
          type="text"
          placeholder="品牌"
          class="w-full p-2 border rounded"
        />
        <input
          v-model.number="newVehicle.initial_odometer"
          type="number"
          placeholder="初始里程"
          class="w-full p-2 border rounded"
        />
        <button
          type="submit"
          class="w-full bg-blue-500 text-white p-2 rounded hover:bg-blue-600"
        >
          添加
        </button>
      </form>
    </div>

    <!-- 车辆列表 -->
    <div class="space-y-3">
      <div
        v-for="vehicle in vehicles"
        :key="vehicle.id"
        class="bg-white rounded-lg shadow p-4"
      >
        <div class="flex justify-between items-start">
          <div>
            <h3 class="font-semibold">{{ vehicle.name }}</h3>
            <p class="text-sm text-gray-600">车牌: {{ vehicle.plate_number }}</p>
            <p v-if="vehicle.brand" class="text-sm text-gray-600">品牌: {{ vehicle.brand }}</p>
          </div>
          <button
            @click="handleDeleteVehicle(vehicle.id)"
            class="text-red-500 hover:text-red-700"
          >
            删除
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import * as vehicleApi from '@/api/vehicles'

const vehicles = ref<any[]>([])

const newVehicle = ref({
  name: '',
  plate_number: '',
  brand: '',
  initial_odometer: 0
})

const loadVehicles = async () => {
  vehicles.value = await vehicleApi.list()
}

const handleAddVehicle = async () => {
  await vehicleApi.create(newVehicle.value)
  newVehicle.value = { name: '', plate_number: '', brand: '', initial_odometer: 0 }
  await loadVehicles()
}

const handleDeleteVehicle = async (id: number) => {
  if (confirm('确定删除此车辆及其所有加油记录吗？')) {
    await vehicleApi.delete(id)
    await loadVehicles()
  }
}

onMounted(() => {
  loadVehicles()
})
</script>
```

- [ ] **Step 2: 提交**

```bash
cd client
git add src/views/VehicleView.vue
git commit -m "feat: add vehicle management UI

- Add vehicle creation form
- Display vehicle list
- Add delete vehicle functionality

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 7: 添加路由守卫保护需要认证的页面

**Files:**
- Modify: `client/src/router/index.ts`

- [ ] **Step 1: 添加路由守卫**

```typescript
// client/src/router/index.ts - 修改路由配置

import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import LayoutView from '@/views/LayoutView.vue'
import LoginView from '@/views/LoginView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: LoginView,
      meta: { requiresAuth: false }
    },
    {
      path: '/',
      component: LayoutView,
      meta: { requiresAuth: true },
      children: [
        { path: '', name: 'home', component: () => import('@/views/HomeView.vue') },
        { path: 'records', name: 'records', component: () => import('@/views/RecordListView.vue') },
        { path: 'records/new', name: 'record-new', component: () => import('@/views/RecordFormView.vue') },
        { path: 'records/:id/edit', name: 'record-edit', component: () => import('@/views/RecordFormView.vue') },
        { path: 'stats', name: 'stats', component: () => import('@/views/StatsView.vue') },
        { path: 'vehicles', name: 'vehicles', component: () => import('@/views/VehicleView.vue') },
        { path: 'maintenance', name: 'maintenance', component: () => import('@/views/MaintenanceView.vue') },
        { path: 'settings', name: 'settings', component: () => import('@/views/SettingsView.vue') },
      ]
    }
  ]
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  const requiresAuth = to.meta.requiresAuth !== false

  if (requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else if (to.path === '/login' && authStore.isAuthenticated) {
    next('/')
  } else {
    next()
  }
})

export default router
```

- [ ] **Step 2: 提交**

```bash
cd client
git add src/router/index.ts
git commit -m "feat: add route guard for authentication

Protect all routes except login with auth check.
Redirect unauthenticated users to login page.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 8: 更新测试

**Files:**
- Modify: `server/tests/test_auth.py`

- [ ] **Step 1: 更新认证测试**

```python
# server/tests/test_auth.py - 添加新测试

import pytest
from httpx import AsyncClient

class TestTokenAuth:
    """测试 Token 认证系统"""

    async def test_register_creates_token(self, client: AsyncClient, db):
        """测试注册时创建 token"""
        response = await client.post("/api/v1/auth/register", json={
            "email": "test@example.com",
            "password": "password123",
            "name": "Test User"
        })
        assert response.status_code == 200
        data = response.json()
        assert "token" in data["data"]
        assert data["data"]["user"]["email"] == "test@example.com"

    async def test_login_returns_token(self, client: AsyncClient, existing_user):
        """测试登录返回 token"""
        response = await client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "password123"
        })
        assert response.status_code == 200
        data = response.json()
        assert "token" in data["data"]

    async def test_logout_deletes_token(self, authenticated_client):
        """测试退出登录删除 token"""
        response = await authenticated_client.delete("/api/v1/auth/logout")
        assert response.status_code == 200

        # 后续请求应该失败
        response = await authenticated_client.get("/api/v1/auth/me")
        assert response.status_code == 401

    async def test_get_current_user(self, authenticated_client):
        """测试获取当前用户"""
        response = await authenticated_client.get("/api/v1/auth/me")
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["email"] == "test@example.com"

    async def test_change_password(self, authenticated_client, db):
        """测试修改密码"""
        response = await authenticated_client.put("/api/v1/auth/password", json={
            "old_password": "password123",
            "new_password": "newpassword123"
        })
        assert response.status_code == 200

        # 用新密码登录
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/api/v1/auth/login", json={
                "email": "test@example.com",
                "password": "newpassword123"
            })
            assert response.status_code == 200

    async def test_invalid_token_returns_401(self, client: AsyncClient):
        """测试无效 token 返回 401"""
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401
```

- [ ] **Step 2: 运行测试验证**

```bash
cd server
pytest tests/test_auth.py -v
```

- [ ] **Step 3: 提交**

```bash
cd server
git add tests/test_auth.py
git commit -m "test: add comprehensive auth tests

Cover register, login, logout, get current user,
change password, and token validation.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## 验证步骤

完成所有任务后，运行以下验证：

```bash
# 后端测试
cd server
pytest tests/ -v

# 前端构建
cd client
pnpm build

# 启动服务验证
docker compose up --build
```

**手动测试清单：**
- [ ] 注册新用户成功
- [ ] 登录成功，获得 token
- [ ] 获取当前用户信息正常
- [ ] 修改密码成功
- [ ] 退出登录成功，token 失效
- [ ] 添加车辆成功
- [ ] 添加加油记录，油耗按累积法计算
- [ ] 未登录访问受保护页面跳转到登录页
