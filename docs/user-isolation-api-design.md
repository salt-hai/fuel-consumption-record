# 用户数据隔离 API 设计文档

## 问题分析

### 当前状态
- ✅ 有完整的用户认证系统（注册、登录、token）
- ❌ 所有业务 API 没有认证保护
- ❌ Vehicle 模型缺少 user_id，无法实现数据隔离

### 目标
1. 所有业务 API 需要 token 认证
2. 用户只能访问自己的数据（车辆、记录、统计等）

---

## 数据库变更

### 1. Vehicle 表添加 user_id

```sql
ALTER TABLE vehicles ADD COLUMN user_id INTEGER REFERENCES users(id);

-- 为现有数据设置默认用户（假设第一个用户 id=1）
UPDATE vehicles SET user_id = 1 WHERE user_id IS NULL;

-- 设置 NOT NULL 约束
ALTER TABLE vehicles ALTER COLUMN user_id SET NOT NULL;
```

### 模型更新

```python
# models/vehicle.py
class Vehicle(Base):
    # ... 现有字段 ...
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    # 关系
    user = relationship("User", back_populates="vehicles")

# models/user.py
class User(Base):
    # ... 现有字段 ...

    # 关系
    vehicles = relationship("Vehicle", back_populates="user")
```

---

## API 变更

### 认证流程

```
1. POST /v1/auth/register → 注册，返回 token
2. POST /v1/auth/login    → 登录，返回 token
3. 后续所有请求携带: Authorization: Bearer <token>
```

### API 保护策略

| 路由 | 认证要求 | 数据隔离 |
|------|---------|---------|
| POST /v1/auth/register | ❌ 否 | - |
| POST /v1/auth/login | ❌ 否 | - |
| POST /v1/auth/logout | ✅ 是 | 当前用户的 token |
| GET /v1/auth/me | ✅ 是 | 当前用户 |
| PUT /v1/auth/password | ✅ 是 | 当前用户 |
| **车辆管理** |||
| GET /v1/vehicles/ | ✅ 是 | 仅当前用户的车辆 |
| POST /v1/vehicles/ | ✅ 是 | 关联到当前用户 |
| PUT /v1/vehicles/{id} | ✅ 是 | 只能操作自己的车辆 |
| DELETE /v1/vehicles/{id} | ✅ 是 | 只能删除自己的车辆 |
| **加油记录** |||
| GET /v1/records/ | ✅ 是 | 仅当前用户车辆的记录 |
| POST /v1/records/ | ✅ 是 | 只能添加到自己的车辆 |
| PUT /v1/records/{id} | ✅ 是 | 只能操作自己的车辆记录 |
| DELETE /v1/records/{id} | ✅ 是 | 只能删除自己的车辆记录 |
| **统计** |||
| GET /v1/stats/summary | ✅ 是 | 仅当前用户数据 |
| GET /v1/stats/trend | ✅ 是 | 仅当前用户数据 |
| GET /v1/stats/monthly | ✅ 是 | 仅当前用户数据 |

---

## 实现细节

### 1. 数据验证辅助函数

```python
# utils/auth.py (新增)

async def get_user_vehicle(vehicle_id: int, user: User, db: AsyncSession) -> Vehicle:
    """获取属于当前用户的车辆，不存在则返回 404"""
    result = await db.execute(
        select(Vehicle).where(Vehicle.id == vehicle_id, Vehicle.user_id == user.id)
    )
    vehicle = result.scalar_one_or_none()
    if not vehicle:
        raise HTTPException(status_code=404, detail="车辆不存在")
    return vehicle

async def get_user_record(record_id: int, user: User, db: AsyncSession) -> FuelRecord:
    """获取属于当前用户的记录，不存在则返回 404"""
    result = await db.execute(
        select(FuelRecord)
        .join(Vehicle, FuelRecord.vehicle_id == Vehicle.id)
        .where(FuelRecord.id == record_id, Vehicle.user_id == user.id)
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    return record
```

### 2. API 变更示例

