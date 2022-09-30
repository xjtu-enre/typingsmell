<template>
  <div
    id="test"
    style="
      height: 550px;
      overflow-y: scroll;
      overflow-x: hidden;
    "
  >
    <pre
      class="line-numbers"
      :data-line="keyline"
      :data-start="startl"
      style="overflow: hidden"
    ><code class="language-python">{{codetext}}</code></pre>
  </div>
  <el-button @click="toNext">next</el-button>
</template>
<script>
import { onUpdated, getCurrentInstance, ref } from "vue";
import Prism from "prismjs"; //引入插件
// import "prismjs/themes/prism-coy.css"  //引入官方的css
import "../../../assets/themes/prism-mycoy.css"; //引入自己修改过的css。
export default {
  name: "demo",
  props: {
    codetext: String,
    keyline: String,
    startLines: Array,
    startl: Number,
  },
  setup() {
    const { proxy } = getCurrentInstance();
    const index = ref(0);
    const lenStart = ref(0);
    onUpdated(() => {
      Prism.highlightAll();
      proxy.handleInit();
    });

    const handleInit = () => {
      index.value = 0;
      lenStart.value = proxy.startLines.length;
      proxy.scrollToLine(0);
    };

    const scrollToLine = (lineNum) => {
      const LINEHEIGHT = 16 * 1.5;
      var elem = document.getElementById("test");
      var myOff = LINEHEIGHT * lineNum;
      elem.scrollTo({
        top: myOff,
        behavior: "smooth",
      });
    };

    const toNext = () => {
      var startKey = index.value % lenStart.value;
      scrollToLine(proxy.startLines[startKey] - 1);
      index.value += 1;
    };

    return { handleInit, index, scrollToLine, toNext };
  },
};
</script>
