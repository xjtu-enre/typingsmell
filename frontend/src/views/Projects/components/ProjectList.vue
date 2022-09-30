<template>
  <div>
    <div class="list-box">
      <div class="list-title">
        <div class="title-text">ProjectList</div>
        <div class="title-tool">
          <upload-proj></upload-proj>
          <el-input
            v-model="state.searchProj"
            size="large"
            placeholder="input project name to search"
            style="width: 300px"
          />
        </div>
      </div>
      <div class="list-header">
        <el-table
          v-loading="state.dataLoading"
          :data="
            state.projectList.filter(
              (data) =>
                !state.searchProj ||
                data.project_name
                  .toLowerCase()
                  .includes(state.searchProj.toLowerCase())
            )
          "
          style="width: 100%"
          max-height="350"
          fit
        >
          <el-table-column
            prop="project_name"
            label="ProjectName"
            width="200"
          />
          <el-table-column prop="version" label="Version" width="150" />
          <el-table-column prop="file" label="FileCount" width="100" />
          <el-table-column prop="loc" label="LoC" width="100" />
          <el-table-column prop="type_manner" label="TypeManner" width="150" />
          <el-table-column prop="git_url" label="GitUrl" width="250" />
          <el-table-column label="Operations">
            <template #default="scope">
              <el-button
                @click="getCoverage(scope.row.id, scope.row.project_name)"
                type="text"
                size="small"
              >
                Coverage
              </el-button>
              <el-button
                @click="getUsage(scope.row.id, scope.row.project_name)"
                type="text"
                size="small"
              >
                Usage
              </el-button>
              <el-button
                @click="getPattern(scope.row.id, scope.row.project_name)"
                type="text"
                size="small"
              >
                Pattern
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
      <div class="pagination">
        <el-pagination
          @current-change="handleCurrentChange"
          :current-page="state.currentPage"
          :page-size="state.currentPageSize"
          layout="total, prev, pager, next"
          :total="state.projectCount"
        >
        </el-pagination>
      </div>
    </div>
    <div>
      <el-dialog v-model="state.infoVisible" destroy-on-close width="800px">
        <div
          v-loading="state.graphDataLoading"
          element-loading-text="First loading need much time"
          id="typing-info"
          class="info-card"
        />
      </el-dialog>
    </div>
  </div>
</template>
<script>
import { onMounted, ref, getCurrentInstance } from "vue";
import UploadProj from "./UploadProj";
import { getProjectList } from "../../../api/proj";
import { getProjectCoverage } from "../../../api/coverage";
import { getProjectUsage } from "../../../api/usage";
import { getProjectPattern } from "../../../api/pattern";
import * as echarts from "echarts";
import { jsonToTable } from "../../../utils/jsonToTable";
export default {
  components: {
    "upload-proj": UploadProj,
  },
  setup() {
    const { proxy } = getCurrentInstance();
    var myChart;
    const state = ref({
      projectList: [],
      projectCount: 0,
      coverage: {},
      infoVisible: false,
      searchProj: "",
      currentPage: 1,
      currentPageSize: 10,
      dataLoading: false,
      graphDataLoading: false,
    });
    const showTypingInfo = (row) => {
      console.log(row);
      state.value.infoVisible = true;
    };

    const getProjects = (params) => {
      getProjectList(params).then(
        (res) => {
          state.value.projectList = res.data.res;
          state.value.projectCount = res.data.count;
          state.value.dataLoading = false;
        },
        () => {
          state.value.dataLoading = false;
        }
      );
    };

    const getCoverage = (project_id, project_name) => {
      state.value.infoVisible = true;
      state.value.graphDataLoading = true;
      getProjectCoverage(project_id).then(
        (res) => {
          showGraph(res.data, "Coverage", project_name);
        },
        () => {
          state.value.graphDataLoading = false;
        }
      );
    };

    const getUsage = (project_id, project_name) => {
      state.value.infoVisible = true;
      state.value.graphDataLoading = true;
      getProjectUsage(project_id).then(
        (res) => {
          showGraph(res.data, "Usage", project_name);
        },
        () => {
          state.value.graphDataLoading = false;
        }
      );
    };

    const getPattern = (project_id, project_name) => {
      state.value.infoVisible = true;
      state.value.graphDataLoading = true;
      getProjectPattern(project_id).then(
        (res) => {
          showGraph(res.data.pattern_count, "Pattern", project_name);
        },
        () => {
          state.value.graphDataLoading = false;
        }
      );
    };

    const showGraph = (dataSet, infoType, project_name) => {
      proxy.$nextTick(() => {
        if (myChart !== null && myChart !== "" && myChart !== undefined) {
          myChart.dispose();
        }
        myChart = echarts.init(document.getElementById("typing-info"));
        var option = jsonToTable(dataSet, infoType, project_name);
        myChart.setOption(option);
        state.value.graphDataLoading = false;
      });
    };

    const handleCurrentChange = (currentPage) => {
      state.value.dataLoading = true;
      getProjectList({
        page: currentPage - 1,
        limit: state.value.currentPageSize,
      }).then(
        (res) => {
          state.value.projectList = res.data.res;
          state.value.projectCount = res.data.count;
          state.value.dataLoading = false;
          state.value.currentPage = currentPage;
        },
        (res) => {
          proxy.$message.error(res.msg);
          state.value.dataLoading = false;
        }
      );
    };

    onMounted(() => {
      state.value.dataLoading = true;
      proxy.getProjects({
        page: state.value.currentPage - 1,
        limit: state.value.currentPageSize,
      });
    });

    return {
      state,
      showTypingInfo,
      getProjects,
      getCoverage,
      getUsage,
      getPattern,
      handleCurrentChange,
      showGraph,
    };
  },
};
</script>

<style scoped>
.list-box {
  padding: 30px;
  background-color: #ffffff;
  height: 550px;
  position: relative;
}
.list-title {
  box-sizing: border-box;
  height: 160px;
  width: 100%;
  background-color: #ffffff;
}
.title-text {
  box-sizing: border-box;
  height: 70px;
  padding: 10px;
  font-size: 28px;
  text-align: start;
}
.title-tool {
  box-sizing: border-box;
  height: 90px;
  padding: 10px;
  display: flex;
  justify-content: space-between;
}
.pagination {
  position: absolute;
  bottom: 10px;
  height: 30px;
  padding: 10px;
  right: 10px;
}

.info-card {
  height: 400px;
  width: 700px;
  padding: 0;
  text-align: center;
  background: #fff;
}
</style>