<template>
  <div class="backround">
    <h1>404</h1>
    <div class="container">
      <div class="row justify-content-center">
        <div class="col-md-6 text-center">
          <p class="lead">抱歉，您访问的页面不存在。</p>
          <router-link to="/login" class="btn btn-primary">返回首页</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script></script>

<style lang="scss">
@import '/public/css/style.css';

h1{
  font-size: 5rem;
  text-align: center;
  margin-top: 20vh;
  color: #000;
}
.backround{
  background: rgb(244, 244, 244);
  height: 100vh;
}

</style>
