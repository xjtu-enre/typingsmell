import axios from 'axios';
import { ElMessage } from 'element-plus';

const baseUrl = 'http://127.0.0.1:5000';

const service = axios.create({
  baseURL: baseUrl,
  timeout: 5000,
});

service.interceptors.response.use(
  (response) => {
    const res = response.data;

    if (res.msg !== 'success') {
      ElMessage({
        message: res.msg || 'Error',
        type: 'error',
        duration: 5 * 1000,
      });
      return Promise.reject(new Error(res.msg || 'Error'));
    } else {
      return res;
    }
  },
  (error) => {
    ElMessage({
      message: error.message,
      type: 'error',
      duration: 5 * 1000,
    });
    return Promise.reject(error);
  }
);

export default service;
