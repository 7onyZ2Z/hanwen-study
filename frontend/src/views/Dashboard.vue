<template>
  <div class="dashboard-container">
    <el-container>
      <el-header class="header">
        <div class="header-branding">
          <img src="/vite.svg" alt="logo" class="logo" />
          <div class="title-container">
            <h1 class="app-name">Hanwen Study</h1>
            <span class="divider">|</span>
            <span class="page-title">数据看板</span>
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
      
      <el-main class="main-content">
        <div class="dashboard-layout">
          <!-- Task List Section (Left) -->
          <div class="task-grid">
              <div 
                  v-for="task in sortedTasks" 
                  :key="task.id" 
                  class="task-card"
                  :style="{ 
                      backgroundColor: task.color || '#409EFF',
                      boxShadow: `0 8px 16px -4px ${task.color}80`
                  }"
              >
                  <div class="card-content">
                      <div class="card-left">
                          <div class="title-row">
                             <h3 class="task-title">{{ task.title }}</h3>
                             <el-icon v-if="task.completed_episodes >= task.total_episodes" class="completed-icon"><Check /></el-icon>
                          </div>
                          <div class="progress-info">
                              <span class="episode-count">{{ task.completed_episodes }} / {{ task.total_episodes }} 集</span>
                          </div>
                          <!-- Custom Progress Bar -->
                          <div class="progress-track">
                              <div 
                                  class="progress-fill" 
                                  :style="{ width: (task.completed_episodes / task.total_episodes * 100) + '%' }"
                              ></div>
                          </div>
                      </div>
                      
                      <div class="card-right">
                          <div class="control-group">
                             <el-popover
                                placement="bottom"
                                :width="200"
                                trigger="click"
                              >
                                <template #reference>
                                  <el-button 
                                      circle 
                                      :icon="Edit" 
                                      size="small" 
                                      class="control-btn"
                                      title="更新进度"
                                  />
                                </template>
                                <div class="popover-content">
                                    <p class="popover-title">更新进度</p>
                                    <div class="popover-input-group">
                                        <el-input-number 
                                          v-model="task.completed_episodes" 
                                          :min="0" 
                                          :max="task.total_episodes" 
                                          size="small"
                                          :step="1"
                                          step-strictly
                                          @change="(val) => handleProgressChange(task, val)"
                                          style="width: 100%"
                                        />
                                    </div>
                                </div>
                              </el-popover>
                          </div>
                          <el-button 
                              v-if="task.url"
                              circle 
                              :icon="Link" 
                              size="large" 
                              class="link-btn"
                              @click="openUrl(task.url)"
                              title="前往网课"
                          />
                      </div>
                  </div>
              </div>
              <!-- Empty State -->
              <div v-if="tasks.length === 0" class="empty-state">
                  <p>还没有任务，去「任务管理」添加吧</p>
                  <el-button type="primary" @click="router.push('/tasks')">前往添加</el-button>
              </div>
          </div>

          <!-- Side Panel Section (Right: Stats + Chart) -->
          <div class="side-panel">
              <!-- Stats Card -->
              <div class="stats-card">
                 <div class="stats-header">
                     <div class="stats-title-row">
                        <el-icon class="stats-icon"><Calendar /></el-icon>
                        <h3>打卡记录</h3>
                     </div>
                     <el-button 
                        :type="hasClockedInToday ? 'success' : 'primary'" 
                        size="default" 
                        round 
                        @click="clockIn" 
                        :disabled="hasClockedInToday"
                        class="clock-btn"
                     >
                        {{ hasClockedInToday ? '今日已打卡' : '立即打卡' }}
                     </el-button>
                 </div>
                 <div class="stats-grid">
                     <div class="stat-item">
                         <span class="stat-value">{{ authStore.user?.total_study_days || 0 }}</span>
                         <span class="stat-label">总天数</span>
                     </div>
                     <div class="stat-divider"></div>
                     <div class="stat-item">
                         <span class="stat-value">{{ authStore.user?.consecutive_study_days || 0 }}</span>
                         <span class="stat-label">连续打卡</span>
                     </div>
                 </div>
              </div>

              <!-- Chart Card -->
              <div class="chart-card">
                  <div ref="chartDom" class="chart-container"></div>
              </div>
          </div>
        </div>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue';
