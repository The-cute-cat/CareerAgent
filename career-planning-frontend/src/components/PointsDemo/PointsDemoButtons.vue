<script setup lang="ts">
import { computed } from 'vue'
import { 
  Document, 
  Reading, 
  ChatDotRound, 
  User,
  Medal,
  List,
  MagicStick
} from '@element-plus/icons-vue'
import { usePoints } from '@/composables/usePoints'

const { 
  currentPoints, 
  memberType,
  discountRate,
  rechargePoints,
  upgradeMember
} = usePoints()

const isMember = computed(() => memberType.value !== 'normal')
const discountPercent = computed(() => Math.round((1 - discountRate.value) * 100))

// 演示：直接充值积分
const handleRechargeDemo = async () => {
  await rechargePoints(1000, '测试充值')
}

// 演示：开通会员
const handleUpgradeMemberDemo = async (type: 'monthly' | 'quarterly' | 'yearly') => {
  await upgradeMember(type)
}

// 会员套餐配置
const memberPlans = [
  { key: 'monthly', label: '月度会员', color: '#3b82f6', price: '¥29.9' },
  { key: 'quarterly', label: '季度会员', color: '#8b5cf6', price: '¥79.9' },
  { key: 'yearly', label: '年度会员', color: '#f59e0b', price: '¥299.9' }
] as const
</script>

<template>
  <div class="points-demo-panel">
    <div class="demo-header">
      <div class="header-title">
        <el-icon><MagicStick /></el-icon>
        <span>积分系统演示</span>
      </div>
      <div class="header-stats">
        <div class="stat-item">
          <span class="label">当前积分</span>
          <span class="value points">{{ currentPoints }}</span>
        </div>
        <div class="stat-item" v-if="isMember">
          <span class="label">会员折扣</span>
          <span class="value discount">{{ discountPercent }}折</span>
        </div>
      </div>
    </div>
    
    <div class="demo-content">
      <p class="demo-desc">系统已集成功能点积分扣除，以下操作将自动扣减积分：</p>
      
      <div class="feature-list">
        <div class="feature-item">
          <el-icon color="#3b82f6"><ChatDotRound /></el-icon>
          <span>AI问答（10积分/次）</span>
        </div>
        <div class="feature-item">
          <el-icon color="#10b981"><List /></el-icon>
          <span>岗位推荐分析（20积分/次）</span>
        </div>
        <div class="feature-item">
          <el-icon color="#8b5cf6"><Medal /></el-icon>
          <span>AI职业测评（30积分/次）</span>
        </div>
        <div class="feature-item">
          <el-icon color="#f59e0b"><Document /></el-icon>
          <span>简历优化（50积分/次）</span>
        </div>
        <div class="feature-item">
          <el-icon color="#ef4444"><User /></el-icon>
          <span>模拟面试（80积分/次）</span>
        </div>
        <div class="feature-item">
          <el-icon color="#ec4899"><Reading /></el-icon>
          <span>生涯规划报告（100积分/次）</span>
        </div>
      </div>
      
      <div class="member-upgrade-section">
        <p class="section-title">测试开通会员：</p>
        <div class="member-buttons">
          <button
            v-for="plan in memberPlans"
            :key="plan.key"
            class="member-btn"
            :style="{ '--btn-color': plan.color }"
            @click="handleUpgradeMemberDemo(plan.key)"
          >
            <el-icon><Medal /></el-icon>
            <span class="btn-label">{{ plan.label }}</span>
            <span class="btn-price">{{ plan.price }}</span>
          </button>
        </div>
      </div>
      
      <div class="recharge-section">
        <p class="recharge-desc">测试充值功能：</p>
        <button class="recharge-btn" @click="handleRechargeDemo">
          <el-icon><MagicStick /></el-icon>
          充值 1000 积分（测试）
        </button>
      </div>
    </div>
    
    <div class="points-rules">
      <h4>积分消耗规则</h4>
      <ul>
        <li>AI职业测评：30积分/次</li>
        <li>岗位推荐分析：20积分/次</li>
        <li>简历优化：50积分/次</li>
        <li>简历一键生成：60积分/次</li>
        <li>模拟面试：80积分/次</li>
        <li>生涯规划报告：100积分/次</li>
        <li>AI问答：10积分/次</li>
      </ul>
      <p class="member-hint" v-if="isMember">
        您当前是会员，享受 {{ discountPercent }}% 折扣优惠
      </p>
    </div>
  </div>
