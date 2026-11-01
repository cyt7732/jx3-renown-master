<div align="center">

<img src="https://jx3.xoyo.com/p/zt/2023/10/26/index/favicon-200x200.png" alt="剑网3名望大师 Logo" width="100" style="border-radius: 20px; box-shadow: 0 8px 24px rgba(0,0,0,0.35);" />

# 剑网3名望大师

名望排班实时追踪与解阵连线求解辅助工坊

[![Online Demo](https://img.shields.io/badge/Online%20Demo-在线使用-f0c060.svg?style=flat-square)](https://cyt7732.github.io/jx3-renown-master/)
[![Release](https://img.shields.io/badge/Release-v1.2.0-emerald.svg?style=flat-square)](https://github.com/cyt7732/jx3-renown-master/releases)
[![Platform](https://img.shields.io/badge/Platform-JX3%20旗舰端%20%2F%20缘起端-38bdf8.svg?style=flat-square)](https://jx3.xoyo.com)
[![Offline Ready](https://img.shields.io/badge/Offline-100%25%20Single--File-blueviolet.svg?style=flat-square)](https://github.com/cyt7732/jx3-renown-master)

👉 **[点击直接在线使用 (GitHub Pages)](https://cyt7732.github.io/jx3-renown-master/)**

*作者：凌千羽 · 龙争虎斗*

</div>

---

# 剑网3名望大师 (`jx3-renown-master`)

实时追踪剑网3四大名望组织活动排班，并集成「解阵」智能图像识别与连线求解助手。

## 核心功能

### 1. 名望活动排班
- 实时追踪楚天社、云从社、披风会、穹野卫活动
- 统一相对偏移时间模型，彻底消除跨日错乱
- 时间范围滑块可调（30分钟 ~ 24小时），每分钟自动平滑刷新
- 支持按组织多选筛选、自定义测试时间与活动类型图标

### 2. 解阵智能求解器 (Ctrl+V 截图即解)
- 游戏内按 `Win+Shift+S` 框选解阵面板，网页中直接按 `Ctrl+V` 粘贴截图
- 纯前端本地视觉识别：自动定位 7×7 棋盘、提取格心亮点与彩色节点
- 带连通性剪枝的 Flow 算法，毫秒级规划 49 格满盘走法路线
- 在原图上高光叠加拖拽路径，提供起止坐标步骤与一键复制功能

## 追踪组织

| 组织 | 循环周期 | 地图 |
|:---|:---|:---|
| 楚天社 | 2小时 | 烂柯山 → 晟江 → 百溪 → 楚州 |
| 云从社 | 2小时 | 银霜口 |
| 披风会 | 3小时 | 河西瀚漠 |
| 穹野卫 | 3小时 | 伊丽川 |

## 使用方法

1. 将整个项目文件夹部署到 NAS / 静态服务器，或本地直接双击打开 `index.html` 即可
2. 纯静态单文件，无需任何后端或 Node 环境
3. 界面风格采用现代化国风暗色玻璃态设计系统

## 文件结构

```
jx3-renown-master/
├── index.html              # 主程序（名望排班 + 解阵求解器单文件，开箱即用）
├── solver/                 # 解阵小游戏桌面与独立工具包
│   ├── 截图即解.bat         # 双击直接读取剪贴板截图秒解
│   ├── 一键求解.bat         # 自动求解最新截图或拖拽求解
│   ├── auto_solve.py       # 图像分析与 Flow 求解核心
│   ├── clip.ps1            # 剪贴板识别处理脚本
│   ├── run.ps1             # 命令行与批处理逻辑
│   ├── sample.png          # 示例截图
│   ├── standalone.html     # 独立纯 HTML 版解阵求解器
│   └── README.md           # 独立工具使用说明
├── CHANGELOG.md            # 更新日志（详细版）
├── RELEASE.md              # 更新日志（简洁版）
├── LICENSE-FontAwesome.txt # Font Awesome Free 许可证
└── README.md               # 本文件
```

## 数据来源

- 剑网3 CMS API：`cms.jx3box.com/api/cms/game/celebrity`
- 图标来自：`img.jx3box.com/pve/minimap/`

## 技术栈

- HTML + CSS + JavaScript（纯前端原生，零框架依赖）
- Font Awesome 6.4.0（本地 `fontawesome/` 优先，缺失时自动回退 CDN）
- localStorage 缓存 + 偏好持久化

## 图标本地化

默认走 CDN，联网即可用。想让图标也离线可用：

1. 下载 Font Awesome 6.4.0 Free
2. 把 `css/` 和 `webfonts/` 两个目录放进项目根目录，命名成 `fontawesome/`
3. 最终结构是 `fontawesome/css/all.min.css` 和 `fontawesome/webfonts/*.woff2`
4. 刷新页面即可 —— 代码会自动优先用本地文件，检测不到才回退 CDN

## 许可证

- 项目代码：未指定开源协议
- 图标：Font Awesome Free 6.4.0，遵循 CC BY 4.0 / SIL OFL 1.1 / MIT，详见 `LICENSE-FontAwesome.txt`

## 版本

**v1.2.0** | 2026-11-01

### 更新记录
- 界面风格全面升级（国风暗色毛玻璃、微流光背景、Topbar 品牌系统）
- 新增「解阵」求解器：支持按 `Ctrl + V` 直接粘贴截图即刻自动识别与满盘求解
- 全量统一项目命名为 `jx3-renown-master`
- 精简历史副本，单文件便携即开即用
- 优化 Font Awesome 本地优先与 CDN 回退机制

---

© 2026 凌千羽·龙争虎斗