import { useAuthStore } from '../stores/auth';
import { useRouter, useRoute } from 'vue-router';
import axios from '../axios';
import * as echarts from 'echarts';
import { Link, Edit, Check, Calendar } from '@element-plus/icons-vue';
import { ElMessage } from 'element-plus';

const authStore = useAuthStore();
const router = useRouter();
const route = useRoute();
const activeIndex = ref(route.path);
const tasks = ref([]);
const chartDom = ref(null);
let myChart = null;

const hasClockedInToday = computed(() => {
    if (!authStore.user?.last_study_date) return false;
    const lastDate = new Date(authStore.user.last_study_date);
    const today = new Date();
    return lastDate.getDate() === today.getDate() && 
           lastDate.getMonth() === today.getMonth() && 
           lastDate.getFullYear() === today.getFullYear();
});

const clockIn = async () => {
    try {
        const response = await axios.post('/users/clockin');
        authStore.user = response.data; // Update local user state
        ElMessage.success('打卡成功！坚持就是胜利！');
    } catch (error) {
        ElMessage.error('打卡失败，请重试');
    }
};

const sortedTasks = computed(() => {
    return [...tasks.value].sort((a, b) => {
        const aComplete = a.completed_episodes >= a.total_episodes;
        const bComplete = b.completed_episodes >= b.total_episodes;
        
        if (aComplete === bComplete) {
            return a.id - b.id; // Or by creation date if available
        }
        return aComplete ? 1 : -1;
    });
});

const logout = () => {
  authStore.logout();
  router.push('/login');
};

const fetchTasks = async () => {
  try {
    const response = await axios.get('/tasks/');
    tasks.value = response.data;
    initChart();
  } catch (error) {
    console.error('Failed to fetch tasks', error);
  }
};

const handleProgressChange = async (task, newValue) => {
    // If undefined or null (e.g. empty input), ignore or reset
    if (newValue === undefined || newValue === null) return;
    
    // Safety check just in case, though el-input-number handles min/max
    if (newValue < 0) newValue = 0;
    if (newValue > task.total_episodes) newValue = task.total_episodes;

    // Optimistic update for chart
    // Note: v-model already updated the task.completed_episodes ref locally
    initChart(); // Refresh chart with new value

    try {
        await axios.put(`/tasks/${task.id}`, { completed_episodes: newValue });
    } catch (error) {
        ElMessage.error({ message: '更新失败', duration: 500 });
        fetchTasks(); // Revert on error
    }
};

const openUrl = (url) => {
    if (!url) return;
    if (!url.startsWith('http')) {
        url = 'https://' + url;
    }
    window.open(url, '_blank');
};

