<template>
  <layout>
    <swiper :url="imageArray" />
    <introduction></introduction>
  </layout>
</template>
<script>
import { ref } from "vue";
import Layout from "../../components/Layout.vue";
import Swiper from "../../components/Swiper";
import Introduction from "./components/Introduction";
export default {
  name: "home",
  components: {
    Swiper,
    layout: Layout,
    introduction: Introduction,
  },

  setup() {
    const activeName = ref("1");
    const imageArray = ["logo.png", "logo.png"];

    return { activeName, imageArray };
  },
};
</script>
<style>
.module-intro {
  height: 300px;
  margin: 20px;
  padding: 20px 100px;
  text-align: center;
}
</style>