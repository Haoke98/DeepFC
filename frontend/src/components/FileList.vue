<template>
  <div class="file-manager">
    <!-- 磁盘使用情况 -->
    <div class="disk-usage">
      <el-card>
        <template #header>
          <div class="disk-header">
            <span>磁盘使用情况</span>
            <el-button type="primary" link @click="updateDiskUsage">
              刷新
            </el-button>
          </div>
        </template>
        <div class="disk-info">
          <el-progress 
            type="dashboard"
            :percentage="diskUsage.percentage || 0"
            :color="diskUsageColor"
          >
            <template #default="{ percentage }">
              <div class="progress-content">
                <div>{{ (percentage || 0).toFixed(1) }}%</div>
                <div class="usage-details">
                  <div>已用: {{ formatSize(diskUsage.used) }}</div>
                  <div>可用: {{ formatSize(diskUsage.free) }}</div>
                  <div>总计: {{ formatSize(diskUsage.total) }}</div>
                </div>
              </div>
            </template>
          </el-progress>
        </div>
      </el-card>
    </div>

    <!-- 控制栏 -->
    <div class="controls">
      <el-select v-model="scanPath" placeholder="选择扫描路径" class="path-select">
        <el-option
          v-for="item in pathOptions"
          :key="item.value"
          :label="item.label"
          :value="item.value"
        />
      </el-select>
      
      <el-input
        v-model="customPath"
        placeholder="输入自定义路径"
        class="custom-path"
        :disabled="scanPath !== 'custom'"
      />

      <el-select v-model="groupBy" placeholder="分组方式">
        <el-option label="按大小排序" value="size" />
        <el-option label="按账号分组" value="account" />
        <el-option label="按类型分组" value="type" />
      </el-select>
      
      <el-input-number 
        v-model="minSize" 
        :min="1"
        :max="1000"
        label="最小文件大小(MB)"
      />
      
      <el-button type="primary" @click="scanFiles">
        扫描文件
      </el-button>
    </div>

    <!-- 文件列表 -->
    <div class="file-list">
      <el-table :data="files" style="width: 100%">
        <el-table-column prop="type" label="类型" width="100" />
        <el-table-column prop="size" label="大小" width="120">
          <template #default="scope">
            {{ formatSize(scope.row.size) }}
          </template>
        </el-table-column>
        <el-table-column prop="relative_path" label="路径" />
        <el-table-column label="操作" width="250">
          <template #default="scope">
            <el-button-group>
              <el-button 
                @click="handleAction('preview', scope.row)"
                :icon="View"
                size="small">
                预览
              </el-button>
              <el-button 
                @click="handleAction('reveal', scope.row)"
                :icon="Folder"
                size="small">
                打开目录
              </el-button>
              <el-button 
                @click="handleAction('delete', scope.row)"
                :icon="Delete"
                type="danger"
                size="small">
                删除
              </el-button>
            </el-button-group>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { View, Folder, Delete } from '@element-plus/icons-vue'
import axios from 'axios'

const files = ref([])
const groupBy = ref('size')
const minSize = ref(10)
const scanPath = ref('wechat')
const customPath = ref('')

const pathOptions = [
  {
    label: '微信历史消息',
    value: 'wechat',
  },
  {
    label: 'MacOS照片库',
    value: 'photos',
  },
  {
    label: 'Yarn缓存',
    value: 'yarn',
  },
  {
    label: 'JetBrains缓存',
    value: 'jetbrains',
  },
  {
    label: 'Lark缓存',
    value: 'lark',
  },
  {
    label: 'PIP缓存',
    value: 'pip',
  },
  {
    label: 'Google缓存',
    value: 'google',
  },
  {
    label: '自定义路径',
    value: 'custom',
  },
]

const formatSize = (bytes) => {
  if (bytes === undefined || bytes === null) {
    return '0 B'
  }

  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  let size = Number(bytes)
  let unitIndex = 0
  
  if (isNaN(size)) {
    return '0 B'
  }
  
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024
    unitIndex++
  }
  
  return `${size.toFixed(2)} ${units[unitIndex]}`
}

// 创建 axios 实例
const api = axios.create({
  baseURL: 'http://localhost:5173',
  withCredentials: true
})

const diskUsage = ref({
  total: 0,
  used: 0,
  free: 0,
  percentage: 0
})

const diskUsageColor = computed(() => {
  const percentage = diskUsage.value.percentage
  if (percentage < 60) return '#67C23A'
  if (percentage < 80) return '#E6A23C'
  return '#F56C6C'
})

const updateDiskUsage = async () => {
  try {
    const { data } = await api.get('/api/disk-usage')
    diskUsage.value = {
      total: data.total,
      used: data.used,
      free: data.free,
      percentage: data.usage_percent
    }
  } catch (error) {
    console.error('Failed to get disk usage:', error)
    ElMessage.error('获取磁盘使用情况失败')
  }
}

const scanFiles = async () => {
  try {
    const path = scanPath.value === 'custom' ? customPath.value : scanPath.value
    await api.get(`/api/scan?min_size=${minSize.value}&path=${path}`)
    await loadFiles()
    await updateDiskUsage()
  } catch (error) {
    console.error('Scan error:', error)
    ElMessage.error('扫描失败')
  }
}

const loadFiles = async () => {
  try {
    const { data } = await api.get(`/api/files?group_by=${groupBy.value}`)
    files.value = data
  } catch (error) {
    console.error('Load files error:', error)
    ElMessage.error('加载文件列表失败')
  }
}

const handleAction = async (action, file) => {
  try {
    await api.post(`/api/file/action/${action}`, {
      file_path: file.path,
      base_path: scanPath.value
    })
    
    if (action === 'delete') {
      await loadFiles()
      ElMessage.success('删除成功')
    }
  } catch (error) {
    console.error('Action error:', error.response?.data || error)
    ElMessage.error(`操作失败: ${error.response?.data?.detail || '未知错误'}`)
  }
}

onMounted(() => {
  loadFiles()
  updateDiskUsage()
})
</script>

<style scoped>
.file-manager {
  padding: 20px;
}

.controls {
  margin-bottom: 20px;
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.path-select {
  width: 200px;
}

.custom-path {
  width: 300px;
}

.file-list {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.1);
}

.disk-usage {
  margin-bottom: 20px;
}

.disk-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.disk-info {
  display: flex;
  justify-content: center;
  padding: 20px;
}

.progress-content {
  text-align: center;
}

.usage-details {
  margin-top: 10px;
  font-size: 12px;
  color: #666;
}
</style> 