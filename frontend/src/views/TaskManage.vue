<template>
  <div class="task-manage-container">
    <el-container>
      <el-header class="header">
        <div class="header-branding">
          <img src="/vite.svg" alt="logo" class="logo" />
          <div class="title-container">
            <h1 class="app-name">Hanwen Study</h1>
            <span class="divider">|</span>
            <span class="page-title">学习任务管理</span>
          </div>
        </div>
        <div class="header-center">
            <el-menu mode="horizontal" :default-active="activeIndex" router :ellipsis="false" class="nav-menu">
                <el-menu-item index="/">数据看板</el-menu-item>
                <el-menu-item index="/tasks">任务管理</el-menu-item>
            </el-menu>
        </div>
        <div class="header-right">
          <span class="username">你好, {{ authStore.user?.username }}</span>
          <el-button type="danger" plain size="small" @click="logout">退出登录</el-button>
        </div>
      </el-header>
      <el-main>
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span class="section-title">学习任务列表</span>
              <el-button type="primary" @click="showAddTaskDialog = true">+ 创建新任务</el-button>
            </div>
          </template>
          
          <el-table :data="tasks" style="width: 100%" v-loading="loading" stripe>
            <el-table-column prop="title" label="任务名称" />
            <el-table-column prop="total_episodes" label="总集数" width="100" />
            <el-table-column prop="completed_episodes" label="已完成" width="100" />
            <el-table-column label="进度" width="180">
                <template #default="scope">
                    <el-progress 
                      :percentage="calculatePercentage(scope.row)" 
                      :status="calculatePercentage(scope.row) === 100 ? 'success' : ''"
                    />
                </template>
            </el-table-column>
            <el-table-column label="开始时间" width="150">
                <template #default="scope">
                    {{ formatDate(scope.row.start_date) }}
                </template>
            </el-table-column>
             <el-table-column label="预计完成" width="150">
                <template #default="scope">
                    {{ formatDate(scope.row.estimated_end_date) }}
                </template>
            </el-table-column>
            <el-table-column label="标记" width="80" align="center">
                <template #default="scope">
                    <div :style="{width: '20px', height: '20px', borderRadius: '4px', backgroundColor: scope.row.color || '#409EFF', margin: '0 auto'}"></div>
                </template>
            </el-table-column>
             <el-table-column label="链接" width="80" align="center">
                <template #default="scope">
                    <el-link v-if="scope.row.url" :href="scope.row.url" target="_blank" type="primary">跳转</el-link>
                </template>
            </el-table-column>
            <el-table-column label="操作" width="200" align="center">
              <template #default="scope">
                <el-button size="small" @click="openEditDialog(scope.row)">编辑</el-button>
                 <el-popconfirm title="确定要删除这个任务吗?" @confirm="deleteTask(scope.row.id)">
                    <template #reference>
                        <el-button size="small" type="danger">删除</el-button>
                    </template>
                  </el-popconfirm>
              </template>
            </el-table-column>
          </el-table>
        </el-card>

        <!-- Add/Edit Task Dialog -->
        <el-dialog v-model="showDialog" :title="isEditMode ? '编辑任务' : '创建新任务'" width="90%" style="max-width: 500px">
          <el-form :model="taskForm" label-width="100px">
            <el-form-item label="任务名称">
              <el-input v-model="taskForm.title" placeholder="例如: Python Django 教程" />
            </el-form-item>
            <el-form-item label="总集数">
              <el-input-number v-model="taskForm.total_episodes" :min="1" />
            </el-form-item>
            <el-form-item label="已看集数" v-if="isEditMode">
               <el-input-number v-model="taskForm.completed_episodes" :min="0" :max="taskForm.total_episodes" />
            </el-form-item>
            <el-form-item label="开始时间">
                <el-date-picker
                    v-model="taskForm.start_date"
                    type="date"
                    placeholder="选择日期"
                    style="width: 100%"
                />
            </el-form-item>
            <el-form-item label="预计完成">
                <el-date-picker
                    v-model="taskForm.estimated_end_date"
                    type="date"
                    placeholder="选择日期"
                    style="width: 100%"
                />
            </el-form-item>
             <el-form-item label="网课链接">
              <el-input v-model="taskForm.url" placeholder="https://example.com" />
            </el-form-item>
             <el-form-item label="颜色标记">
               <el-color-picker v-model="taskForm.color" :predefine="predefineColors" />
            </el-form-item>
          </el-form>
          <template #footer>
            <span class="dialog-footer">
              <el-button @click="showDialog = false">取消</el-button>
              <el-button type="primary" @click="submitTask">确认</el-button>
            </span>
          </template>
        </el-dialog>

      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, reactive } from 'vue';
import { useAuthStore } from '../stores/auth';
import { useRouter, useRoute } from 'vue-router';
import axios from '../axios';
import { ElMessage } from 'element-plus';
import dayjs from 'dayjs';

const authStore = useAuthStore();
const router = useRouter();
const route = useRoute();
const activeIndex = ref(route.path);

