import { createApp } from 'vue';
import ElementPlus from 'element-plus';
import 'element-plus/lib/theme-chalk/index.css';
import App from './App.vue';
import router from './router/router.js';
import * as echarts from 'echarts';
import uploader from 'vue-simple-uploader';

const app = createApp(App);
app.use(router);
app.use(ElementPlus);
app.use(echarts);
app.use(uploader);
app.mount('#app');
