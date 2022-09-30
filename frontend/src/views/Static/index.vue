<template>
  <layout>
    <div class="rec-box">
      <h2 class="my-h2">PatternCodeView</h2>
      <div class="rec-description">
        You can use this tool to recommend the files, which should be typed with
        priority, by <b>Degree Centrality</b>, <b>Design Rule Hierarchy</b>, or
        <b>Maintenance Cost Measurement</b>. You can also choose the proportion
        of recommended files by supplying the portion to the top option.
      </div>
      <el-divider />
      <div class="pattern-view-box">
        <div class="pattern-view-header">
          <el-select
            v-model="state.currentProject"
            clearable
            filterable
            size="large"
            placeholder="Choose a project"
            value-key="id"
            style="width: 50%;position: relative;left: 25%"
            @change="getPattern"
          >
            <el-option
              v-for="item in state.projectList"
              :key="item.id"
              :label="item.project_name"
              :value="item"
            >
            </el-option>
          </el-select>
        </div>
        <div
            class="pattern-view-indexs"
            v-loading="state.patternInfoLoading"
            element-loading-custom-class="custom-loading"
          >
          <div style="display: flex;height: 50%">
            <div style="width: 45%">
              <div>计算出的类型注解实践结果如下</div>
              <el-cascader
              v-model="state.filePath"
              size="small"
              :options="state.pattern_info"
              :show-all-levels="false"
              @change="getFile"
              style="margin: 20px 0px"
                ></el-cascader>
              <div>
                <el-radio-group v-model="apattern">
                  <el-radio :label="1" style="margin: 5px 0px">
                    ApiVisibility (total count: {{state.pattern_count.ApiVisibility}})
                  </el-radio><br/>
                  <el-radio :label="2" style="margin: 5px 0px">
                    ExtensionTyping (total count: {{state.pattern_count.ExtensionTyping}})
                  </el-radio><br/>
                  <el-radio :label="3" style="margin: 5px 0px">
                    Overload (total count: {{state.pattern_count.Overload}})
                  </el-radio><br/>
                  <el-radio :label="4" style="margin: 5px 0px">
                    TypeCompatibility (total count: {{state.pattern_count.TypingCompatibility}})
                  </el-radio><br/>
                  <el-radio :label="5" style="margin: 5px 0px">
                    FunctionalVariable (total count: {{state.pattern_count.FunctionalVariable}})
                  </el-radio><br/>
                  <el-radio :label="6" style="margin: 5px 0px">
                    BaseclassPresentation (total count: {{state.pattern_count.BaseclassPresentation}})
                  </el-radio><br/>
                </el-radio-group>
              </div>
            </div>
            <div style="width: 45%;left: 55%">
              出现文件列表<br/>
              {{bpattern}}
            </div>
          </div>

          <div style="height: 45%;top: 55%">
            高亮块列表
          </div>
        </div> 
        <div class="pattern-view-body" v-loading="state.dataLoading">
          <code-view
            :codetext="state.code"
            :keyline="state.hightLightLines"
            :startLines="state.startLines"
            :startl="state.start"
          ></code-view>
        </div>
      </div>
    </div>
  </layout>
</template>
<script>
import { ref, getCurrentInstance, onMounted, watch } from "vue";
import Layout from "../../components/Layout";

import CodeView from "./components/CodeView.vue";
import { getProjectFile } from "../../api/file.js";
import { getProjectList } from "../../api/proj";
import { getProjectPattern } from "../../api/pattern";
import { toOption } from "../../utils/jsonToTable";

export default {
  components: {
    Layout,
    "code-view": CodeView,
  },
  setup() {
    const { proxy } = getCurrentInstance();
    var apattern = 2;
    var bpattern = 1;
    watch(apattern, () => {bpattern=apattern});
    const state = ref({
      pattern_info: [],
      pattern_count: [],
      code: ``,
      hightLightLines: "",
      startLines: [],
      start: 1,
      projectList: [],
      dataLoading: false,
      patternInfoLoading: false,
      currentProject: {},
      filePath: "",
      dirPath: "",
      pathList: [],
      currentPath: "",
      dirList: [],
      fileList: [],
    });
    const getAllProject = () => {
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
    const getPattern = () => {
      var project_id = state.value.currentProject.id;
      state.value.patternInfoLoading = true;
      state.value.pattern_info = [];
      getProjectPattern(project_id).then(
        (res) => {
          state.value.pattern_info = toOption(res.data.pattern_info);
          state.value.pattern_count = res.data.pattern_count;
          state.value.patternInfoLoading = false;
        },
        () => {
          state.value.patternInfoLoading = false;
        }
      );
    };

    const getFile = () => {
      state.value.dataLoading = true;
      getProjectFile({
        project_id: state.value.currentProject.id,
        file_path: state.value.filePath[1].filePath,
      }).then(
        (res) => {
          state.value.code = res.data;
          state.value.hightLightLines = state.value.filePath[1].lines;
          state.value.startLines = state.value.filePath[1].startLines;
          state.value.dataLoading = false;
        },
        () => {
          state.value.dataLoading = false;
        }
      );
    };
    onMounted(() => {
      state.value.dirPath = "mini-back";
      proxy.getAllProject();
    });
    return {
      getAllProject,
      state,
      getPattern,
      getFile,
      apattern,
      bpattern
    };
  },
};
</script>
<style>
.pattern-view-box {
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
}
.pattern-view-header {
  /* min-width: 400px; */
  width: 100%;
  margin: 20px 0;
  text-align: start;
  /* border-right: 2px solid rgb(221, 221, 223); */
}
.pattern-view-indexs {
  /* display: flex; */
  width: 50%;
  /* flex-wrap: wrap; */
}
.pattern-view-body {
  position: relative;
  min-width: 400px;
  width: 50%;
  display: flex;
  flex-wrap: wrap;
  justify-content: space-around;
  overflow: hidden;
}
.divider {
  margin: 0 auto;
  padding: 0 5px;
}
.custom-loading .el-loading-spinner .circular {
  width: 20px;
}
</style>