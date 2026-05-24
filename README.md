# 寰宇图鉴 · Atlas Mundi

> 中文交互式世界地图。99 个国家详尽风物志 + 792 座城市，点击国家自动缩放并显示城市分布。

## 启动步骤

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 迁移数据库并写入详情 (首次或更新数据时运行)
python seed_data.py

# 3. 抓取 99 国 Wikipedia 地标图 (联网, 首次必跑, 约 30 秒)
python fetch_wiki_images.py

# 4. 启动应用
uvicorn main:app --reload
```

打开 http://127.0.0.1:8000 即可使用。

> **若改了 data/country_wiki_targets.py 里的词条**, 重跑步骤 3 即可重新抓图.
> **若改了 templates/index.html**, uvicorn 在 --reload 模式下自动热加载, 但浏览器要 Ctrl+Shift+R 强制刷新.

## 项目结构

```
atlas-mundi/
├── main.py                              # FastAPI 应用入口
├── models.py                            # SQLAlchemy 模型
├── database.py                          # 数据库连接
├── seed_data.py                         # 国家详情种子脚本
├── fetch_wiki_images.py                 # ⭐ 抓 Wikipedia 地标图脚本 (无需安装额外依赖)
├── countries.db                         # SQLite 数据库
├── requirements.txt                     # Python 依赖
├── data/
│   ├── countries_data_eu1.py            # 欧洲 25 国 (1-25)
│   ├── countries_data_eu2.py            # 欧洲+亚洲 25 国 (26-50)
│   ├── countries_data_asia.py           # 亚洲 20 国 (51-70)
│   ├── countries_data_americas.py       # 美洲 14 国 (71-84)
│   ├── countries_data_africa_oceania.py # 非洲与大洋洲 15 国 (85-99)
│   └── country_wiki_targets.py          # ⭐ 99 国 Wikipedia 词条名映射
└── templates/
    └── index.html                       # D3.js 前端
```

## 核心功能

### 国家详情扩展 (11 类字段)
气候 · 节日 · 景点 · 历史 · 美食 · 文化 · 人口 · 面积 · 时区 · 宗教

### 城市分布可视化
点击金色国家自动缩放居中, 绘制该国 8 座主要城市;
首都用金色五角星标记, 悬停显示简介;左上角"返回全局"按钮重置视图.

### 微型国家专属标记
50m 分辨率世界地图不含梵蒂冈/摩纳哥/列支敦士登等微型国家几何, 
本应用通过专属标记层在精确经纬度位置绘制金色光环 + 国名标签,
确保 99 个国家全部可见可点击.

### Wikipedia 地标主图 + SVG 兜底
每国配该国最著名地标的 Wikipedia 词条主图:
- 法国—埃菲尔铁塔 · 中国—长城 · 日本—富士山 · 印度—泰姬陵
- 巴西—基督像 · 秘鲁—马丘比丘 · 埃及—金字塔
- 委内瑞拉—安赫尔瀑布 · 玻利维亚—乌尤尼盐沼 · 澳大利亚—悉尼歌剧院 · ……

完整 99 国词条映射见 `data/country_wiki_targets.py`.
图片加载失败时 (网络问题/被墙) 自动 fallback 到本地 SVG, 5 种主题轮换:
🏔 远山 · 🌙 星空 · 🌅 日出 · 🏙 建筑 · ✺ 图腾

### 全球国家中文化 (213 国家与地区)
即使数据库未收录的国家 (如喀麦隆/阿尔及利亚), 在地图上也显示中文名.

## API 端点
- `GET /` — 主页
- `GET /api/countries` — 全部国家列表
- `GET /api/country/{id}` — 单国详情 (含城市)
- `GET /api/country/{id}/cities` — 单国城市列表

## 修改地标图片

如果某国的地标图片不满意:
1. 打开 `data/country_wiki_targets.py`
2. 找到该国, 改成你想要的 Wikipedia 词条名 (英文, 空格用下划线)
   例如把法国从 `Eiffel_Tower` 改成 `Arc_de_Triomphe`
3. 重新运行 `python fetch_wiki_images.py`
4. 强制刷新浏览器 (Ctrl+Shift+R)

如何确定 Wikipedia 词条名: 打开维基百科找到该地标的页面, URL 末尾就是词条名.
例如 https://en.wikipedia.org/wiki/Eiffel_Tower → 词条名是 `Eiffel_Tower`.
