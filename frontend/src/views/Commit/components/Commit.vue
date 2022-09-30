<template>
  <el-card shadow="hover" class="evaluation-card">
    <el-select
      v-model="state.current_project"
      clearable
      filterable
      placeholder="Choose a project"
      value-key="id"
      style="width: 600px"
    >
      <el-option
        v-for="item in state.projectList"
        :key="item.id"
        :label="item.project_name"
        :value="item"
      >
      </el-option>
    </el-select>
    <el-button @click="handleChoose" style="margin: 0 10px"
      >GenerateChart</el-button
    >
    <div id="commit-cov" class="bar-card" v-loading="state.dataLoading" />
    <div v-if="state.projectSelected">Period: 
      <el-date-picker
        v-model="state.timePeriod"
        type="daterange"
        unlink-panels
        start-placeholder="Start Date"
        end-placeholder="End Date"
        :shortcuts="state.shortcuts"
        value-format="YYYY-MM-DD"
        @change="changePeriod"
      >
      </el-date-picker>
    </div>
    <!-- <div style="margin: 20px"><hr/>
      {{state.showData}}
    </div> -->
  </el-card>
</template>
<script>
import { onMounted, ref, getCurrentInstance } from "vue";
import { listToTable } from "../../../utils/jsonToTable.js";
import { selectTimePeriod } from "../../../utils/jsonToTable.js";
import { getProjectList } from "../../../api/proj";
import { getCommitCoverage } from "../../../api/coverage";
import { ElMessage } from 'element-plus'
import * as echarts from "echarts";

export default {
  setup() {
    const { proxy } = getCurrentInstance();
    var myChart;
    const state = ref({
      timePeriod: '',
      timePeriod_buf: '',
      projectSelected: false,
      data: '',
      showData: '',
      projectList: [],
      current_project: {},
      dataLoading: false,
      shortcuts: [
      {
        text: 'Last week',
        value: () => {
          const end = new Date()
          const start = new Date()
          start.setTime(start.getTime() - 3600 * 1000 * 24 * 7)
          return [start, end]
        },
      },
      {
        text: 'Last month',
        value: () => {
          const end = new Date()
          const start = new Date()
          start.setMonth(start.getMonth() - 1)
          return [start, end]
        },
      },
      {
        text: 'Last 3 months',
        value: () => {
          const end = new Date()
          const start = new Date()
          start.setMonth(start.getMonth() - 3)
          return [start, end]
        },
      },
      {
        text: 'Last year',
        value: () => {
          const end = new Date()
          const start = new Date()
          start.setFullYear(start.getFullYear() - 1)
          return [start, end]
        },
      },
      ],
    });
    onMounted(() => {
      proxy.handleInit();
    });

    const handleInit = () => {
      getProjectList({ page: 0, limit: 0 }).then(
        (res) => {
          state.value.projectList = res.data.res;
          state.value.dataLoading = false;
        },
        () => {
          state.value.dataLoading = false;
        }
      );
    };

    const handleChoose = () => {
      state.value.dataLoading = true;
      if (myChart !== null && myChart !== "" && myChart !== undefined) {
        myChart.dispose();
      }
      myChart = echarts.init(document.getElementById("commit-cov"));
      getCommitCoverage({ project_id: state.value.current_project.id }).then(
        (res) => {
          state.value.data = res.data;
          state.value.showData = state.value.data;
          var option = listToTable("commit", "line", state.value.showData);
          option && myChart.setOption(option);
          state.value.timePeriod = '';
          state.value.dataLoading = false;
          state.value.projectSelected = true;
        },
        () => {
          state.value.dataLoading = false;
        }
      );
    };
    const changePeriod = () => {
      state.value.dataLoading = true;
      let filteredDate = selectTimePeriod(state.value.timePeriod, state.value.data);//添加时间筛选
      if(filteredDate.length == 0) {
        ElMessage.error('No Commit in this period!');
        state.value.timePeriod = state.value.timePeriod_buf;
      } else {
        state.value.timePeriod_buf = state.value.timePeriod;
        if (myChart !== null && myChart !== "" && myChart !== undefined) {
          myChart.dispose();
        }
        myChart = echarts.init(document.getElementById("commit-cov"));
        state.value.showData = filteredDate;
        var option = listToTable("commit", "line", state.value.showData);
        option && myChart.setOption(option);
      }
      state.value.dataLoading = false;
      state.value.projectSelected = true;
    };
    return { state, handleInit, handleChoose, changePeriod };
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