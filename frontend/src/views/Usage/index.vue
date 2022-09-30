<template>
  <layout>
    <div class="evaluation-body">
      <usage></usage>
    </div>
  </layout>
</template>
<script>
import { ref } from "vue";

import Layout from "../../components/Layout";
import Usage from "./components/Usage";

export default {
  name: "evaluation",
  components: {
    layout: Layout,
    usage: Usage,
  },

  setup() {
    // const { proxy } = getCurrentInstance();
    const activeName = ref("1");

    return { activeName };
  },
};
</script>
<style>
.evaluation-body {
  padding: 20px 100px;
}
</style>