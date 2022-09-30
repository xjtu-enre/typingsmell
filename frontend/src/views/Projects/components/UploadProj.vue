<template>
  <div>
    <el-dropdown
      split-button
      type="primary"
      @click="handleClick"
      @command="handleMode"
    >
      {{ state.mode }}
      <template #dropdown>
        <el-dropdown-menu>
          <el-dropdown-item command="uploadFolder"
            >Upload Folder</el-dropdown-item
          >
          <el-dropdown-item command="uploadFiles"
            >Upload Files</el-dropdown-item
          >
        </el-dropdown-menu>
      </template>
    </el-dropdown>
  </div>
  <el-dialog
    title="Upload Project"
    v-model="state.uploadDisable"
    destroy-on-close
    :close-on-click-modal="false"
    :close-on-press-escape="false"
  >
    <el-dialog
      width="30%"
      title="input project path"
      v-model="state.innerVisible"
      append-to-body
      :show-close="false"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
    >
      <el-input
        placeholder="es: root/tree1/sontree/"
        v-model="state.currentPath"
        clearable
      />
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="handleInputCancel">取 消</el-button>
          <el-button type="primary" @click="handleInputConfirm"
            >确 定</el-button
          >
        </span>
      </template>
    </el-dialog>
    <div class="add-select">
      Add a new project A project contains all '.py' and '.pyi' files. Already
      have a project online github?
      <div>Import a repository.</div>
    </div>
    <el-divider></el-divider>
    <div class="add-dialog">
      <el-form
        ref="project"
        :model="projectForm"
        :rules="projectRules"
        label-width="120px"
      >
        <el-form-item label="ProjectName" prop="project_name" required>
          <el-input
            v-model="projectForm.project_name"
            placeholder="input project name"
          />
        </el-form-item>
        <el-form-item label="Version" prop="version" required>
          <el-input
            v-model="projectForm.version"
            placeholder="input project version"
          />
        </el-form-item>
        <el-form-item label="FileCount" prop="file" required>
          <el-input
            v-model="projectForm.file"
            disabled
            placeholder="auto fill after upload project"
          />
        </el-form-item>
        <el-form-item label="UploadProject" required>
          <el-upload
            class="upload-demo"
            ref="uploadProj"
            action="action"
            name="proj"
            :on-remove="handleRemove"
            :on-exceed="handleExceed"
            :before-upload="handleBeforeUpload"
            :on-change="handleChange"
            :http-request="handleUpload"
            :file-list="state.fileList"
            multiple
            :auto-upload="false"
          >
            <template #trigger>
              <el-button size="small" type="primary">SELECT</el-button>
            </template>
            <el-button
              style="margin-left: 10px"
              size="small"
              type="primary"
              @click="handleSubmit"
              >CONFIRM</el-button
            >
            <template #tip>
              <div class="el-upload__tip" style="margin: 0">
                {{ state.uploadTip }}
              </div>
            </template>
          </el-upload>
        </el-form-item>
      </el-form>
    </div>
    <div style="text-align: center">
      <el-button type="primary" @click="handleAddproject('project')">
        + Add</el-button
      >
    </div>
  </el-dialog>
