<template>
  <div class="container" :class="{ mode: tmode }">
    <!--form 表单容器-->
    <div class="forms-container">
      <div class="signin-signup">
        <!-- 登录 -->
        <Login v-if="mode === false" />
        <!-- 注册 -->
        <Register v-if="mode === true" />
      </div>
    </div>
    <!-- 左右切换动画 -->
    <div class="panels-container">
      <div class="panel left-panel">
        <div class="content">
          <h3>湖南大学XXX实验室</h3>
          <p>AI服务平台</p>
          <el-button @click="chageMode">注册</el-button>
        </div>
        <img
          src="@/assets/logo.png"
          class="image"
          alt=""
          @click="handleBackHome"
        />
      </div>
      <div class="panel right-panel">
        <div class="content">
          <h3>湖南大学XXX实验室</h3>
          <p>AI服务平台</p>
          <el-button @click="chageMode">登录</el-button>
        </div>
        <img
          src="@/assets/logo.png"
          class="image"
          alt=""
          @click="handleBackHome"
        />
      </div>
    </div>
  </div>
</template>
<script>
import { ref } from "vue";
import { useRouter } from "vue-router";
import Login from "./components/Login";
import Register from "./components/Register";

export default {
  name: "LoginRegister",
  components: { Login, Register },
  setup() {
    const router = useRouter();
    const mode = ref(false);
    const tmode = ref(false);
    const chageMode = () => {
      tmode.value = !tmode.value;
      setTimeout(() => {
        mode.value = !mode.value;
      }, 1200);
    };

    const handleBackHome = () => {
      router.replace("/");
    };

    return {
      mode,
      tmode,
      chageMode,
      handleBackHome,
    };
  },
};
</script>
<style scoped>
.container {
  position: relative;
  width: 100%;
  background-color: #fff;
  min-height: 100vh;
  overflow: hidden;
}

.forms-container {
  position: absolute;
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
}

.signin-signup {
  position: absolute;
  top: 50%;
  transform: translate(-50%, -50%);
  left: 75%;
  width: 400px;
  transition: 1s 0.7s ease-in-out;
  display: grid;
  grid-template-columns: 1fr;
  z-index: 5;
}

.el-button {
  background: rgba(30, 30, 30, 0.8);
  color: #fff;
}

.panels-container {
  position: absolute;
  height: 100%;
  width: 100%;
  top: 0;
  left: 0;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
}

.container:before {
  content: "";
  position: absolute;
  height: 2000px;
  width: 2000px;
  top: -10%;
  right: 48%;
  transform: translateY(-50%);
  background-image: linear-gradient(
    -45deg,
    rgb(30, 30, 30) 0%,
    rgb(30, 30, 30) 100%
  );
  transition: 1.8s ease-in-out;
  border-radius: 50%;
  z-index: 6;
}

.image {
  width: 100%;
  transition: transform 1.1s ease-in-out;
  transition-delay: 0.4s;
}

.panel {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  justify-content: space-around;
  text-align: center;
  z-index: 6;
}

.left-panel {
  pointer-events: all;
  padding: 3rem 17% 2rem 12%;
}

.right-panel {
  pointer-events: none;
  padding: 3rem 12% 2rem 17%;
}

.panel .content {
  width: 100%;
  color: #fff;
  transition: transform 0.9s ease-in-out;
  transition-delay: 0.6s;
}

.panel h3 {
  font-weight: 600;
  line-height: 1;
  font-size: 1.5rem;
}

.panel p {
  font-size: 0.95rem;
  padding: 0.7rem 0;
}

.btn.transparent {
  margin: 0;
  background: none;
  border: 2px solid #fff;
  width: 130px;
  height: 41px;
  font-weight: 600;
  font-size: 0.8rem;
}

.right-panel .image,
.right-panel .content {
  transform: translateX(800px);
}

/* ANIMATION */

.container.mode:before {
  transform: translate(100%, -50%);
  right: 52%;
}

.container.mode .left-panel .image,
.container.mode .left-panel .content {
  transform: translateX(-800px);
}

.container.mode .signin-signup {
  left: 25%;
}

.container.mode form.sign-up-form {
  opacity: 1;
  z-index: 2;
}

.container.mode form.sign-in-form {
  opacity: 0;
  z-index: 1;
}

.container.mode .right-panel .image,
.container.mode .right-panel .content {
  transform: translateX(0%);
}

.container.mode .left-panel {
  pointer-events: none;
}

.container.mode .right-panel {
  pointer-events: all;
}

@media (max-width: 870px) {
  .container {
    min-height: 800px;
    height: 100vh;
  }

  .signin-signup {
    width: 100%;
    top: 95%;
    transform: translate(-50%, -100%);
    transition: 1s 0.8s ease-in-out;
  }

  .signin-signup,
  .container.mode .signin-signup {
    left: 50%;
  }

  .panels-container {
    grid-template-columns: 1fr;
    grid-template-rows: 1fr 2fr 1fr;
  }

  .panel {
    flex-direction: row;
    justify-content: space-around;
    align-items: center;
    padding: 2.5rem 8%;
    grid-column: 1 / 2;
  }

  .right-panel {
    grid-row: 3 / 4;
  }

  .left-panel {
    grid-row: 1 / 2;
  }

  .image {
    width: 200px;
    transition: transform 0.9s ease-in-out;
    transition-delay: 0.6s;
  }

  .panel .content {
    padding-right: 15%;
    transition: transform 0.9s ease-in-out;
    transition-delay: 0.8s;
  }

  .panel h3 {
    font-size: 1.2rem;
  }

  .panel p {
    font-size: 0.7rem;
    padding: 0.5rem 0;
  }

  .btn.transparent {
    width: 110px;
    height: 35px;
    font-size: 0.7rem;
  }

  .container:before {
    width: 1500px;
    height: 1500px;
    transform: translateX(-50%);
    left: 30%;
    bottom: 68%;
    right: initial;
    top: initial;
    transition: 2s ease-in-out;
  }

  .container.mode:before {
    transform: translate(-50%, 100%);
    bottom: 32%;
    right: initial;
  }

  .container.mode .left-panel .image,
  .container.mode .left-panel .content {
    transform: translateY(-300px);
  }

  .container.mode .right-panel .image,
  .container.mode .right-panel .content {
    transform: translateY(0px);
  }

  .right-panel .image,
  .right-panel .content {
    transform: translateY(300px);
  }

  .container.mode .signin-signup {
    top: 5%;
    transform: translate(-50%, 0);
  }
}

@media (max-width: 570px) {
  form {
    padding: 0 1.5rem;
  }

  .image {
    display: none;
  }

  .panel .content {
    padding: 0.5rem 1rem;
  }

  .container {
    padding: 1.5rem;
  }

  .container:before {
    bottom: 72%;
    left: 50%;
  }

  .container.mode:before {
    bottom: 28%;
    left: 50%;
  }
}
/* 控制login & register显示 */
/* form {
  padding: 0rem 5rem;
  transition: all 0.2s 0.7s;
  overflow: hidden;
}

form.sign-in-form {
  z-index: 2;
}

form.sign-up-form {
  opacity: 0;
  z-index: 1;
}

.submit-btn {
  width: 100%;
} */
</style>