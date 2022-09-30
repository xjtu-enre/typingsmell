<template>
  <layout>
    <div class="utils-box">
      <div class="inner-box">
        <el-tabs v-model="index" style="width: 90%"
          ><el-tab-pane label="UploadProject" name="uploadProject">
            <upload-proj />
          </el-tab-pane>
          <el-tab-pane label="ImageToBase64" name="imageToBase64">
            <trans-img />
          </el-tab-pane>
        </el-tabs>
      </div>
    </div>
  </layout>
</template>

<script>
import { ref } from "vue";
import Layout from "@/components/Layout";
import TransImg from "./components/TransImg";
import UploadProj from "./components/UploadProj.vue";
export default {
  components: {
    Layout,
    "trans-img": TransImg,
    "upload-proj": UploadProj,
  },

  setup() {
    const index = ref("uploadProject");

    return { index };
  },
};
</script>
<style lang="less" scoped>
.utils-box {
  box-sizing: border-box;
  height: 100%;
  width: 100%;
  padding: 20px 40px;
}

.inner-box {
  width: 100%;
}
</style>