</template>
<script>
import { ref, getCurrentInstance, reactive } from "vue";
import { uploadProject, addProject } from "@/api/proj";
export default {
  setup() {
    const { proxy } = getCurrentInstance();
    const state = ref({
      mode: "uploadFolder",
      uploadDisable: false,
      uploadLoading: false,
      fileUploadVisible: false,
      innerVisible: false,
      currentPath: "",
      uploadTip: "请从项目根目录上传，系统自动忽略'__pycache__'及内部文件",
      fileList: [],
      refusedFileList: [],
      filePathList: [],
    });
    const projectForm = reactive({
      projectForm: {
        project_name: "",
        version: "",
        file: 0,
      },
    });

    const handleMode = (command) => {
      state.value.mode = command;
    };

    const handleClick = () => {
      state.value.uploadDisable = true;
      if (state.value.mode === "uploadFolder") {
        state.value.uploadTip =
          "请从项目根目录上传，系统自动忽略'__pycache__'及内部文件";
        proxy.$nextTick(() => {
          document.getElementsByClassName(
            "el-upload__input"
          )[0].webkitdirectory = true;
        });
      } else {
        state.value.uploadTip = "选择文件并输入文件项目路径并上传";
        proxy.$nextTick(() => {
          document.getElementsByClassName(
            "el-upload__input"
          )[0].webkitdirectory = false;
        });
      }
    };

    const handleBeforeUpload = (file) => {
      const filename = file.name;
      const fileType = filename.split(".")[filename.split(".").length - 1];
      if (fileType.indexOf("py") === -1) {
        proxy.$message.warning(`file: ${filename}格式不正确，只接受py后缀文件`);
        return false;
      } else if (fileType !== "py") {
        return false;
      }
    };

    const handleRemove = (file, fileList) => {
      proxy.$message.warning(
        `上传文件列表移除: ${file.name} , 当前文件中包含 ${fileList.length} 个文件`
      );
    };

    const handleChange = (file, fileList) => {
      const filename = file.name;
      const fileType = filename.split(".")[filename.split(".").length - 1];
      if (fileType.indexOf("py") === -1) {
        if (state.value.mode === "uploadFiles") {
          proxy.$message.warning(
            `file: ${filename}格式不正确，只接受py、pyi后缀文件`
          );
        } else {
          state.value.refusedFileList.unshift(filename);
          if (state.value.refusedFileList.length === 10) {
            var refusedFiles = "";
            for (var i = 0; i < 10; i++) {
              refusedFiles += `${state.value.refusedFileList[i]}、`;
            }
            proxy.$message({
              message: `files: ${refusedFiles}等格式不正确，只接受py、pyi后缀文件`,
              duration: 5000,
              type: "warning",
            });
          }
        }
        fileList.splice(-1, 1);
      } else if (fileType !== "py") {
        fileList.splice(-1, 1);
      } else {
        if (state.value.mode === "uploadFiles") {
          state.value.innerVisible = true;
        }
      }
    };

    const handleExceed = (files, fileList) => {
      proxy.$message.warning(
        `当前限制选择 3 个文件，本次选择了 ${files.length} 个文件，共选择了 ${
          files.length + fileList.length
        } 个文件`
      );
    };

    const handleUpload = async (params) => {
      const file = params.file;
      var fileKey = file.webkitRelativePath;
      const formData = new FormData();
      if (fileKey === "") {
        fileKey = file.name;
      }
      formData.append(fileKey, file);
      uploadProject(formData).then((res) => {
        state.value.fileList = [];
        proxy.$message.success(res.msg);
      });
    };

    const handleSubmit = () => {
      state.value.uploadLoading = true;
      const files = proxy.$refs.uploadProj.uploadFiles;
      const formData = new FormData();
      const fileCount = files.length;

      for (var index = 0; index < files.length; index++) {
        var fileKey = files[index].raw.webkitRelativePath;
        const file = files[index].raw;
        if (fileKey === "") {
          fileKey = file.name;
        }
        if (state.value.mode === "uploadFiles") {
          var tempKey = state.value.filePathList[index];
          if (tempKey[tempKey.length - 1] !== "/") {
            fileKey = state.value.filePathList[index] + "/" + file.name;
          } else {
            fileKey = state.value.filePathList[index] + file.name;
          }
        }
        formData.append(fileKey, file);
      }
      uploadProject(formData).then((res) => {
        state.value.fileList = [];
        if (res.msg === "success") {
          projectForm.file = fileCount;
          state.value.uploadLoading = false;
          state.value.filePathList = [];
          proxy.$message.success(res.data);
          proxy.$refs.uploadProj.clearFiles();
        }
      });
    };

    const handleUploadFile = () => {
      state.value.fileUploadVisible = true;
    };
    const handleInputCancel = () => {
      state.value.innerVisible = false;
      proxy.$refs.uploadProj.uploadFiles.splice(-1, 1);
    };

    const handleInputConfirm = () => {
      if (state.value.currentPath === "") {
        proxy.$message.warning("路径不能为空");
      } else {
        state.value.innerVisible = false;
        state.value.filePathList.splice(0, 0, state.value.currentPath);
      }
    };

    const handleAddproject = (formName) => {
      proxy.$refs[formName].validate((valid) => {
        console.log(1111);
        if (valid) {
          console.log(222);
          addProject(projectForm).then(
            (res) => {
              if (res.msg === "success") {
                proxy.$message.success(res.data);
              } else {
                proxy.$message.error(res.data);
              }
            },
            (res) => {
              proxy.$message.error(res.data);
            }
          );
        }
      });
    };

    return {
      state,
      projectForm,
      projectRules: {
        project_name: [
          { required: true, trigger: "blur", message: "input name" },
        ],
        version: [
          { required: true, trigger: "blur", message: "input version" },
        ],
        file: [
          { required: true, trigger: "blur", message: "input file count" },
        ],
      },
      handleMode,
      handleClick,
      handleBeforeUpload,
      handleRemove,
      handleChange,
      handleExceed,
      handleUpload,
      handleSubmit,
      handleInputCancel,
      handleInputConfirm,
      handleUploadFile,
      handleAddproject,
    };
  },
};
</script>
<style lang="less">
.el-dialog__header {
  padding: 30px 50px 0 50px;
  text-align: start;
}
.el-dialog__body {
  padding: 20px 50px 30px 50px;
  text-align: start;
}

.add-select {
  margin-bottom: 20px;
}

.upload-dialog {
  margin: 20px 0;
  padding-left: 150px;
  text-align: start;
}
.button-new-tag {
  margin-left: 10px;
  height: 32px;
  line-height: 30px;
  padding-top: 0;
  padding-bottom: 0;
}
.input-new-tag {
  width: 90px;
  margin-left: 10px;
  vertical-align: bottom;
}

/deep/ .el-upload-list {
  max-height: 100px;
  overflow-y: auto;
}

.upload-demo {
  text-align: start;
}
</style>