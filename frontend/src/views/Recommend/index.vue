<template>
  <layout>
    <div class="rec-box">
      <h2 class="my-h2">Recommend</h2>
      <div class="rec-description">
        You can use this tool to recommend the files, which should be typed with
        priority, by <b>Degree Centrality</b>, <b>Design Rule Hierarchy</b>, or
        <b>Maintenance Cost Measurement</b>. You can also choose the proportion
        of recommended files by supplying the portion to the top option.
      </div>
      <el-divider />
      <div class="rec-body">
        <div class="rec-left">
          <h3 class="label-h3">The repository’s clone URL</h3>
          <div class="git-input">
            <div>
              <div>Git</div>
              <el-select
                v-model="state.gitOption"
                size="small"
                style="width: 150px; margin-top: 10px"
              >
                <el-option
                  v-for="item in state.gitOptions"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
                >
                </el-option>
              </el-select>
            </div>
            <div>
              <span class="xie-span">/</span>
            </div>
            <div>
              <div>Repository</div>
              <div style="width: 220px; margin-top: 10px">
                <el-input
                  placeholder="python/python"
                  v-model="state.gitUrl"
                  size="small"
                ></el-input>
              </div>
            </div>
          </div>
          <div class="option">
            <div>
              <div>Priority</div>
              <el-checkbox-group
                v-model="state.features"
                :min="1"
                :max="3"
                class="option-style"
              >
                <el-checkbox
                  v-for="feature in state.featureOptions"
                  :label="feature"
                  :key="feature"
                  >{{ feature }}
                </el-checkbox>
              </el-checkbox-group>
            </div>
            <div style="width: 150px">
              <div>Top</div>
              <div class="option-style" style="width: 100px">
                <el-select v-model="state.degreeTop" size="mini">
                  <el-option
                    v-for="item in state.topOptions"
                    :key="item"
                    :label="item"
                    :value="item"
                  >
                  </el-option>
                </el-select>
                <el-select v-model="state.mcTop" size="mini">
                  <el-option
                    v-for="item in state.topOptions"
                    :key="item"
                    :label="item"
                    :value="item"
                  >
                  </el-option>
                </el-select>
              </div>
            </div>
          </div>
          <div style="margin-top: 50px; text-align: end">
            <el-button @click="getRecommendFiles" :loading="state.calLoading"
              >Begin Clone</el-button
            >
          </div>
        </div>
        <div
          class="rec-right"
          v-loading="state.calLoading"
          element-loading-text="This may need some time..."
        >
          <el-empty
            v-if="state.fileList.length === 0"
            description="No content"
            style="margin: 0 auto"
          ></el-empty>
          <rec-card
            style="padding: 20px"
            v-for="item in state.fileList"
            :key="item"
            :fileList="item"
          ></rec-card>
        </div>
      </div>
    </div>
  </layout>
</template>
<script>
import { ref, getCurrentInstance } from "vue";
import Layout from "../../components/Layout";
import RecCard from "./components/RecCard";
import { recommendAfterFetch } from "../../api/recommend";

export default {
  components: {
    Layout,
    "rec-card": RecCard,
  },
  setup() {
    const { proxy } = getCurrentInstance();
    const state = ref({
      gitUrl: "",
      fileList: [],
      gitOptions: [
        { value: "https://github.com/", label: "https://github.com" },
        { value: "https://gitee.com/", label: "https://gitee.com" },
      ],
      gitOption: "https://github.com/",
      features: ["degree"],
      featureOptions: ["degree", "drh", "maintenance"],
      degreeTop: "10",
      mcTop: "10",
      topOptions: ["10", "15", "20", "30"],
      calLoading: false,
    });

    const getRecommendFiles = () => {
      state.value.calLoading = true;
      if (state.value.gitUrl === "") {
        proxy.$message.warning("Please input Repository Name");
        state.value.calLoading = false;
        return;
      }
      recommendAfterFetch({
        git_source: state.value.gitOption,
        git_url: state.value.gitUrl,
        features: state.value.features,
        top: [state.value.degreeTop, state.value.mcTop],
      }).then(
        (res) => {
          state.value.fileList = res.data.recommend;
          state.value.calLoading = false;
        },
        () => {
          state.value.calLoading = false;
        }
      );
    };
    return { state, getRecommendFiles };
  },
};
</script>
<style>
.rec-box {
  padding: 20px 100px;
  text-align: start;
}
.rec-description {
  margin-top: 15px;
  font-size: 14px;
  color: var(--color-fg-muted);
  flex: 1 100%;
}
.rec-body {
  display: flex;
}
.git-input {
  height: 100px;
  width: 400px;
  display: flex;
  margin-top: 20px;
}
.rec-left {
  margin: 20px 0;
  padding-right: 20px;
  border-right: 2px solid rgb(221, 221, 223);
}
.rec-right {
  width: 100%;
  padding: 20px;
  display: flex;
  flex-wrap: wrap;
  justify-content: space-around;
  overflow: hidden;
}
.my-h2 {
  font-size: 24px;
  font-weight: 400;
  flex: 1 1 auto;
}
.label-h3 {
  font-size: 20px;
  font-weight: 400 !important;
}
.el-divider--horizontal {
  margin: 15px 0;
}
.xie-span {
  float: left;
  padding-top: 30px;
  margin: 0 8px;
  font-size: 21px;
  color: var(--color-fg-muted);
}

.option {
  display: flex;
}

.option-style {
  width: 150px;
  height: 100px;
  padding-top: 10px;
  display: block;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}
</style>