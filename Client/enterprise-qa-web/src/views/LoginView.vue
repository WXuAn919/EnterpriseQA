<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const loading = ref(false)

const loginForm = reactive({
  username: 'admin',
  password: '123456',
})

/** 提交登录表单并按角色跳转。 */
async function handleLogin() {
  loading.value = true
  try {
    const loginResult = await authStore.login(loginForm)
    ElMessage.success('登录成功')
    if (loginResult.role === 'admin') {
      router.replace('/admin/home')
    } else {
      router.replace('/chat')
    }
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-page">
    <section class="login-hero">
      <div class="login-hero__content">
        <p class="login-hero__eyebrow">Enterprise QA Agent</p>
        <h1>企业内部知识库问答系统</h1>
        <p class="login-hero__desc">
          基于 Flask、Vue3、LangChain、Ollama 与 Chroma 构建的教学型 RAG 问答平台。
        </p>
        <div class="login-hero__tips">
          <span>管理员账号：admin / 123456</span>
          <span>普通用户账号：zhangsan / 123456</span>
        </div>
      </div>
    </section>

    <section class="login-panel">
      <div class="login-card">
        <h2>欢迎登录</h2>
        <p class="login-card__sub">进入后台管理或知识问答工作台</p>
        <el-form label-position="top">
          <el-form-item label="用户名">
            <el-input v-model="loginForm.username" placeholder="请输入用户名" />
          </el-form-item>
          <el-form-item label="密码">
            <el-input
              v-model="loginForm.password"
              placeholder="请输入密码"
              show-password
              type="password"
              @keyup.enter="handleLogin"
            />
          </el-form-item>
          <el-button class="login-button" type="primary" :loading="loading" @click="handleLogin">
            立即登录
          </el-button>
        </el-form>
      </div>
    </section>
  </div>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  display: grid;
  grid-template-columns: 1.15fr 0.85fr;
  background:
    radial-gradient(circle at 12% 18%, rgba(76, 132, 255, 0.2), transparent 24%),
    radial-gradient(circle at 80% 30%, rgba(45, 212, 191, 0.22), transparent 20%),
    linear-gradient(135deg, #eff6ff 0%, #f8fbff 46%, #eef3fa 100%);
}

.login-hero,
.login-panel {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 48px;
}

.login-hero__content {
  max-width: 560px;
}

.login-hero__eyebrow {
  margin: 0 0 12px;
  color: #2563eb;
  font-size: 13px;
  letter-spacing: 1.4px;
  text-transform: uppercase;
}

.login-hero h1 {
  margin: 0;
  font-size: 48px;
  line-height: 1.15;
  color: #0f2742;
}

.login-hero__desc {
  margin: 20px 0 0;
  color: #53657d;
  font-size: 18px;
  line-height: 1.8;
}

.login-hero__tips {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 26px;
}

.login-hero__tips span {
  padding: 10px 16px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.72);
  color: #35506c;
  box-shadow: 0 10px 30px rgba(56, 97, 163, 0.1);
}

.login-card {
  width: min(440px, 100%);
  padding: 34px;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.88);
  box-shadow: 0 18px 50px rgba(28, 64, 112, 0.12);
  backdrop-filter: blur(10px);
}

.login-card h2 {
  margin: 0;
  color: #102a43;
}

.login-card__sub {
  margin: 10px 0 22px;
  color: #688099;
}

.login-button {
  width: 100%;
  height: 44px;
  margin-top: 10px;
}

@media (max-width: 960px) {
  .login-page {
    grid-template-columns: 1fr;
  }

  .login-hero {
    padding-bottom: 12px;
  }

  .login-panel {
    padding-top: 12px;
  }

  .login-hero h1 {
    font-size: 34px;
  }
}
</style>
