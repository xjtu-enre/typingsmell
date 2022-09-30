<template>
  <el-form
    ref="register"
    :model="registerForm"
    :rules="registerRules"
    label-width="100px"
    class="registerForm sign-up-form"
  >
    <el-form-item label="用户名" prop="username">
      <el-input v-model="registerForm.username" placeholder="用户名"></el-input>
    </el-form-item>
    <el-form-item label="密码" prop="password">
      <el-input
        v-model="registerForm.password"
        type="password"
        placeholder="输入密码"
      ></el-input>
    </el-form-item>
    <el-form-item label="确认密码" prop="password2">
      <el-input
        v-model="registerForm.password2"
        type="password"
        placeholder="输入确认密码"
      ></el-input>
    </el-form-item>

    <el-form-item>
      <el-button
        @click="handleRegister('register')"
        type="primary"
        class="submit-btn"
        :loading="registerLoading"
        >注册</el-button
      >
    </el-form-item>
  </el-form>
</template>

<script>
import { getCurrentInstance, reactive, ref } from "vue";
import { validUsername } from "@/utils/validate";
import { validPassword } from "@/utils/validate";
import { registerServer } from "@/api/user.js";

export default {
  setup() {
    const { proxy } = getCurrentInstance();

    // 注册方法
    const handleRegister = (formName) => {
      registerLoading.value = true;
      proxy.$refs[formName].validate((valid) => {
        if (valid) {
          registerServer({
            username: registerForm.username,
            password: registerForm.password,
          }).then(
            (res) => {
              registerLoading.value = false;
              proxy.$message({
                message: `${res.data}`,
                type: "success",
              });
            },
            () => {
              registerLoading.value = false;
            }
          );
        } else {
          console.log("error submit!!");
          return false;
        }
      });
    };

    const validateUsername = (rule, value, callback) => {
      if (!validUsername(value)) {
        callback(new Error("请输入用户名"));
      } else {
        callback();
      }
    };
    const validatePassword = (rule, value, callback) => {
      if (!validPassword(value)) {
        callback(new Error("密码包含字母与数字，6-16位"));
      } else {
        callback();
      }
    };
    var validatePassword2 = (rule, value, callback) => {
      if (value === "") {
        callback(new Error("请再次输入密码"));
      } else if (value !== proxy.registerForm.password) {
        callback(new Error("两次输入密码不一致!"));
      } else {
        callback();
      }
    };

    const registerForm = reactive({
      username: "",
      password: "",
      password2: "",
    });

    const registerRules = reactive({
      username: [
        {
          required: true,
          trigger: "blur",
          validator: validateUsername,
          message: "4-10位字母数字下划线",
        },
      ],
      password: [
        { required: true, trigger: "blur", validator: validatePassword },
      ],
      password2: [
        { required: true, trigger: "blur", validator: validatePassword2 },
      ],
    });

    const registerLoading = ref(false);

    return {
      handleRegister,
      registerForm,
      registerRules,
      registerLoading,
    };
  },
};
</script>
<style lang="less" scoped>
.registerForm {
  margin-top: 20px;
  background-color: #fff;
  padding: 20px 40px 20px 20px;
  border-radius: 5px;
  box-shadow: 0px 5px 10px #cccc;
  width: 400px;
}
</style>