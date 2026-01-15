<template>
  <div class="login-container">
    <div class="brand-section">
       <img src="/vite.svg" alt="Hanwen Study Logo" class="brand-logo" />
       <h1 class="brand-title">Hanwen Study</h1>
    </div>
    <el-card class="login-card" shadow="always">
      <template #header>
        <div class="card-header">
          <h2>{{ isRegister ? '注册账号' : '欢迎登录' }}</h2>
        </div>
      </template>

      <el-tabs v-model="activeTab" class="login-tabs" @tab-click="handleTabClick">
        <el-tab-pane label="登录" name="login"></el-tab-pane>
        <el-tab-pane label="注册" name="register"></el-tab-pane>
      </el-tabs>

      <el-form 
        ref="formRef"
        :model="form" 
        :rules="rules" 
        label-width="0px" 
        class="login-form"
      >
        <el-form-item prop="username">
          <el-input 
            v-model="form.username" 
            placeholder="用户名 (最少3个字符)" 
            prefix-icon="User"
          />
        </el-form-item>
        <el-form-item prop="password">
          <el-input 
            v-model="form.password" 
            type="password" 
            placeholder="密码 (最少6个字符)" 
            prefix-icon="Lock"
            show-password
          />
        </el-form-item>
        <el-form-item v-if="isRegister" prop="confirmPassword">
          <el-input 
            v-model="form.confirmPassword" 
            type="password" 
            placeholder="确认密码" 
            prefix-icon="Lock"
            show-password
          />
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" class="submit-btn" :loading="loading" @click="onSubmit">
            {{ isRegister ? '立即注册' : '登录' }}
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue';
import { useAuthStore } from '../stores/auth';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { User, Lock } from '@element-plus/icons-vue';

const authStore = useAuthStore();
const router = useRouter();
const formRef = ref(null);
const loading = ref(false);
const activeTab = ref('login');

const isRegister = computed(() => activeTab.value === 'register');

const form = reactive({
  username: '',
  password: '',
  confirmPassword: '',
});

const validatePass2 = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请再次输入密码'));
  } else if (value !== form.password) {
    callback(new Error('两次输入密码不一致!'));
  } else {
    callback();
  }
};

const rules = reactive({
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, message: '用户名长度不能少于3个字符', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6个字符', trigger: 'blur' },
  ],
  confirmPassword: [
    { validator: validatePass2, trigger: 'blur' },
  ],
});

const handleTabClick = (tab) => {
  formRef.value?.resetFields();
  form.username = '';
  form.password = '';
  form.confirmPassword = '';
};

const onSubmit = async () => {
  if (!formRef.value) return;
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true;
      try {
        if (isRegister.value) {
          await authStore.register(form.username, form.password);
          ElMessage.success('注册成功，请登录');
          activeTab.value = 'login'; // 切换到登录 tab
          handleTabClick(); // 重置表单
        } else {
          await authStore.login(form.username, form.password);
          ElMessage.success('登录成功');
          // Check if admin
          if (authStore.user?.is_admin) {
             router.push('/admin');
          } else {
             router.push('/');
          }
        }
      } catch (error) {
        ElMessage.error(error.response?.data?.detail || '操作失败');
      } finally {
        loading.value = false;
      }
    } else {
      console.log('error submit!');
      return false;
    }
  });
};
</script>
<style scoped>
.login-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.brand-section {
  display: flex;
  align-items: center;
  margin-bottom: 30px;
  color: white;
  gap: 15px;
}

.brand-logo {
  width: 50px;
  height: 50px;
}

.brand-title {
  font-size: 36px;
  font-weight: bold;
  margin: 0;
  text-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

.login-card {
  width: 100%;
  max-width: 400px;
  border-radius: 12px;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
}

.card-header {
  text-align: center;
  margin-bottom: 0;
}

.card-header h2 {
  margin: 0;
  color: #333;
  font-weight: 600;
  font-size: 24px;
}

.login-tabs {
  margin-bottom: 20px;
}

/* Deep selector to center tabs */
:deep(.el-tabs__nav-scroll) {
  display: flex;
  justify-content: center;
}

.login-form {
  padding: 10px 0;
}

.submit-btn {
  width: 100%;
  padding: 12px;
  font-size: 16px;
  border-radius: 6px;
  margin-top: 10px;
}

:deep(.el-input__wrapper) {
  padding: 8px 11px;
}
</style>
