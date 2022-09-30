<template>
  <div class="error">
    <img src="@/assets/404.png" class="error-image" />
    <h2 style="margin-top: 20px">抱歉，您访问的页面出错了</h2>
    <p style="margin-top: 20px">您可能输错了网址，或该网页已删除或不存在</p>
    <el-button type="primary" @click="handleBackHome" style="margin-top: 20px">
      返回主页
    </el-button>
  </div>
</template>

<script>
import { useRouter } from "vue-router";
export default {
  setup() {
    const router = useRouter();
    const handleBackHome = () => {
      router.push("/");
    };
    return { handleBackHome };
  },
};
</script>

<style lang="less">
</style>