<template>
  <div id="app">
    <!-- <el-container>
      <el-header><my-header /></el-header>
      <el-main><router-view /> </el-main>
      <el-footer><my-footer /></el-footer>
    </el-container> -->
    <router-view />
  </div>
</template>

<script>
export default {
  name: "App",
};
</script>

<style lang="less">
* {
  margin: 0;
  padding: 0;
}

#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  .el-header {
    padding: 0;
  }

  .el-main {
    padding: 0;
    margin: 0;
    overflow-x: hidden;
  }

  .el-footer {
    padding: 0;
    background-color: rgb(84, 92, 100);
    height: auto !important;
  }
  .body {
    background-color: rgb(247, 247, 247);
  }
}
</style>
