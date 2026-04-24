<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

const tabs = [
  { name: '首页', path: '/', icon: 'home-o' },
  { name: '记录', path: '/records', icon: 'bar-chart-o' },
  { name: '统计', path: '/stats', icon: 'chart-trending-o' },
  { name: '我的', path: '/settings', icon: 'user-o' },
]

const activeTab = ref(0)

// 根据当前路由更新激活的 tab
const updateActiveTab = () => {
  const path = route.path
  const index = tabs.findIndex(t => path === t.path || path.startsWith(t.path + '/'))
  if (index !== -1) {
    activeTab.value = index
  }
}

// 监听路由变化
watch(() => route.path, updateActiveTab, { immediate: true })

// 处理 tab 切换
const onTabChange = (index: number) => {
  const targetPath = tabs[index].path
  // 如果当前路径已经匹配目标路径，不重复跳转
  if (route.path !== targetPath && !route.path.startsWith(targetPath + '/')) {
    router.push(targetPath)
  }
}
</script>

<template>
  <div class="layout-container">
    <router-view />

    <van-tabbar v-model="activeTab" @change="onTabChange" class="tab-bar">
      <van-tabbar-item
        v-for="tab in tabs"
        :key="tab.path"
        :icon="tab.icon"
      >
        {{ tab.name }}
      </van-tabbar-item>
    </van-tabbar>
  </div>
</template>

<style scoped>
.layout-container {
  min-height: 100vh;
  padding-bottom: 50px;
}

.tab-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
}
</style>
