<template>
  <div class="rec-card">
    <el-card class="rec-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>{{ recMetric }}</span>
          <el-switch v-model="showAsTree" active-text="showAsTree" />
        </div>
      </template>
      <div class="file-list">
        <el-scrollbar>
          <div
            v-show="!showAsTree"
            v-for="(item, index) in recFiles"
            :key="index"
            style="margin-top: 5px"
          >
            {{ item }}
          </div>
          <div>
            <path-tree
              v-show="showAsTree"
              v-for="item in pathTree"
              :key="item"
              :pathTree="item"
            ></path-tree>
          </div>
        </el-scrollbar>
      </div>
    </el-card>
  </div>
</template>
<script>
import { onMounted, ref, getCurrentInstance } from "vue";
import { treefy } from "../../../utils/treefy";
import PathTree from "./PathTree";
export default {
  props: {
    fileList: Object,
  },
  components: {
    "path-tree": PathTree,
  },
  watch: {
    fileList(val) {
      for (var key in val) {
        var value = val[key];
        this.recMetric = key;
        this.recFiles = value;
        this.pathTree = treefy(value);
      }
    },
  },

  setup() {
    const { proxy } = getCurrentInstance();
    const recMetric = ref("");
    const recFiles = ref([]);
    const pathTree = ref([]);
    const showAsTree = ref(false);

    onMounted(() => {
      for (var key in proxy.fileList) {
        var value = proxy.fileList[key];
        proxy.recMetric = key;
        proxy.recFiles = value;
        proxy.pathTree = treefy(value);
      }
    });

    return { recMetric, recFiles, pathTree, showAsTree };
  },
};
</script>
<style scoped>
.rec-card {
  height: 300px;
  width: 100%;
  text-align: start;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.file-list {
  height: 200px;
}
</style>