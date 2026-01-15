<template>
  <div class="admin-dashboard-container">
    <el-container>
      <el-header class="header">
        <div class="header-left">
          <img src="/vite.svg" alt="logo" class="logo" />
          <div class="title-container">
            <h1 class="app-name">Hanwen Study</h1>
            <span class="divider">|</span>
            <span class="page-title">管理后台</span>
          </div>
        </div>
        <div class="header-right">
          <span class="admin-name">管理员: {{ authStore.user?.username }}</span>
          <el-button type="danger" plain size="small" @click="logout">退出登录</el-button>
        </div>
      </el-header>
      <el-main>
        <el-card shadow="hover" class="users-card">
          <template #header>
             <div class="card-header">
                <h3>用户列表</h3>
                <el-button type="primary" size="small" @click="fetchUsers">刷新列表</el-button>
             </div>
          </template>
          
          <el-table :data="users" style="width: 100%" v-loading="loading" stripe border>
            <el-table-column type="expand">
              <template #default="props">
                <div class="user-tasks-container">
                  <h4>{{ props.row.username }} 的任务进度:</h4>
                  <el-table :data="props.row.tasks" style="width: 100%" class="nested-table">
                    <el-table-column prop="title" label="任务名称" />
                    <el-table-column label="总集数" prop="total_episodes" width="100"/>
                    <el-table-column label="已看集数" prop="completed_episodes" width="100"/>
                    <el-table-column label="进度">
                      <template #default="scope">
                        <el-progress 
                          :percentage="calculatePercentage(scope.row)" 
                          :status="calculatePercentage(scope.row) === 100 ? 'success' : ''"
                        />
                      </template>
                    </el-table-column>
                    <el-table-column label="操作" width="120">
                      <template #default="scope">
                        <el-button size="small" type="primary" link @click="openEditTaskDialog(scope.row)">修改进度</el-button>
                      </template>
                    </el-table-column>
                  </el-table>
                  <el-empty v-if="!props.row.tasks || props.row.tasks.length === 0" description="暂无任务" :image-size="60"></el-empty>
                </div>
              </template>
            </el-table-column>
            
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="username" label="用户名" />
            <el-table-column prop="is_active" label="状态" width="100">
               <template #default="scope">
                 <el-tag :type="scope.row.is_active ? 'success' : 'danger'">{{ scope.row.is_active ? '活跃' : '禁用' }}</el-tag>
               </template>
            </el-table-column>
            <el-table-column label="管理员" width="100">
               <template #default="scope">
                 <el-tag v-if="scope.row.is_admin" type="warning">是</el-tag>
                 <span v-else>否</span>
               </template>
            </el-table-column>
            <el-table-column label="操作" width="150" align="center">
               <template #default="scope">
                  <el-button link type="primary" size="small" @click="viewUserTasks(scope.row)">查看详细</el-button>
               </template>
            </el-table-column>
          </el-table>
        </el-card>

        <!-- Edit Task Dialog -->
        <el-dialog v-model="showEditDialog" title="修改用户任务进度" width="90%" style="max-width: 400px">
          <el-form :model="currentTask" label-width="100px">
            <el-form-item label="任务名称">
              <el-input v-model="currentTask.title" disabled />
            </el-form-item>
            <el-form-item label="已看集数">
              <el-input-number v-model="currentTask.completed_episodes" :min="0" :max="currentTask.total_episodes" />
            </el-form-item>
          </el-form>
           <div class="dialog-tips">注: 最大集数为 {{ currentTask.total_episodes }}</div>
          <template #footer>
            <span class="dialog-footer">
              <el-button @click="showEditDialog = false">取消</el-button>
              <el-button type="primary" @click="saveTaskProgress">保存修改</el-button>
            </span>
          </template>
        </el-dialog>

      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from '../axios';
import { useAuthStore } from '../stores/auth';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';

const authStore = useAuthStore();
const router = useRouter();
const users = ref([]);
const loading = ref(false);

const showEditDialog = ref(false);
const currentTask = ref({ id: null, title: '', completed_episodes: 0, total_episodes: 0 });

const fetchUsers = async () => {
  loading.value = true;
  try {
    const response = await axios.get('/admin/users');
    users.value = response.data.map(user => ({...user, tasks: []})); // Initialize tasks array
    
    // Optimistically fetch tasks for all users to populate the expand rows naturally or fetch on expand
    // Simplified: fetch tasks for each user one by one (or could implement bulk fetch API)
    for (const user of users.value) {
        fetchUserTasks(user);
    }

  } catch (error) {
    ElMessage.error('获取用户列表失败');
    console.error(error);
  } finally {
    loading.value = false;
  }
};

const fetchUserTasks = async (user) => {
    try {
        const res = await axios.get(`/admin/users/${user.id}/tasks`);
        user.tasks = res.data;
    } catch (err) {
        console.error(`Failed to fetch tasks for user ${user.id}`, err);
    }
}

const viewUserTasks = (user) => {
    // Just re-fetch to be sure
    fetchUserTasks(user);
    // Programmatically expand row if supported by element-plus table ref, or just let user click expand arrow
    ElMessage.info(`已刷新 ${user.username} 的数据`);
};


const openEditTaskDialog = (task) => {
    currentTask.value = { ...task };
    showEditDialog.value = true;
};

const saveTaskProgress = async () => {
    try {
        await axios.put(`/admin/tasks/${currentTask.value.id}`, {
            completed_episodes: currentTask.value.completed_episodes
        });
        showEditDialog.value = false;
        ElMessage.success('更新成功');
        fetchUsers(); // Refresh all data
    } catch (error) {
        ElMessage.error('更新失败');
        console.error(error);
    }
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
  fetchUsers();
});
</script>

<style scoped>
.admin-dashboard-container {
  min-height: 100vh;
  background-color: #f0f2f5;
}

.header {
  background-color: #001529;
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  box-shadow: 0 1px 4px rgba(0,21,41,.08);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 15px;
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
  color: #fff;
  font-size: 20px;
  font-weight: bold;
  margin: 0;
}

.divider {
  color: rgba(255,255,255,0.3);
  font-size: 18px;
}

.page-title {
  color: rgba(255,255,255,0.7);
  font-size: 14px;
  margin: 0;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 15px;
}

.admin-name {
    font-size: 14px;
    opacity: 0.9;
}

.users-card {
    margin-top: 20px;
}

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.card-header h3 {
    margin: 0;
    font-size: 18px;
    color: #333;
}

.user-tasks-container {
    padding: 20px;
    background-color: #fcfcfc;
    border-radius: 4px;
}

.user-tasks-container h4 {
    margin-top: 0;
    margin-bottom: 15px;
    color: #666;
}

.nested-table {
    border-radius: 4px;
    overflow: hidden;
}

.dialog-tips {
    margin-top: 10px;
    font-size: 12px;
    color: #999;
    text-align: right;
}

@media screen and (max-width: 768px) {
  .header {
    flex-wrap: wrap; /* Allow wrapping */
    height: auto !important; 
    padding: 10px;
    gap: 10px;
  }
  
  .header-left, .header-right {
    width: 100%;
    justify-content: space-between;
  }

  .header-left {
    margin-bottom: 5px;
  }

  /* Make table scrollable container if needed, though el-table handles it */
  .el-main {
      padding: 10px;
  }
  
  .users-card .el-card__body {
      padding: 10px;
  }
}
</style>
