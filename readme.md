# Mosiac Instance Reincarnation for General Enhancement of Object Detection with Domain Randomization

## 1. 概述

本仓库作为论文 *Mosiac Instance Reincarnation for General Enhancement of Object Detection with Domain Randomization* 的源码仓库。

代码按照论文所述的流程，分为 `fragmentor` 与 `reincarnator` 两部分。两部分的依赖有所不同，前者主要为 *Blender as python module* 相关模块，后者主要为 `opencv-python` 模块，可以按需求分别配置环境。

## 2. 使用方法

### 2.1 环境配置

首先进入对应代码的主目录下，也就是各自的 `main.py` 所在的文件夹当中。

使用 pip。

```shell
pip install -r requirements.txt
```

### 2.2 使用方法

检查素材路径是否正确，素材路径包括模型的 `.blend` 文件夹和背景图片的文件夹。我们建议将所有的素材存放在 `fragmentor/assets` 路径下。

在 `config.yml.template` 当中修改配置，并另存为 `config.yml`。可以注意到，配置文件模板有 *json* 版本，如果同时编辑了 *json* 和 *yaml* 会优先搜索 *yaml* 版本的。

执行 `main.py`。