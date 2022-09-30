<template>
  <el-card shadow="hover" class="evaluation-card">
    <el-select
      v-model="state.sourceProjects"
      multiple
      clearable
      filterable
      :multiple-limit="10"
      placeholder="choose"
      value-key="project_id"
      style="width: 600px"
    >
      <el-option
        v-for="item in state.projectList"
        :key="item.project_id"
        :label="item.usage.project_name"
        :value="item"
      >
      </el-option>
    </el-select>
    <el-button @click="handleChoose" style="margin: 0 10px"
      >GenerateChart</el-button
    >
    <el-select
      v-model="state.metric"
      placeholder="SortBy"
      @change="handleSortUsage"
      style="width: 150px"
    >
      <el-option
        v-for="item in state.metrics"
        :key="item"
        :label="item"
        :value="item"
      >
      </el-option>
    </el-select>
    <div id="usage" class="bar-card" v-loading="state.dataLoading" />
  </el-card>
</template>
<script>
import { onMounted, ref, getCurrentInstance } from "vue";
import { listToTable } from "../../../utils/jsonToTable.js";
import { sortGraph } from "../../../utils/sort";
import { getUsage } from "../../../api/usage";
import * as echarts from "echarts";

export default {
  setup() {
    const { proxy } = getCurrentInstance();
    var myChart;
    const state = ref({
      projectList: [],
      sourceProjects: [],
      metric: "",
      metrics: [],
      dataLoading: false,
    });
    onMounted(() => {
      proxy.handleInit();
    });

    const handleInit = () => {
      state.value.dataLoading = true;
      getUsage().then((res) => {
        if (res.msg === "success") {
          state.value.dataLoading = false;
          state.value.projectList = res.data.res;
          state.value.metrics = res.data.metrics;
          proxy.handleChoose();
        } else {
          proxy.$message.error("Data load filed");
        }
      });
    };

    const handleSortUsage = () => {
      if (myChart !== null && myChart !== "" && myChart !== undefined) {
        myChart.dispose();
      }
      myChart = echarts.init(document.getElementById("usage"));
      var showData;
      if (state.value.sourceProjects.length === 0) {
        showData = state.value.projectList;
      } else {
        showData = state.value.sourceProjects;
      }
      var option = listToTable(
        "usage",
        "line",
        sortGraph(showData, state.value.metric)
      );
      option && myChart.setOption(option);
    };
    const handleChoose = () => {
      if (myChart !== null && myChart !== "" && myChart !== undefined) {
        myChart.dispose();
      }
      myChart = echarts.init(document.getElementById("usage"));
      var showData;
      if (state.value.sourceProjects.length === 0) {
        showData = state.value.projectList;
      } else {
        showData = state.value.sourceProjects;
      }
      var option = listToTable("usage", "line", showData);
      option && myChart.setOption(option);
    };
    return { state, handleInit, handleChoose, handleSortUsage };
  },
};
</script>
<style scoped>
.evaluation-card {
  margin: 10px 0;
}
.bar-card {
  height: 430px;
  margin: 20px;
  padding: 20px 100px;
  text-align: center;
  background: #fff;
}
</style>