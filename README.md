## 知乎热榜爬虫（Python）

一个简单脚本：抓取知乎热榜并在终端打印，或保存为 JSON。

### 安装依赖

无需安装第三方依赖（仅用 Python 标准库）。

### 用法

```bash
# 默认抓取 20 条并打印
python zhihu_hot.py

# 抓取 50 条并保存到文件
python zhihu_hot.py --limit 50 --output zhihu_hot.json
```

### 输出字段

- `rank`: 排名
- `title`: 标题
- `excerpt`: 摘要
- `url`: 问题链接
- `heat`: 热度文案
