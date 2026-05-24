# Atlas Mundi 项目交接文档

> 此文档给下一轮新对话的 Claude 读。用户在新对话开头会把整个项目 zip 上传 + 粘贴本文档第一段作为指令。

---

## 给新 Claude 的开场指令（用户会复制粘贴这段）

```
我有一个 FastAPI + SQLite + D3.js 的中文交互世界地图项目。当前数据库已有 165 国（含全部 54 个非洲国家），
其中 46 国配了 Unsplash 真实地标图。

图片源已切换到双源支持: Unsplash + Pexels (Pexels 是新增, Pixabay 因反爬已弃用).
两个源 CDN 直链都能直接嵌入首页, 国内访问正常.

我现在要把它扩展到「全球所有主权国家 + 南北极」(~196 条记录).

请先读 HANDOFF.md 了解项目状态、约束和接力方法,然后按下面"工作清单"开始干。
不要重新发明流程,严格按文档里的方法做。

每一轮对话能做 8-15 国(受工具调用次数限制)。这次你做完后,把更新过的
country_images.py、新国家数据文件、countries.db 打包给我,我下次再开新对话继续。

这一轮请优先: 给非洲 43 个新增国家配 Pexels 图 (本轮已切换到 Pexels 流程, 仅完成切换但未来得及配图)
```

---

## 项目结构（不要改动核心架构）

```
atlas-mundi/
├── main.py                          # FastAPI 入口,不要改
├── models.py                        # SQLAlchemy 模型,11 字段 + 8 城市,不要改 schema
├── database.py                      # DB 连接,不要改
├── countries.db                     # 数据库（这是真实数据存储,每轮都更新）
├── seed_data.py                     # 启动时写入 99 国旧数据(已不会覆盖 image_url)
├── requirements.txt
├── templates/
│   └── index.html                   # D3 地图前端,第 1150-1168 行已改为图片+SVG 兜底
├── data/
│   ├── countries_data_*.py          # 99 国旧数据(按大洲分文件)
│   ├── country_images.py            # ★ Unsplash photo ID 映射,每轮新增国家写到这里
│   └── country_wiki_targets.py      # 旧的 Wikipedia 抓图方案残留,可忽略
└── HANDOFF.md                       # 本文档
```

## 数据库 schema（不要改）

```python
Country: id, name, capital, language, currency, best_season, description, image_url,
         climate, festivals, attractions, history, cuisine, culture,
         population, area, timezone, religion
City: id, country_id, name, name_en, latitude, longitude, is_capital, description
```

每个国家配 8 个 city 是标准, 但新国允许 1-3 个城市先顶上。

---

## 当前进度快照（截至此交接时，2026-05 第四轮后）

### 已完成
- **165 国**在数据库（99 + 亚洲 23 + 非洲 43 = 全部非洲完整）
- **46 国**配了 Unsplash 图（三重元数据验证，保留不动）
- 前端"图片优先 + SVG 圆圈兜底"已实现
- **新增 Pexels 图源支持** (本轮第四轮): `country_images.py` 双源切换器，Pexels 用前缀 `pexels:1234567`，Unsplash 保持 `photo-xxxxx`
- `seed_data.py` 已可幂等运行：含 `NEW_COUNTRY_BASICS` 字典自动创建扩展国家
- `data/countries_data_extra.py` 亚洲 23 国
- `data/countries_data_africa_extra.py` 北非+东非+中非 14 国
- `data/countries_data_africa_extra_2.py` 南部非洲+岛国+西非 29 国

### 图片源决策（重要）
**已弃用** Pixabay：详情页对机器人 fetch 全部 403，无法做三步元数据验证流程。
**现行双源**：
  1. **Unsplash** (已有 46 国) — photo_id 格式 `photo-XXXXXXXX`
  2. **Pexels** (新增) — photo_id 格式 `pexels:1234567`，CDN `images.pexels.com/photos/{id}/pexels-photo-{id}.jpeg`

Pexels 验证流程（与 Unsplash 三步类似）：
```
[1] web_search "pexels.com photo <国家英文名> <地标>"
[2] 挑 URL 形如 https://www.pexels.com/photo/<slug>-<id>/  
    slug 含国家+地标关键词
[3] web_fetch 该 URL,从返回找:
    - 地理标签 (如 "Béni Abbès, Béchar Province, Algeria")
    - meta-og:image 含 images.pexels.com/photos/<id>/pexels-photo-<id>.jpeg
    - tags 含国家+地标
[4] 写入 country_images.py:
    '国名': ('pexels:<id>', '中文地标描述', '英文元数据')
```