const initChart = () => {
  if (!chartDom.value) return;
  
  if (!myChart) {
    myChart = echarts.init(chartDom.value);
  }

  const data = [];
  const totalCompleted = tasks.value.reduce((sum, t) => sum + t.completed_episodes, 0);
  const totalEpisodes = tasks.value.reduce((sum, t) => sum + t.total_episodes, 0);
  const remaining = totalEpisodes - totalCompleted;

  // Add slices for each task's contribution to COMPLETION
  tasks.value.forEach(t => {
      // Always add to data for legend, but value is 0 if nothing completed?
      // Actually legend usually takes from series name or data name.
      // If we want legend for ALL tasks, we need data entries for them.
      // But pie chart only shows segments with value > 0.
      
      if (t.completed_episodes > 0) {
          const isFinished = t.completed_episodes >= t.total_episodes;
          data.push({
              value: t.completed_episodes,
              name: t.title,
              itemStyle: { color: t.color || '#409EFF' },
              label: {
                  show: isFinished,
                  position: 'inside',
                  formatter: '✓',
                  fontSize: 16,
                  fontWeight: 'bold',
                  color: '#fff'
              }
          });
      }
  });

  // Add Remaining slice
  if (remaining > 0 || data.length === 0) {
      data.push({
          value: remaining,
          name: '未完成',
          itemStyle: { color: '#E4E7ED' },
          label: { show: false },  // Hide label for gray part
          tooltip: { show: false }
      });
  }

  const option = {
    title: {
      text: '整体学习进度',
      subtext: `${totalCompleted} / ${totalEpisodes} 集`,
      left: 'center',
      top: '38%', // Align with center of pie chart (42%) - roughly center visually
      itemGap: 10,
      textStyle: {
          fontSize: 20,
          fontWeight: 'bold',
          color: '#303133'
      },
      subtextStyle: {
          fontSize: 16,
          color: '#909399'
      }
    },
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)' // Show percentage relative to total
    },
    legend: {
        bottom: 10,  // Reduced distance
        left: 'center',
        type: 'scroll',
        data: tasks.value.map(t => t.title) // Show all tasks in legend
    },
    series: [
      {
        name: '学习分布',
        type: 'pie',
        radius: ['50%', '75%'], // Donut - adjusted for legend space
        center: ['50%', '42%'], // Move chart up slightly to balance with legend
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 8,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: false
        },
        emphasis: {
            scale: true,
            scaleSize: 10
        },
        data: data
      }
    ]
  };

  myChart.setOption(option);
};

const handleResize = () => {
    myChart && myChart.resize();
};

onMounted(() => {
  fetchTasks();
  authStore.fetchUser(); // Ensure fresh stats
  window.addEventListener('resize', handleResize);
});

onUnmounted(() => {
    window.removeEventListener('resize', handleResize);
    if (myChart) myChart.dispose();
});
</script>

<style scoped>
.dashboard-container {
  min-height: 100vh;
  background-color: #f5f7fa;
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', Arial, sans-serif;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #fff;
  padding: 0 30px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  z-index: 10;
}

.header-branding {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 250px;
}

.logo { height: 32px; width: 32px; }

.title-container {
  display: flex;
  align-items: baseline;
  gap: 10px;
}

.app-name {
  color: #303133;
  font-size: 22px;
  font-weight: 800;
  margin: 0;
}

.divider { color: #dcdfe6; font-size: 20px; }
.page-title { color: #909399; font-size: 16px; font-weight: 500;}

.header-center { flex: 1; display: flex; justify-content: center; }
.nav-menu { border-bottom: none !important; background-color: transparent !important; }

.header-right {
  display: flex;
  align-items: center;
  gap: 15px;
  min-width: 200px;
  justify-content: flex-end;
}
.username { color: #606266; font-size: 14px; font-weight: 500; }

/* Main Content Layout */
.main-content {
    padding: 20px 40px;
    max-width: 1400px; /* Increased max width */
    margin: 0 auto;
    height: calc(100vh - 80px); /* Fill remaining height */
    overflow: hidden; /* Hide scroll on main itself, scroll inside layout if needed */
}

.dashboard-layout {
    display: flex;
    gap: 30px;
    height: 100%;
}

/* Side Panel */
.side-panel {
    display: flex;
    flex-direction: column;
    gap: 20px;
    width: 380px;
    min-width: 380px;
    height: 100%;
    position: sticky;
    top: 0;
}

.stats-card, .chart-card {
    background: #fff;
    border-radius: 24px;
    padding: 20px;
    box-shadow: 0 8px 20px rgba(0,0,0,0.03);
}

.stats-card {
    flex-shrink: 0;
}

.chart-card {
    flex: 1; /* Fill remaining height */
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 300px;
}

.stats-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    padding-bottom: 15px;
    border-bottom: 1px solid #f0f2f5;
}

.stats-title-row {
    display: flex;
    align-items: center;
    gap: 8px;
    color: #303133;
}

.stats-title-row h3 {
    margin: 0;
    font-size: 18px;
    font-weight: 700;
}

.stats-icon {
    font-size: 20px;
    color: #409EFF;
}

.clock-btn {
    font-weight: 600;
    transition: all 0.3s ease;
}

.stats-grid {
    display: flex;
    justify-content: space-around;
    align-items: center;
}

.stat-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 5px;
}

.stat-value {
    font-size: 28px;
    font-weight: 800;
    color: #303133;
    line-height: 1;
}

.stat-label {
    font-size: 13px;
    color: #909399;
    font-weight: 500;
}

.stat-divider {
    width: 1px;
    height: 40px;
    background-color: #f0f2f5;
}

.chart-container {
    width: 100%;
    height: 100%;
}

/* Task Grid */
.task-grid {
    flex: 1; /* Take remaining space */
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: 25px;
    align-content: start; /* Don't stretch rows */
    overflow-y: auto; /* Scrollable tasks */
    padding-right: 5px; /* Space for scrollbar */
    padding-bottom: 20px;
}

/* Task Card Style */
.task-card {
    border-radius: 24px;
    padding: 25px;
    color: white;
    transition: transform 0.2s, box-shadow 0.2s;
    position: relative;
    overflow: hidden;
}

.title-row {
    display: flex;
    align-items: center;
    gap: 10px;
}

.completed-icon {
    font-size: 20px;
    color: white;
    font-weight: bold;
    background: rgba(255,255,255,0.2);
    border-radius: 50%;
    padding: 2px;
}

.task-card:hover {
    transform: translateY(-5px);
}

.card-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    height: 100%;
}

