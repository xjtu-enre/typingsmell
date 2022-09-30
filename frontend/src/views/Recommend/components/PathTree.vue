<template>
  <div class="tree">
    <div v-if="tree.type === `folder`">
      <div @click="folderShow = !folderShow">
        <el-image
          :src="require('../../../assets/folder.png')"
          style="width: 20px; margin-right: 7px"
        />
        <div class="text">
          {{ tree.label }}
        </div>
      </div>
    </div>

    <div v-if="tree.type === `file`">
      <el-image
        :src="require('../../../assets/file.png')"
        style="width: 20px; margin-right: 7px"
      />
      <div class="text">
        {{ tree.label }}
      </div>
    </div>
    <div
      v-for="(item, index) in tree.children"
      :key="index"
      style="margin-top: 5px"
    >
      <path-tree :pathTree="item" v-if="folderShow"></path-tree>
    </div>
  </div>
</template>
<script>
import { onMounted, ref, getCurrentInstance } from "vue";
export default {
  name: "PathTree",
  props: {
    pathTree: Object,
  },
  watch: {
    pathTree(val) {
      this.tree = val;
    },
  },

  setup() {
    const { proxy } = getCurrentInstance();
    const tree = ref([]);
    const folderShow = ref(false);
    onMounted(() => {
      proxy.tree = proxy.pathTree;
    });
    return { tree, folderShow };
  },
};
</script>
<style scoped>
.file-list {
  margin-left: 10px;
  margin-top: 5px;
}

.text {
  font-size: 17px;
  display: inline;
}

.text::after {
  content: " ";
  display: inline-block;
  width: 0;
  height: 100%;
  vertical-align: middle;
  margin-top: 1px;
}
.tree {
  margin-left:10px;
}
</style>