注意：Pexels 偶发请求限流（同一会话短时间内多次 fetch 可能 403），可改用搜索结果摘要里的 tags + slug 做验证，不必每张都 fetch。

### 已确认的 46 国 photo ID 清单
（保持原状不变，见 country_images.py）

### 未完成

- **新增非洲 43 国全部需要配图**（本轮 Pexels 流程已就绪但未来得及配，留给下轮）
  - 阿尔及利亚已部分验证 (`pexels:2092453`, Béni Abbès Sahara) — 可直接用
  - 突尼斯已部分验证 (`pexels:27599624`, Sidi Bou Said) — 可直接用
- 165 国中 119 国还没配图
- 全球还有 **~31 个国家不在数据库**（美洲 21 + 大洋洲 10 + 南北极 2）

---

## ★★★ 严格遵守的工作流程 ★★★

### 1. 添加新国家(基本信息)

只填**核心字段**, 不要硬凑 11 字段全填:

```python
NEW_COUNTRY = {
    'name': '中文名',      # 例:越南
    'name_en': 'Vietnam',
    'capital': '河内',
    'language': '越南语',
    'currency': '越南盾',
    'description': '一两句话简介。',
    'population': '9700万',
    'area': '33.1万 km²',
    'timezone': 'UTC+7',
    'religion': '佛教/无宗教',
    'best_season': '10月-4月',
    # climate/festivals/attractions/history/cuisine/culture 留空, 让前端有兜底
}
```

写入数据库示例代码(每次扩展国家时用):
```python
import sqlite3
conn = sqlite3.connect('countries.db')
cur = conn.cursor()
cur.execute('''
    INSERT INTO countries (name, capital, language, currency, description, population, area, timezone, religion, best_season)
    VALUES (?,?,?,?,?,?,?,?,?,?)
''', (...))
conn.commit()
```

### 2. 给国家配 Unsplash 图片(关键流程, 不要偷工)

**步骤(每国都要做完整 3 步)**:

```
[1] web_search "unsplash <地标英文名> <国家英文名>"
[2] 从搜索结果里挑一条 URL 形如 https://unsplash.com/photos/xxxxx-XXXXXXXXX
    选标题/描述含明确地标关键词的(不要选 interior/inside 这种室内图)
[3] web_fetch 那个 URL,从返回内容里找:
    - <map marker> 地点标签(必须含国家名/地标名)
    - meta-og:image 中的 photo-XXXXXXXXXXXXX 数字串(这就是 photo ID)
    - tags 里要含地标关键词
[4] 三重验证通过后,写入 country_images.py:
    '国名': ('photo-XXXXXXXXX', '中文地标描述', '英文位置元数据')
```

**禁止事项**:
- ❌ 凭记忆猜 photo ID(之前犯过的错,导致张冠李戴)
- ❌ 用 source.unsplash.com 关键词 URL(已停服)
- ❌ 跳过 web_fetch 直接信任搜索结果摘要(可能挑到错图)
- ❌ 用 Wikipedia API 或要用户本地跑脚本(用户在中国大陆环境)

**URL 模板**(横屏 1600x600 CDN 裁切):
```
https://images.unsplash.com/{photo_id}?auto=format&fit=crop&crop=entropy&w=1600&h=600&q=80
```

### 3. 南北极的特殊处理

南极/北极不是国家, 但用户要求包含。建议:
- 作为"特殊区域"加进 countries 表
- name='南极洲'/'北极地区', capital='-'(或'昭和站/麦克默多站'等科考站)
- 经纬度可以放 (-82, 0) 和 (85, 0)
- 写一张冰原/极光的 Unsplash 图

### 4. 上下文管理(每轮的硬约束)

- 每个 web_fetch 返回 ~4-5KB 文本, 累积到 ~40 次 fetch 时上下文会接近极限
- 实际安全推进速度: **每轮 10-15 国**
- 做完 10-15 国后立刻打包给用户, 不要硬冲
- 打包给用户时, 把更新过的 `country_images.py` 和新建的 `data/countries_extra.py` 一并放进 zip

### 5. 全球主权国家清单(参考, ~196 个)

按地理分组, 已在数据库的标 ✓:

