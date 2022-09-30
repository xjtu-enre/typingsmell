<template>
  <div class="box">
    <layout>
      <div class="proj-box">
        <project-list></project-list>
      </div>
    </layout>
  </div>
</template>
<script>
import Layout from "../../components/Layout.vue";
import ProjectList from "./components/ProjectList.vue";
export default {
  components: {
    layout: Layout,
    "project-list": ProjectList,
  },
};
</script>
<style scoped>
.box {
  position: absolute;
  height: 100%;
  width: 100%;
  background-color: rgb(247, 247, 247);
}
.proj-box {
  box-sizing: border-box;
  padding: 20px 100px;
}
</style>