</template>

<style scoped lang="scss">
.points-demo-panel {
  background: linear-gradient(135deg, #fff 0%, #f8fafc 100%);
  border-radius: 20px;
  padding: 24px;
  border: 1px solid #e2e8f0;
}

.demo-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e2e8f0;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
  font-weight: 700;
  color: #1e293b;
  
  .el-icon {
    font-size: 24px;
    color: #3b82f6;
  }
}

.header-stats {
  display: flex;
  gap: 20px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
  
  .label {
    font-size: 12px;
    color: #94a3b8;
  }
  
  .value {
    font-size: 20px;
    font-weight: 800;
    
    &.points {
      color: #3b82f6;
    }
    
    &.discount {
      color: #f59e0b;
    }
  }
}

.demo-content {
  margin-bottom: 24px;
}

.demo-desc {
  font-size: 14px;
  color: #64748b;
  margin: 0 0 16px;
}

.function-buttons {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 12px;
  margin-bottom: 20px;
}

.func-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 16px 12px;
  border-radius: 12px;
  border: 2px solid #e2e8f0;
  background: #fff;
  cursor: pointer;
  transition: all 0.3s ease;
  
  .el-icon {
    font-size: 24px;
    color: var(--btn-color, #3b82f6);
  }
  
  .btn-label {
    font-size: 13px;
    font-weight: 600;
    color: #1e293b;
  }
  
  .btn-points {
    font-size: 11px;
    color: #94a3b8;
    padding: 2px 8px;
    background: #f1f5f9;
    border-radius: 10px;
  }
  
  &:hover {
    border-color: var(--btn-color, #3b82f6);
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  }
}

.feature-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 20px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: #f8fafc;
  border-radius: 10px;
  font-size: 14px;
  color: #475569;
}

.feature-item .el-icon {
  font-size: 18px;
}

.member-upgrade-section {
  padding-top: 16px;
  border-top: 1px dashed #e2e8f0;
  margin-bottom: 20px;
}

.member-upgrade-section .section-title {
  font-size: 13px;
  color: #94a3b8;
  margin: 0 0 12px;
}

.member-buttons {
  display: flex;
  gap: 10px;
}

.member-btn {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 14px 10px;
  border-radius: 12px;
  border: 2px solid #e2e8f0;
  background: #fff;
  cursor: pointer;
  transition: all 0.3s ease;
}

.member-btn .el-icon {
  font-size: 22px;
  color: var(--btn-color, #3b82f6);
}

.member-btn .btn-label {
  font-size: 13px;
  font-weight: 600;
  color: #1e293b;
}

.member-btn .btn-price {
  font-size: 12px;
  color: #94a3b8;
  font-weight: 500;
}

.member-btn:hover {
  border-color: var(--btn-color, #3b82f6);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.recharge-section {
  padding-top: 16px;
  border-top: 1px dashed #e2e8f0;
}

.recharge-desc {
  font-size: 13px;
  color: #94a3b8;
  margin: 0 0 12px;
}

.recharge-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  padding: 12px 20px;
  border-radius: 10px;
  border: none;
  background: linear-gradient(135deg, #10b981, #059669);
  color: #fff;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
  
  .el-icon {
    font-size: 18px;
  }
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
  }
}

.points-rules {
  padding: 16px;
  background: #f8fafc;
  border-radius: 12px;
  
  h4 {
    font-size: 14px;
    font-weight: 700;
    color: #1e293b;
    margin: 0 0 12px;
  }
  
  ul {
    margin: 0;
    padding-left: 18px;
    font-size: 13px;
    color: #64748b;
    line-height: 1.8;
  }
  
  .member-hint {
    margin: 12px 0 0;
    padding: 10px 14px;
    background: linear-gradient(135deg, #fef3c7, #fde68a);
    border-radius: 8px;
    font-size: 13px;
    color: #b45309;
    font-weight: 600;
  }
}
</style>
