---
name: portfolio-tracker
description: 查询股票持仓市值并计算各股票占比。当用户询问"查市值"、"股票市值"、"portfolio"、"持仓情况"等时触发。自动读取 portfolio.md 中的持仓数据，调用 portfolio_tracker.py 脚本获取实时股价，返回包含每只股票的市值、涨跌、以及持仓占比的完整报告。
---

# Portfolio Tracker - 股票持仓市值查询

## 使用方法

当用户询问股票市值时：

1. **读取持仓配置**: 从 `~/portfolio.md` 读取持仓数据
2. **运行查询脚本**: 执行 `python3 ~/.openclaw/skills/portfolio-tracker/scripts/portfolio_tracker.py`
3. **返回格式化结果**: 将脚本输出整理成易读的表格形式

## 输出格式

回复应包含：
- 每只股票：代码、股价、持股数、市值、涨跌、占比
- 现金金额及占比
- 总资产

## 示例

用户问："查下市值"

回复格式：
```
📊 你的持仓市值（YYYY-MM-DD）：

| 股票 | 股价 | 持股 | 市值 | 涨跌 | 占股票 | 占总资产 |
|------|------|------|------|------|--------|----------|
| TSLA | $xxx | xx | $xxx | 📈/📉 x% | x% | x% |
...

- 股票总市值: $xxx
- 现金: $xxx (x%)
- 总资产: $xxx
```

## 脚本位置

`~/.openclaw/skills/portfolio-tracker/scripts/portfolio_tracker.py`

## 持仓数据位置

`~/portfolio.md`
