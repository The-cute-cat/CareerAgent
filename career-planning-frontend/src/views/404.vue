<template>
  <div class="not-found">
    <div class="content">
      <div class="error-code">
        <span class="digit">4</span>
        <span class="digit zero">0</span>
        <span class="digit">4</span>
      </div>
      <h2 class="title">页面走丢了</h2>
      <p class="description">抱歉，您访问的页面不存在或已被移除</p>
      <div class="actions">
        <router-link to="/" class="btn-home">
          <span class="icon"></span>
          返回首页
        </router-link>
      </div>
    </div>
    <div class="background-decoration">
      <div class="circle circle-1"></div>
      <div class="circle circle-2"></div>
      <div class="circle circle-3"></div>
    </div>
  </div>
</template>

<style scoped>
.not-found {
  min-height: 100vh;
  height: 100vh;
  width: 100vw;
  min-width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1a1f36 0%, #2d3752 50%, #1a1f36 100%);
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  overflow: hidden;
  z-index: 9999;
}

.content {
  text-align: center;
  z-index: 2;
  padding: 40px;
}

.error-code {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
}

.digit {
  font-size: 120px;
  font-weight: 700;
  color: #ffffff;
  text-shadow: 0 0 40px rgba(255, 255, 255, 0.3);
  animation: float 3s ease-in-out infinite;
}

.digit:nth-child(2) {
  animation-delay: 0.5s;
}

.digit:nth-child(3) {
  animation-delay: 1s;
}

.zero {
  color: #409eff;
  text-shadow: 0 0 40px rgba(64, 158, 255, 0.5);
}

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

.title {
  font-size: 32px;
  font-weight: 500;
  color: #ffffff;
  margin: 0 0 16px 0;
}

.description {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.6);
  margin: 0 0 40px 0;
}

.actions {
  display: flex;
  justify-content: center;
  gap: 16px;
}

.btn-home {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 14px 32px;
  background: #409eff;
  color: #ffffff;
  text-decoration: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 500;
  transition: all 0.3s ease;
  box-shadow: 0 4px 14px rgba(64, 158, 255, 0.4);
}

.btn-home:hover {
  background: #66b1ff;
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(64, 158, 255, 0.5);
}

.icon {
  font-size: 18px;
  transition: transform 0.3s ease;
}

.btn-home:hover .icon {
  transform: translateX(-4px);
}

/* 背景装饰 */
.background-decoration {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
  pointer-events: none;
}

.circle {
  position: absolute;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(64, 158, 255, 0.1) 0%, transparent 70%);
}

.circle-1 {
  width: 600px;
  height: 600px;
  top: -200px;
  right: -100px;
}

.circle-2 {
  width: 400px;
  height: 400px;
  bottom: -100px;
  left: -100px;
}

.circle-3 {
  width: 300px;
  height: 300px;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: radial-gradient(circle, rgba(64, 158, 255, 0.05) 0%, transparent 70%);
}

/* 响应式 */
@media (max-width: 768px) {
  .digit {
    font-size: 80px;
  }
  
  .title {
    font-size: 24px;
  }
  
  .description {
    font-size: 14px;
  }
  
  .btn-home {
    padding: 12px 24px;
    font-size: 14px;
  }
}
</style>
