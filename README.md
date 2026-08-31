# 基于关键词的推特（Twitter/X）热搜抓取系统

> 面向**境外社交平台**的关键词定向数据采集工具，支撑跨境舆情 / 国际传播研究；配置本地保存、不含账号凭据。

![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python&logoColor=white)
![Stack](https://img.shields.io/badge/Stack-Scweet%20%2B%20Excel-green)
![Privacy](https://img.shields.io/badge/Privacy-%E6%9C%AC%E5%9C%B0%E9%85%8D%E7%BD%AE-success)

---

## 📌 项目简介

用 Scweet 框架按关键词在 Twitter/X 上定向采集热搜与推文，结果导出 Excel，用于**跨境舆情 / 涉外舆情风险研判**。检索词完全由你本地配置，仓库不含任何账号或凭据。

## ✨ 核心亮点

- **关键词驱动**：在 `keywords.txt` 配置目标关键词，批量定向抓取。
- **跨境采集**：面向 Twitter/X 的公开数据，支撑国际传播与境外平台信息搜集。
- **结果可分析**：抓取结果导出 `xlsx`，便于后续清洗、去重与统计。

## 🚀 快速开始

```bash
pip install scweet openpyxl

# 编辑 keywords.txt 填入关键词
python scweet_bot.py
```

- 抓取结果见 `推文结果.xlsx`。

## 📂 目录结构

```
基于关键词的推特热搜抓取系统/
├── scweet_bot.py      # 抓取主程序
├── keywords.txt       # 关键词配置（自行填写）
└── 推文结果.xlsx       # 抓取结果（本地生成）
```

## 🔒 隐私与安全

- 不含任何账号凭据；`keywords.txt` 仅含你的检索词，可放心随仓库分发。
- 抓取为公开数据检索，不进行登录态凭据存储。