#### 车辆列表
```python
# 变更前
@router.get("/")
async def get_vehicles(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Vehicle).order_by(Vehicle.created_at.desc()))
    vehicles = result.scalars().all()
    return success_response([VehicleResponse.model_validate(v) for v in vehicles])

# 变更后
@router.get("/")
async def get_vehicles(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Vehicle)
        .where(Vehicle.user_id == current_user.id)
        .order_by(Vehicle.created_at.desc())
    )
    vehicles = result.scalars().all()
    return success_response([VehicleResponse.model_validate(v) for v in vehicles])
```

#### 创建车辆
```python
# 变更前
@router.post("/")
async def create_vehicle(data: VehicleCreate, db: AsyncSession = Depends(get_db)):
    vehicle = Vehicle(**data.model_dump())
    db.add(vehicle)
    await db.commit()
    await db.refresh(vehicle)
    return success_response(VehicleResponse.model_validate(vehicle), "添加成功")

# 变更后
@router.post("/")
async def create_vehicle(
    data: VehicleCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    vehicle = Vehicle(**data.model_dump(), user_id=current_user.id)
    db.add(vehicle)
    await db.commit()
    await db.refresh(vehicle)
    return success_response(VehicleResponse.model_validate(vehicle), "添加成功")
```

#### 更新车辆
```python
# 变更前
@router.put("/{vehicle_id}/")
async def update_vehicle(vehicle_id: int, data: VehicleUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Vehicle).where(Vehicle.id == vehicle_id))
    vehicle = result.scalar_one_or_none()
    if not vehicle:
        raise HTTPException(status_code=404, detail="车辆不存在")
    # ... 更新逻辑 ...

# 变更后
@router.put("/{vehicle_id}/")
async def update_vehicle(
    vehicle_id: int,
    data: VehicleUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    vehicle = await get_user_vehicle(vehicle_id, current_user, db)
    # ... 更新逻辑 ...
```

---

## 前端变更

### 1. API 请求拦截器

```typescript
// client/src/api/index.ts

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE || 'http://localhost:8000',
  timeout: 15000,
})

// 请求拦截器：自动添加 token
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截器：处理 401 未授权
apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)
```

### 2. 认证状态管理

```typescript
// client/src/stores/auth.ts

import { defineStore } from 'pinia'
import { ref } from 'vue'
import * as authApi from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('auth_token'))
  const user = ref<any>(null)
  const isAuthenticated = computed(() => !!token.value)

  async function login(email: string, password: string) {
    const response = await authApi.login({ email, password })
    token.value = response.data.token
    user.value = response.data.user
    localStorage.setItem('auth_token', response.data.token)
  }

  async function logout() {
    await authApi.logout()
    token.value = null
    user.value = null
    localStorage.removeItem('auth_token')
  }

  return { token, user, isAuthenticated, login, logout }
})
```

### 3. 路由守卫

```typescript
// client/src/router/index.ts

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  // 需要认证的页面
  const requiresAuth = to.meta.requiresAuth

  if (requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else if (to.path === '/login' && authStore.isAuthenticated) {
    next('/')
  } else {
    next()
  }
})
```

---

## 迁移步骤

1. **数据库迁移**
   - 创建迁移脚本添加 user_id
   - 为现有数据分配默认用户

2. **后端 API**
   - 更新 Vehicle 模型
   - 添加辅助验证函数
   - 更新所有路由添加认证依赖

3. **前端**
   - 更新 API 拦截器
   - 添加认证状态管理
   - 添加路由守卫
   - 更新登录/注册流程

4. **测试**
   - 测试数据隔离（用户 A 不能访问用户 B 的数据）
   - 测试 token 过期处理
   - 测试跨设备登录

---

## 错误处理

| 错误 | HTTP 状态 | 处理 |
|------|----------|------|
| 无 token | 401 | 跳转登录页 |
| 无效 token | 401 | 清除本地 token，跳转登录 |
| 账户禁用 | 403 | 提示账户已被禁用 |
| 访问他人数据 | 404 | 资源不存在（统一处理） |
