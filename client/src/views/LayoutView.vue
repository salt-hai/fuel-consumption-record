<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const tabs = [
  { name: '首页', path: '/', icon: 'home-o' },
  { name: '记录', path: '/records', icon: 'bar-chart-o' },
  { name: '统计', path: '/stats', icon: 'chart-trending-o' },
  { name: '我的', path: '/settings', icon: 'user-o' },
]

const activeTab = ref(0)

watch(() => router.currentRoute.value.path, (path) => {
  const index = tabs.findIndex(t => path.startsWith(t.path))
  if (index !== -1) {
    activeTab.value = index
  }
}, { immediate: true })

const onTabChange = (index: number) => {
  router.push(tabs[index].path)
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
