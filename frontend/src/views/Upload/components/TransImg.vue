<template>
  <div class="trans-body">
    <el-upload
      class="upload-demo"
      drag
      action="useless"
      :limit="1"
      :before-upload="handleBeforeUpload"
    >
      <i class="el-icon-upload"></i>
      <div class="el-upload__text">将文件拖到此处，或<em>点击上传</em></div>
    </el-upload>
    <div style="margin: 15px">转换结果<i class="el-icon-right"></i></div>
    <div class="trans-end">
      <div class="res">
        <el-scrollbar>
          <div class="res-body">{{ transRes }}</div>
        </el-scrollbar>
      </div>
      <div class="copy">
        <el-button
          size="mini"
          class="copy-btn"
          style="background-color: unset"
          :data-clipboard-text="transRes"
          @click="handleCopy"
          plain
        >
          复制
        </el-button>
      </div>
    </div>
  </div>
</template>
<script>
import { ref, getCurrentInstance } from "vue";
import Clipboard from "clipboard";
export default {
  setup() {
    const { proxy } = getCurrentInstance();
    const transRes = ref("暂无数据");

    const handleBeforeUpload = (file) => {
      handleTrans(file);
      return false;
    };

    const handleTrans = async (params) => {
      const file = params;
      const isJPG = file.type === "image/jpeg";
      const isPNG = file.type === "image/png";
      const isLt4M = file.size / 1024 / 1024 < 4;
      if (!isJPG && !isPNG) {
        proxy.$message.error("上传图片只能是 JPG 或 PNG 格式!");
        return;
      }

      if (!isLt4M) {
        proxy.$message.error("上传图片大小不能超过 4MB!");
        return;
      }
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => {
        transRes.value = reader.result;
      };
    };

    const handleCopy = () => {
      var clipboard = new Clipboard(".copy-btn");
      clipboard.on("success", () => {
        proxy.$message({
          message: "内容已经复制到剪切板",
          type: "success",
        });
        clipboard.destroy();
      });
      clipboard.on("error", () => {
        // 不支持复制
        proxy.$message({
          message: "复制失败",
          type: "error",
        });
        clipboard.destroy();
      });
    };
    return { transRes, handleBeforeUpload, handleTrans, handleCopy };
  },
};
</script>
<style lang="less" scoped>
.trans-body {
  height: 500px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.trans-end {
  height: 400px;
  width: 600px;
  border: 1px solid #ebeef5;
}

.res {
  height: 400px;
  width: 600px;
}

.res-body {
  word-wrap: break-word;
  word-break: break-all;
}

.copy {
  height: 50px;
  margin-top: 10px;
  position: absolute;
}

.res/deep/.el-scrollbar__bar {
  z-index: 999;
  &.is-vertical {
    width: 15px; //滚动条宽度
  }
}
.res/deep/.el-scrollbar__thumb {
  background: rgb(64, 158, 255);
}
</style>