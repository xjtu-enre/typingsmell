<template>
  <layout>
    <div class="evaluation-body">
      <select-project></select-project>
    </div>
  </layout>
</template>
<script>
import { ref } from "vue";

import Layout from "../../components/Layout";
import SelectProject from "./components/SelectProject";

export default {
  name: "evaluation",
  components: {
    layout: Layout,
    "select-project": SelectProject,
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