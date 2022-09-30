<template>
  <el-form
    ref="login"
    :model="loginForm"
    :rules="loginRules"
    label-width="100px"
    class="loginForm sign-in-form"
  >
    <el-form-item label-width="0" prop="username">
      <el-input v-model="loginForm.username" placeholder="用户名" />
    </el-form-item>
    <el-form-item label-width="0" prop="password">
      <el-input
        v-model="loginForm.password"
        type="password"
        placeholder="密码"
      />
    </el-form-item>

    <el-form-item label-width="0">
      <el-button
        @click="handleLogin('login')"
        type="primary"
        class="submit-btn"
        :loading="loginLoading"
      >
        登录
      </el-button>
    </el-form-item>

    <!-- 找回密码 -->
    <!-- <div class="tiparea">
      <p>忘记密码? <a href="">立即找回</a></p>
    </div> -->
  </el-form>
</template>
<script>
import { reactive, ref } from "vue";
import { getCurrentInstance } from "vue";
import { useRouter } from "vue-router";
import { loginServer, getUserInfo } from "@/api/user";
import { setToken } from "@/utils/auth";
import { setInfo } from "@/utils/user";

const LoginAndUserInfoHandler = (proxy, formdata) => {
  const loginAction = () => {
    return loginServer(formdata).then((res) => {
      proxy.$message({
        message: "登录成功",
        type: "success",
      });
      // 登陆成功，存储token
      const { data } = res;
      setToken(data.token);

      return data;
    });
  };

  const userInfoAction = (data) => {
    const user = {
      user_id: data.user_id,
      user_type: data.user_type,
      username: "",
      nickname: "",
    };

    return getUserInfo(data.user_id).then((res) => {
      user.username = res.data.username;
      user.nickname = res.data.nickname;
      setInfo(JSON.stringify(user));
    });
  };

  return loginAction().then(userInfoAction);
};

export default {
  setup() {
    const { proxy } = getCurrentInstance();
    const router = useRouter();
    // 登录方法
    const handleLogin = (formName) => {
      proxy.$refs[formName].validate((valid) => {
        if (valid) {
          loginLoading.value = true;
          LoginAndUserInfoHandler(proxy, {
            username: loginForm.username,
            password: loginForm.password,
          }).then(
            () => {
              loginLoading.value = false;
              router.push("/");
            },
            () => {
              loginLoading.value = false;
            }
          );
        } else {
          console.log("error submit!!");
          return false;
        }
      });
    };

    const loginForm = reactive({
      loginForm: {
        username: "",
        password: "",
      },
    });

    const loginLoading = ref(false);

    return {
      handleLogin,
      loginForm,
      loginLoading,
      loginRules: {
        username: [
          { required: true, trigger: "blur", message: "请输入用户名" },
        ],
        password: [{ required: true, trigger: "blur", message: "请输入密码" }],
      },
    };
  },
};
</script>

<style scoped>
/* register */
.loginForm {
  margin-top: 20px;
  background: #fff;
  padding: 20px 40px 20px 20px;
  border-radius: 5px;
  box-shadow: 0px 5px 10px #cccc;
  width: 400px;
}
</style>