const tasks = ref([]);
const loading = ref(false);
const showDialog = ref(false);
const isEditMode = ref(false);

const predefineColors = ref([
  '#409EFF',
  '#67C23A',
  '#E6A23C',
  '#F56C6C',
  '#909399',
  '#bf209f'
]);

// Use a ref for showDialog to control visibility, but specific methods to open
const showAddTaskDialog = computed({
    get: () => showDialog.value && !isEditMode.value,
    set: (val) => { showDialog.value = val; if(val) resetForm(); isEditMode.value = false; }
});

const taskForm = reactive({
    id: null,
    title: '',
    total_episodes: 10,
    completed_episodes: 0,
    start_date: null,
    estimated_end_date: null,
    url: '',
    color: '#409EFF'
});

const resetForm = () => {
    taskForm.id = null;
    taskForm.title = '';
    taskForm.total_episodes = 10;
    taskForm.completed_episodes = 0;
    taskForm.start_date = null;
    taskForm.estimated_end_date = null;
    taskForm.url = '';
    taskForm.color = '#409EFF';
};

const fetchTasks = async () => {
  loading.value = true;
  try {
    const response = await axios.get('/tasks/');
    tasks.value = response.data;
  } catch (error) {
    console.error('Failed to fetch tasks', error);
  } finally {
    loading.value = false;
  }
};

const openEditDialog = (task) => {
    isEditMode.value = true;
    taskForm.id = task.id;
    taskForm.title = task.title;
    taskForm.total_episodes = task.total_episodes;
    taskForm.completed_episodes = task.completed_episodes;
    taskForm.start_date = task.start_date;
    taskForm.estimated_end_date = task.estimated_end_date;
    taskForm.url = task.url;
    taskForm.color = task.color || '#409EFF';
    showDialog.value = true;
};

const submitTask = async () => {
    if (!taskForm.title) {
        ElMessage.warning({ message: '请输入任务名称', duration: 500 });
        return;
    }
    
    try {
        const payload = { ...taskForm };
        // Clean up empty dates if necessary
        if (!payload.start_date) delete payload.start_date;
        if (!payload.estimated_end_date) delete payload.estimated_end_date;

        if (isEditMode.value) {
            await axios.put(`/tasks/${taskForm.id}`, payload);
            ElMessage.success({ message: '更新成功', duration: 500 });
        } else {
            await axios.post('/tasks/', payload);
            ElMessage.success({ message: '创建成功', duration: 500 });
        }
        showDialog.value = false;
        fetchTasks();
    } catch (error) {
        ElMessage.error({ message: '操作失败', duration: 500 });
        console.error(error);
    }
};

const deleteTask = async (taskId) => {
    try {
        await axios.delete(`/tasks/${taskId}`);
        ElMessage.success({ message: '删除成功', duration: 500 });
        fetchTasks();
    } catch (error) {
        ElMessage.error({ message: '删除失败', duration: 500 });
    }
};

const formatDate = (dateStr) => {
    if (!dateStr) return '-';
    return dayjs(dateStr).format('YYYY-MM-DD');
};

const calculatePercentage = (task) => {
  if (task.total_episodes === 0) return 0;
  return Math.floor((task.completed_episodes / task.total_episodes) * 100);
};

const logout = () => {
  authStore.logout();
  router.push('/login');
};

onMounted(() => {
  fetchTasks();
});
</script>

<style scoped>
.task-manage-container {
  min-height: 100vh;
  background-color: #f5f7fa;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #fff;
  padding: 0 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  border-radius: 4px;
  margin-bottom: 20px;
}

.header-branding {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 250px;
}

.logo {
  height: 32px;
  width: 32px;
}

.title-container {
  display: flex;
  align-items: baseline;
  gap: 10px;
}

.app-name {
  color: #303133;
  font-size: 22px;
  font-weight: bold;
  margin: 0;
}

.divider {
  color: #dcdfe6;
  font-size: 20px;
}

.page-title {
  color: #909399;
  font-size: 16px;
  margin: 0;
}

.header-center {
    flex: 1;
    display: flex;
    justify-content: center;
}

.nav-menu {
    border-bottom: none !important;
    background-color: transparent !important;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 15px;
  min-width: 200px;
  justify-content: flex-end;
}

.username {
  color: #606266;
  font-size: 14px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-title {
  font-weight: bold;
  font-size: 16px;
}

/* Response Design */
@media screen and (max-width: 768px) {
  .header {
    padding: 10px 15px;
    flex-wrap: wrap;
    height: auto !important;
    gap: 10px;
  }
  
  .header-branding {
    min-width: auto;
    width: 100%;
    justify-content: center;
    margin-bottom: 5px;
  }

  .header-center {
    width: 100%;
    order: 3;
    margin-top: 5px;
  }

  .header-right {
     min-width: auto;
    width: 100%;
    justify-content: center;
    margin-bottom: 5px;
  }

  .nav-menu {
      width: 100%;
      display: flex;
      justify-content: center;
  }

  /* Make table scrollable/compact if needed, though el-table handles scroll */
  .el-main {
      padding: 10px;
  }
}
</style>
