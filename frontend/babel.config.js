module.exports = {
  presets: ['@vue/cli-plugin-babel/preset'],
  plugins: [
    [
      'prismjs',
      {
        languages: ['javascript', 'css', 'markup', 'python'], //配置支持语法高亮的语言
        plugins: ['line-numbers', 'line-highlight'], //配置显示行号插件
        // "theme": "tomorrow", //全局主题
        css: true,
      },
    ],
  ],
};
