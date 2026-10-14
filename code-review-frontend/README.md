# 智能代码审查平台 · 前端

毕业设计前端原型，技术栈：Vue 3 + TypeScript + Vite + Tailwind CSS + Chart.js。

## 运行

```bash
npm install
npm run dev
```

浏览器打开终端提示的地址（默认 http://localhost:5173）。

## 构建 / 预览

```bash
npm run build
npm run preview
```

## 目录结构

```
src/
├─ App.vue                 # 顶层编排：输入 → 扫描 → 结果 三阶段切换
├─ style.css               # 设计变量 + 组件样式 + 动画（豆包浅色风）
├─ types.ts                # 类型定义
├─ data/
│  └─ samples.ts           # 示例代码 + 缺陷数据（JS / Python）
├─ utils/
│  └─ highlight.ts         # 手写语法高亮 + HTML 转义
└─ components/
   ├─ SideNav.vue          # 左侧边栏
   ├─ IntroCard.vue        # 系统简介卡片
   ├─ InputPanel.vue       # 三输入模式 + 配置项
   ├─ ScanPanel.vue        # 扫描动画（进度条 + 打字机 + 日志）
   ├─ ResultPanel.vue      # 结果编排
   ├─ StatCard.vue         # 统计卡片
   ├─ RiskCharts.vue       # 环形图 + 柱状图
   ├─ DefectList.vue       # 缺陷列表（展开/筛选/定位）
   └─ CodePreview.vue      # 代码预览（高亮 + 问题行 + 滚动同步）
```