#### 欧洲(45) — 已配图标 ✓✓, 在库未配图标 ✓✗
✓✓ 法国 ✓✓ 德国 ✓✓ 英国 ✓✓ 西班牙 ✓✓ 葡萄牙 ✓✓ 意大利 ✓✓ 荷兰 ✓✓ 瑞士 ✓✓ 希腊 ✓✓ 俄罗斯
✓✓ 比利时 ✓✗ 奥地利 ✓✗ 瑞典 ✓✗ 挪威 ✓✗ 丹麦 ✓✗ 芬兰 ✓✗ 冰岛 ✓✗ 爱尔兰 ✓✗ 波兰 ✓✗ 捷克
✓✗ 匈牙利 ✓✗ 罗马尼亚 ✓✗ 保加利亚 ✓✗ 克罗地亚 ✓✗ 斯洛文尼亚 ✓✗ 斯洛伐克 ✓✗ 乌克兰 ✓✗ 白俄罗斯
✓✗ 立陶宛 ✓✗ 拉脱维亚 ✓✗ 爱沙尼亚 ✓✗ 塞尔维亚 ✓✗ 黑山 ✓✗ 波斯尼亚和黑塞哥维那 ✓✗ 阿尔巴尼亚
✓✗ 北马其顿 ✓✗ 科索沃 ✓✗ 摩尔多瓦 ✓✗ 卢森堡 ✓✗ 列支敦士登 ✓✗ 摩纳哥 ✓✗ 安道尔 ✓✗ 圣马力诺
✓✗ 梵蒂冈 ✓✗ 马耳他 ✓✗ 塞浦路斯

#### 亚洲(48) — 已配图标 ✓✓, 在库未配图标 ✓✗, 不在库标 ✗
✓✓ 中国 ✓✓ 日本 ✓✓ 韩国 ✓✓ 印度 ✓✓ 印度尼西亚 ✓✓ 越南 ✓✓ 泰国 ✓✓ 柬埔寨 ✓✓ 老挝 ✓✓ 缅甸
✓✓ 马来西亚 ✓✓ 新加坡 ✓✓ 菲律宾 ✓✗ 蒙古 ✓✓ 尼泊尔 ✓✓ 斯里兰卡 ✓✓ 哈萨克斯坦
✓✓ 阿联酋 ✓✓ 沙特阿拉伯 ✓✓ 以色列 ✓✓ 土耳其 ✓✗ 格鲁吉亚 ✓✗ 亚美尼亚 ✓✗ 阿塞拜疆
✓✓ 巴基斯坦 ✓✓ 伊朗 ✓✓ 黎巴嫩 ✓✓ 约旦 ✓✓ 卡塔尔 ✓✓ 阿曼 ✓✓ 不丹 ✓✓ 孟加拉国 ✓✓ 马尔代夫 ✓✓ 乌兹别克斯坦
✓✗ 朝鲜 ✓✗ 阿富汗 ✓✗ 伊拉克 ✓✗ 叙利亚 ✓✗ 巴勒斯坦 ✓✗ 巴林 ✓✗ 科威特 ✓✗ 也门
✓✗ 文莱 ✓✗ 东帝汶 ✓✗ 吉尔吉斯斯坦 ✓✗ 塔吉克斯坦 ✓✗ 土库曼斯坦

#### 美洲(35)
✓ 美国 ✓ 加拿大 ✓ 墨西哥 ✓ 巴西 ✓ 阿根廷 ✓ 智利 ✓ 秘鲁 ✓ 哥伦比亚 ✓ 委内瑞拉
✓ 厄瓜多尔 ✓ 玻利维亚 ✓ 巴拉圭 ✓ 乌拉圭 ✓ 古巴
✗ 危地马拉 ✗ 洪都拉斯 ✗ 萨尔瓦多 ✗ 尼加拉瓜 ✗ 哥斯达黎加 ✗ 巴拿马 ✗ 伯利兹
✗ 海地 ✗ 多米尼加 ✗ 牙买加 ✗ 巴哈马 ✗ 巴巴多斯 ✗ 特立尼达和多巴哥 ✗ 圣卢西亚
✗ 圣文森特和格林纳丁斯 ✗ 格林纳达 ✗ 安提瓜和巴布达 ✗ 圣基茨和尼维斯 ✗ 多米尼克
✗ 苏里南 ✗ 圭亚那

