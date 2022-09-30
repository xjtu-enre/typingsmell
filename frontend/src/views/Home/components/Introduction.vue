<template>
  <div class="intro-box">
    <div class="inner-box">
      <el-col>
        <div class="intro-title">Introduction</div>
        <el-row>
          <div class="function">
            <div class="func-title">TypingCoverageDetection</div>
            <div class="func-intro">To get typing coverage of a project</div>
          </div>
          <div class="function">
            <div class="func-title">DegreeCentrality</div>
            <div class="func-intro">
              This module computes the degree centrality for files based on the
              ADG built by Dependency Structure Analysis.
            </div>
          </div>
          <div class="function">
            <div class="func-title">MaintenanceCostMeasurement</div>
            <div class="func-intro">
              Based on commit records, this module quantifies the effort taken
              on maintaining source files. Six measures are computed, including
              #commit; #changeLoc; #author; issue; #issueCmt; #issueLoc
            </div>
          </div>
        </el-row>
      </el-col>
    </div>
  </div>
</template>

<script>
export default {};
</script>

<style lang="less" scoped>
.intro-box {
  height: 400px;
  display: flex;
  padding: 25px 100px;
}

.inner-box {
  box-sizing: border-box;
  max-width: 100%;
  display: flex;
  margin: 60px auto 0;
  height: auto;
  justify-content: center;
  overflow: hidden;
  // align-items: center;
}

.el-col {
  font-size: 14px;
  display: block;
}

.intro-title {
  font-size: 32px;
}

.function {
  display: table-cell;
  position: relative;
  width: 330px;
  margin: 50px 25px;
}

.func-title {
  font-size: 22px;
  height: 38px;
  line-height: 38px;
  font-weight: 700;
}

.func-intro {
  font-size: 15px;
  height: 100px;
  line-height: 38px;
  margin-top: 30px;
  padding: 0 25px;
}
</style>