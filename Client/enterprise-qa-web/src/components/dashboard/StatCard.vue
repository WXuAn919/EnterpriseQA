<script setup>
/** 统计卡片组件，用于后台首页展示关键指标。 */
defineProps({
  title: {
    type: String,
    default: '',
  },
  value: {
    type: [String, Number],
    default: 0,
  },
  hint: {
    type: String,
    default: '',
  },
})
</script>

<template>
  <div class="stat-card">
    <p class="stat-card__title">{{ title }}</p>
    <h3 class="stat-card__value">{{ value }}</h3>
    <p class="stat-card__hint">{{ hint }}</p>
  </div>
</template>

<style scoped>
.stat-card {
  padding: 22px;
  border-radius: 18px;
  background: linear-gradient(145deg, #ffffff, #f4f8ff);
  box-shadow: 0 16px 40px rgba(33, 72, 118, 0.08);
  border: 1px solid rgba(127, 157, 202, 0.14);
}

.stat-card__title {
  margin: 0;
  color: #6a7892;
  font-size: 14px;
}

.stat-card__value {
  margin: 12px 0 8px;
  color: #12304c;
  font-size: 34px;
  font-weight: 700;
}

.stat-card__hint {
  margin: 0;
  color: #7f8ca3;
  font-size: 13px;
}
</style>
