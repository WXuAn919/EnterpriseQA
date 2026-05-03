<script setup>
import { nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import * as echarts from 'echarts'

import { getDashboardApi } from '@/api/admin'
import StatCard from '@/components/dashboard/StatCard.vue'

const summary = ref({
  userCount: 0,
  knowledgeBaseCount: 0,
  documentCount: 0,
  todayQaCount: 0,
})
const trendRef = ref(null)
const distributionRef = ref(null)
let trendChart = null
let distributionChart = null

/** 初始化后台图表并渲染统计数据。 */
async function loadDashboard() {
  const response = await getDashboardApi()
  const dashboard = response.data
  summary.value = dashboard.summary

  await nextTick()
  if (!trendChart) {
    trendChart = echarts.init(trendRef.value)
  }
  if (!distributionChart) {
    distributionChart = echarts.init(distributionRef.value)
  }

  trendChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: 36, right: 20, top: 30, bottom: 26 },
    xAxis: {
      type: 'category',
      data: dashboard.qaTrend.map((item) => item.date),
      boundaryGap: false,
    },
    yAxis: { type: 'value' },
    series: [
      {
        name: '问答次数',
        type: 'line',
        smooth: true,
        data: dashboard.qaTrend.map((item) => item.count),
        areaStyle: {
          color: 'rgba(59,130,246,0.16)',
        },
        lineStyle: {
          color: '#2563eb',
          width: 3,
        },
      },
    ],
  })

  distributionChart.setOption({
    tooltip: { trigger: 'item' },
    series: [
      {
        type: 'pie',
        radius: ['44%', '72%'],
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 3,
        },
        data: dashboard.documentDistribution.map((item) => ({
          name: item.name,
          value: item.count,
        })),
      },
    ],
  })
}

onMounted(loadDashboard)

onBeforeUnmount(() => {
  trendChart?.dispose()
  distributionChart?.dispose()
})
</script>

<template>
  <section class="page-section">
    <div class="page-header">
      <div>
        <p class="page-header__eyebrow">管理后台</p>
        <h2>首页概览</h2>
      </div>
      <el-button type="primary" plain @click="loadDashboard">刷新统计</el-button>
    </div>

    <div class="stat-grid">
      <StatCard title="系统用户数" :value="summary.userCount" hint="包含管理员与普通用户" />
      <StatCard title="知识库数量" :value="summary.knowledgeBaseCount" hint="当前可问答的知识库总数" />
      <StatCard title="文档总数" :value="summary.documentCount" hint="已登记的知识文档数量" />
      <StatCard title="今日问答数" :value="summary.todayQaCount" hint="用于观察今日活跃度" />
    </div>

    <div class="chart-grid">
      <div class="chart-card">
        <div class="chart-card__header">
          <h3>近 7 天问答趋势</h3>
          <p>观察系统近期问答活跃情况</p>
        </div>
        <div ref="trendRef" class="chart-box"></div>
      </div>

      <div class="chart-card">
        <div class="chart-card__header">
          <h3>知识库文档分布</h3>
          <p>查看不同知识库中的文档数量</p>
        </div>
        <div ref="distributionRef" class="chart-box"></div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.page-section {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.page-header__eyebrow {
  margin: 0 0 8px;
  color: #3b82f6;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 1.2px;
}

.page-header h2,
.chart-card__header h3 {
  margin: 0;
  color: #12304c;
}

.stat-grid,
.chart-grid {
  display: grid;
  gap: 18px;
}

.stat-grid {
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.chart-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.chart-card {
  padding: 22px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.92);
  box-shadow: 0 18px 48px rgba(41, 79, 122, 0.08);
}

.chart-card__header p {
  margin: 8px 0 0;
  color: #71829a;
}

.chart-box {
  height: 320px;
  margin-top: 14px;
}

@media (max-width: 1100px) {
  .stat-grid,
  .chart-grid {
    grid-template-columns: 1fr;
  }
}
</style>
