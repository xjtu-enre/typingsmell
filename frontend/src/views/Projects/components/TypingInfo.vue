<template>
  <div>
    <div id="typing-info" class="bar-card" />
  </div>
</template>
<script>
import { getCurrentInstance, onMounted } from "vue";
import * as echarts from "echarts";
import { jsonToTable } from "../../../utils/jsonToTable";
export default {
  name: "evaluation",
  props: {
    dataSet: Object,
    infoType: String,
  },

  setup() {
    const { proxy } = getCurrentInstance();

    const showCoverage = () => {
      var chartDom = document.getElementById("typing-info");
      var myChart = echarts.init(chartDom);
      var option = jsonToTable(proxy.dataSet, proxy.project, proxy.infoType);
      option && myChart.setOption(option);
    };
    onMounted(() => {
      proxy.showCoverage();
    });

    return { showCoverage };
  },
};
</script>
<style>
.evaluation-card {
  margin: 10px 0;
  text-align: center;
}
.bar-card {
  height: 300px;
  width: 700px;
  padding: 0;
  text-align: center;
  background: #fff;
}
</style>