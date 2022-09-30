<template>
  <div>
    <el-carousel height="450px">
      <el-carousel-item v-for="item in url" :key="item">
        <el-image :src="require('../assets/' + item)"></el-image>
      </el-carousel-item>
    </el-carousel>
  </div>
</template>

<script>
export default {
  props: {
    url: Array,
  },
};
</script>

<style lang="less">
.el-carousel__item h3 {
  color: #475669;
  font-size: 14px;
  opacity: 0.75;
  line-height: 300px;
  margin: 0;
  padding: 0;
}

.el-carousel__item {
  height: 450px;
}
</style>