<template>
  <layout>
    <div class="evaluation-body">
      <commit-coverage></commit-coverage>
    </div>
  </layout>
</template>
<script>
import { ref } from "vue";

import Layout from "../../components/Layout";
import Commit from "./components/Commit";

export default {
  name: "evaluation",
  components: {
    layout: Layout,
    "commit-coverage": Commit,
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