#### 非洲(54) — 已配图标 ✓✓, 在库未配图标 ✓✗（本轮全部 54 国均在库）
✓✓ 埃及 ✓✓ 摩洛哥 ✓✗ 南非 ✓✗ 肯尼亚 ✓✗ 坦桑尼亚 ✓✗ 埃塞俄比亚 ✓✗ 加纳 ✓✗ 尼日利亚
✓✗ 马达加斯加 ✓✗ 津巴布韦 ✓✗ 卢旺达
✓✗ 阿尔及利亚 ✓✗ 突尼斯 ✓✗ 利比亚 ✓✗ 苏丹 ✓✗ 南苏丹 ✓✗ 厄立特里亚 ✓✗ 吉布提 ✓✗ 索马里
✓✗ 乌干达 ✓✗ 布隆迪 ✓✗ 刚果民主共和国 ✓✗ 刚果共和国 ✓✗ 中非 ✓✗ 喀麦隆 ✓✗ 加蓬 ✓✗ 赤道几内亚
✓✗ 圣多美和普林西比 ✓✗ 安哥拉 ✓✗ 赞比亚 ✓✗ 马拉维 ✓✗ 莫桑比克 ✓✗ 博茨瓦纳 ✓✗ 纳米比亚
✓✗ 莱索托 ✓✗ 斯威士兰 ✓✗ 科摩罗 ✓✗ 毛里求斯 ✓✗ 塞舌尔 ✓✗ 佛得角 ✓✗ 几内亚比绍
✓✗ 几内亚 ✓✗ 塞拉利昂 ✓✗ 利比里亚 ✓✗ 科特迪瓦 ✓✗ 多哥 ✓✗ 贝宁 ✓✗ 布基纳法索 ✓✗ 马里
✓✗ 尼日尔 ✓✗ 乍得 ✓✗ 毛里塔尼亚 ✓✗ 塞内加尔 ✓✗ 冈比亚

#### 大洋洲(14)
✓ 澳大利亚 ✓ 新西兰 ✓ 巴布亚新几内亚 ✓ 斐济
✗ 萨摩亚 ✗ 汤加 ✗ 瓦努阿图 ✗ 所罗门群岛 ✗ 基里巴斯 ✗ 图瓦卢 ✗ 瑙鲁
✗ 马绍尔群岛 ✗ 密克罗尼西亚联邦 ✗ 帕劳

#### 特殊区域(2)
✗ 南极洲 ✗ 北极地区(可作为格陵兰/挪威/俄罗斯北部的归属说明,不重复)

#### 总计
- 已在数据库: **165 国** (含全部 54 个非洲国家)
- 待添加: **~31 国 + 2 极地区域** (美洲 21 + 大洋洲 10 + 南北极)
- 总目标: ~196 条记录

---

## ★ 给下一轮新 Claude 的"工作清单"（按优先级）★

**第 N 轮对话的标准动作**:

1. 读 HANDOFF.md(本文档)
2. 读 `data/country_images.py` 确认当前进度
3. `sqlite3 countries.db` 看现存国家清单
4. 挑 10-15 个**未完成的国家**(按上面的 ✗ 清单)
5. 对每国: 添加基本信息(SQL INSERT) + 配 Unsplash 图(走 3 步流程)
6. 把更新过的文件打包到 `/mnt/user-data/outputs/atlas-mundi.zip`
7. 用 `present_files` 给用户

**这一轮重点做的批次建议**:
- 下一轮（第 5 轮）: 用 Pexels 流程给非洲新增 43 国配图（已有 2 国候选 photo_id 可直接用）
- 第 6 轮: 添加美洲剩余 21 国 + 配图（混用 Pexels + Unsplash）
- 第 7 轮: 添加大洋洲 10 国 + 南北极 + 配图

每轮做完, 用户拿 zip 重启 uvicorn 就能看到新增。

---

## 上一轮 Claude 留下的经验 (2026-05 第四轮)

**图片源决策（重大变更）**:
- 用户曾要求换 Pixabay，但 Pixabay 对机器人 fetch **全部返回 403**，无法做三步元数据验证
- 转向 **Pexels**，验证通过：fetch 不被拦截、CDN 直链可嵌入、含完整地理元数据、国内访问正常
- `country_images.py` 已升级为双源 `get_image_url`，按前缀判断：
  - `pexels:1234567` → `images.pexels.com/photos/.../pexels-photo-...jpeg`
  - `photo-xxxxx`    → `images.unsplash.com/photo-xxxxx`
- 前端 `templates/index.html` `isDirectImage` 判断已含 `images.pexels.com`

**Pexels 流程实操**:
- 单次 search 摘要里就含 tags（数十个英文关键词）+ 位置 + 描述，可直接验证不需 fetch
- Pexels 偶发限流：同会话短时间多次 fetch 同 URL 可能 403，间隔几秒重试或换搜索摘要验证
- URL 模板已固定写在 country_images.py 里，每国只需记 `pexels:<id>` 7 位数字 ID

