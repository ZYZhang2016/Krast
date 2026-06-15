# 学习量化交易和AI编程的地方

> 感谢Algae的陪伴

## 市场宽度弱转强脚本

本仓库包含一个 Python CLI，用于从 A 股市场宽度数据中识别近期由弱转强的行业，并汇总候选行业内的股票代码。

运行源码版脚本：

```bash
python3 scripts/analyze_market_breadth.py
```

安装后也可以使用命令入口：

```bash
pip install -e .
krast-weak-to-strong
```

常用参数：

```bash
krast-weak-to-strong --max-sectors 5
krast-weak-to-strong --output json
krast-weak-to-strong --strong-threshold 55 --min-rebound 8
```

输出说明：

- `latest`：行业最新市场宽度，默认大于等于 `50` 视为进入强区。
- `recent_avg` / `comparison_avg`：近期窗口与前置比较窗口的均值。
- `recent_low` / `rebound`：近阶段低点与反弹幅度。
- 股票代码后的 `*` 表示该股票收盘价高于 MA20。

报告仅用于数据分析，不构成交易建议。
