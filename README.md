# Eagle Eye Stitcher 🦅

**鹰眼图像拼接器** — 基于图割和局部梯度融合的多图顺序拼接引擎。

## 功能特点

- **多图顺序拼接**：支持任意数量图像按顺序逐一拼接
- **GraphCut 最优接缝**：综合颜色差异、显著性、物体边缘等维度，自动计算最小视觉代价的接缝线
- **局部泊松融合**：在接缝区域进行梯度域融合，消除拼接痕迹
- **羽化平滑**：高斯羽化过渡，进一步柔化边界
- **缝合线可视化**：支持在拼接结果上叠加红色缝合线标注，便于调试和分析
- **双模式选择**：`normal` 快速模式 / `professional` 精准模式
- **GUI + CLI**：图形界面与命令行双入口

## 算法流程

对每两张图像之间的拼接，执行以下 7 个阶段：

| 阶段 | 算法 | 说明 |
|------|------|------|
| 1 | MBS 显著性 + Canny 边缘 | 提取显著区域和图像边缘 |
| 2 | SIFT + RANSAC | 特征点匹配，计算单应性变换矩阵 |
| 3 | 透视变换对齐 | 将待拼接图变换到基准图坐标系 |
| 4 | GraphCut 图割 | 在重叠区域寻找最优接缝线 |
| 5 | 硬合成 | 按图割标签选取像素 |
| 6 | 局部泊松融合 | 梯度域无缝融合 |
| 7 | 高斯羽化 | 平滑过渡 |

## 安装

```bash
pip install -r requirements.txt
```

依赖：`opencv-python`、`numpy`、`Pillow`、`scipy`、`maxflow`

## 使用

### 图形界面

```bash
python app.py
```

控制面板（左）— 选择图像 → 调节参数 → 开始拼接 → 查看结果

拼接完成后可勾选 **"显示缝合线"** 查看红色标注的接缝位置。

### 命令行

```bash
python scripts/demo_cli.py img1.jpg img2.jpg img3.jpg -o result.png
python scripts/demo_cli.py img1.jpg img2.jpg --seam-band 15 --feather-radius 20
python scripts/demo_cli.py img1.jpg img2.jpg --show-seam -o result.png
```

| 参数 | 说明 |
|------|------|
| `-o` / `--output` | 输出路径（默认 ./outputs/result.png） |
| `--seam-band` | 融合带宽（默认 9） |
| `--feather-radius` | 羽化半径（默认 11） |
| `--show-seam` | 额外输出缝合线标注图 |
| `-v` / `--verbose` | 详细日志输出 |

## 项目结构

```
├── app.py                    # GUI 启动入口
├── stitcher/                 # 核心代码
│   ├── algorithms/           # 算法模块
│   │   ├── saliency_mbs.py          # MBS 显著性检测
│   │   ├── edge_detection.py        # Canny 边缘检测
│   │   ├── feature_registration.py  # SIFT 特征匹配 + RANSAC
│   │   ├── homography_alignment.py   # 透视变换对齐
│   │   ├── overlap_masks.py         # 重叠区域计算
│   │   ├── seam_graphcut.py         # GraphCut 接缝选择
│   │   ├── hist_otsu.py             # OTSU 阈值分割
│   │   └── local_poisson_blend.py   # 局部泊松融合
│   ├── pipeline/             # 拼接流水线编排
│   │   └── stitching_pipeline.py
│   ├── ui/                   # Tkinter 图形界面
│   │   └── main_window.py
│   ├── workers/              # 多进程后台执行
│   │   └── stitching_worker.py
│   ├── common/               # 公共工具
│   │   ├── logger.py
│   │   ├── exceptions.py
│   │   └── image_utils.py
│   ├── config/               # 配置参数
│   │   └── settings.py
│   └── io/                   # 图像读写（支持中文路径）
│       └── image_io.py
├── scripts/
│   └── demo_cli.py           # 命令行工具
└── legacy/                   # 旧版代码（重构前参考）
```

## 设计

- **模块化架构**：算法层、管线层、界面层、Worker 层职责分离
- **多进程拼接**：GUI 将拼接任务派发到独立子进程，界面不卡顿
- **双区配色**：左侧控制面板鹰羽白 + 右侧画布深夜蓝 + 金色分隔与装饰

## 许可

MIT License