**Pexels 题材覆盖不均**:
- Algeria、Tunisia、Morocco、South Africa 等热门地丰富（Algeria 有 6K+ 张）
- 但 Libya、Eritrea、Equatorial Guinea 等冷门国家可能 Pexels 没合适内容
- **回退策略**：Pexels 找不到的国家用 Unsplash（双源支持的好处）
- Unsplash 题材广度更全，Pexels 题材深度更好

**非洲 43 国数据已完整入库**:
- `data/countries_data_africa_extra.py` (14 国: 北非5+东非3+中部6) 
- `data/countries_data_africa_extra_2.py` (29 国: 南部13+岛国4+西非12)
- seed_data.py `NEW_COUNTRY_BASICS` 字典已含全部 43 国基础字段
- 重启 `python3 seed_data.py` 可从空库恢复

**第四轮跳过未做的 (留给下轮)**:
- **关键**: 非洲 43 国 Pexels 配图（仅完成 2 个候选: Algeria pexels:2092453 / Tunisia pexels:27599624）
- 第二轮老遗留: 蒙古、阿塞拜疆、亚美尼亚、格鲁吉亚 (亚洲); 欧洲剩 33 国; 美洲老 11 国
- 美洲剩余 21 国 + 大洋洲剩余 10 国 + 南北极

---

## 不变的约束

1. 用户**不愿本地跑脚本**, 要纯打包成品
2. 用户在中国大陆类似网络环境(Unsplash 可访问, Wikipedia 不稳)
3. 图片必须横构图(195px 高 hero 区, 竖图被裁出问题)
4. 写 Python 字符串嵌入中文时, 用单引号包裹避免英文引号冲突
5. seed_data.py 已修改: 重启时不会清空 image_url 字段
6. **新国家添加后, 不要在 seed_data.py 里也写一份**, 直接 SQL INSERT 到 countries.db
7. Claude 沙盒里无外网访问 pip, 但 web_search / web_fetch 可用

---

## 故障排查

**如果用户说某张图错了/不喜欢**:
- 不要重新搜该国, 直接问用户要哪种风格的备选
- 重新走 3 步流程 fetch 验证

**如果数据库里 image_url 字段被清空**:
- 检查 seed_data.py 是不是回退了
- 用 `python3 -c "from data.country_images import COUNTRY_IMAGES, get_image_url; ..."` 重新批量 UPDATE

**如果前端不显示新国家**:
- 检查浏览器强制刷新(Cmd/Ctrl+Shift+R)
- 检查 main.py 的路由是否返回所有国家
- 检查 D3 地图渲染是否按 country.name 中文匹配

---

## 上一轮 Claude 留下的经验 (2026-05 第二批)

**有些 URL 直接 fetch 会 403, 但搜索结果摘要里已经包含完整三重元数据**:
- 搜索结果里如果同时出现 map marker + tags + 国家英文名匹配, 可以直接 fetch 同一个 photo 详情页提取 photo ID
- 如果 fetch 403, 换一张图或重新搜索, 不要为了一张图死磕
- 实际发现 unsplash URL 里如果带有完整 slug (e.g. `cars-drive-near-the-kingdom-tower-in-riyadh-XXXXX`) 通常 fetch 成功率高
- 如果 URL 只有 photo ID (e.g. `/photos/Z26QvyTYrrs`) 容易 403, 换一张候选

**Unsplash+ (premium) 图片不能用**:
- 若 `meta-og:image` URL 是 `plus.unsplash.com/premium_photo-XXX` 而不是 `images.unsplash.com/photo-XXX`, 这是付费图, 跳过
- 搜索结果摘要里如果出现 "For Unsplash+" 或 "Licensed under the Unsplash+ License", 这是付费图, 不选

**蒙古的特殊情况**:
- 蒙古地标(成吉思汗雕像)在 Unsplash 上几乎没有
- 当地标搜不到时, 改搜国家典型场景(草原+ger/蒙古包)
- 但本轮蒙古所有候选都 403, 已跳过, 留给下轮处理

**第二轮跳过未做的 (历史记录)**:
- 当时蒙古候选 URL 全部 403，留下了，本轮未处理
- 当时也未处理：阿塞拜疆、亚美尼亚、格鲁吉亚（亚洲）；欧洲剩余 33 国；美洲剩余 11 国；非洲剩余 10 国；大洋洲剩余 3 国

---

文档结束。新 Claude 看完这个就能干活了。祝顺利。