.card-left {
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
}

.task-title {
    margin: 0 0 10px 0;
    font-size: 22px;
    font-weight: 700;
    line-height: 1.2;
    text-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.progress-info {
    font-size: 14px;
    opacity: 0.9;
    margin-bottom: 12px;
    font-weight: 500;
}

.progress-track {
    background: rgba(255, 255, 255, 0.3);
    height: 8px;
    border-radius: 4px;
    overflow: hidden;
    width: 90%;
}

.progress-fill {
    background: #fff;
    height: 100%;
    border-radius: 4px;
    transition: width 0.3s ease;
}

.card-right {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 15px;
    margin-left: 15px;
}

.control-group {
    display: flex;
    gap: 8px;
}

.control-btn {
    background: rgba(255,255,255,0.2) !important;
    border: none !important;
    color: white !important;
}

.control-btn:hover:not(:disabled) {
    background: rgba(255,255,255,0.4) !important;
}

.control-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.popover-content {
    text-align: center;
}

.popover-title {
    margin: 0 0 10px 0;
    font-size: 14px;
    font-weight: bold;
    color: #606266;
}

.link-btn {
    background: white !important;
    color: #333 !important;
    border: none !important;
    box-shadow: 0 4px 8px rgba(0,0,0,0.15) !important;
    font-size: 18px !important;
}

.link-btn:hover {
    transform: scale(1.05);
}

.empty-state {
    grid-column: 1 / -1;
    text-align: center;
    padding: 40px;
    color: #909399;
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
    order: 3; /* Move menu to bottom or keep in middle */
    margin-top: 5px;
  }

  .header-right {
    min-width: auto;
    width: 100%;
    justify-content: center;
    margin-bottom: 5px;
  }

  .main-content {
    padding: 15px;
    height: auto;
    overflow: visible;
  }

  .dashboard-layout {
    flex-direction: column-reverse; /* Side Panel (Stats+Chart) on top, Tasks below */
    gap: 20px;
    height: auto;
  }

  .side-panel {
    display: flex;
    flex-direction: column;
    width: 100%;
    min-width: unset;
    height: auto;
    position: relative;
    top: 0;
  }

  .chart-card {
    display: block; /* Ensure block display */
    width: 100%;
    height: 300%; 
    min-height: 300px;
    flex: none; /* Do not flex */
  }

  .chart-container {
      width: 100%;
      height: 300px; /* Explicit height */
  }
  
  .stats-card {
      width: 100%;
  }

  .task-grid {
    grid-template-columns: 1fr; /* Single column for tasks */
    overflow-y: visible; /* Let page scroll */
    padding-right: 0;
    max-height: none; /* Remove scroll limit */
  }

  .nav-menu {
      width: 100%;
      display: flex;
      justify-content: center;
  }
}
</style>
