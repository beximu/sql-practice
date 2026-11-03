# SQL 练习集 · 海洋经济省级面板 20 题

用**自己参与的大创项目数据**练 SQL，而不是刷完 LeetCode 就扔。

20 道题全部来自真实业务问题：给领导看排名、筛掉数据覆盖不足的省、把长表转成宽表、算加权研发强度。每题一个 `.sql` 文件，文件头写清「业务场景 → 考点 → 预期结果 → 思路」。

---

## 为什么用这批数据练

大部分人的 SQL 练习集是 LeetCode 截图，数据是 `employee` 和 `orders` 这种假表。问题是：**假表不会给你 NULL，不会给你缺列，不会给你两张表关联不上。**

这批数据会。它是我在学校大创项目里整理的沿海 11 省宏观面板，原始数据来自各省统计年鉴和统计公报。真实数据该有的毛病它都有：

- 海洋生产总值 110 个观测里只有 85 个有值（77.3%），剩下 25 个查不到
- 海洋三次产业增加值更惨，110 行里只有 9 行有值（8.2%）
- 进出口数据只有 2022–2023 两年，其它年份是空的
- 原始 CSV 里 `R&D经费内部支出` 这种列名带 `&`，不处理的话每次写 SQL 都得加引号

**在这些数据上写出来的 SQL，和在生产环境写出来的 SQL 是同一类东西。**

---

## 数据长什么样

8 张表，全部在 `data/raw/` 下：

| 表名 | 行 × 列 | 粒度 | 说明 |
|---|---|---|---|
| `panel_hqd` | 110 × 39 | 省 × 年 | 主分析表，11 个沿海省 × 2015–2024 |
| `macro` | 550 × 8 | 省 × 年 × 指标 | 长表：GDP、三次产业、人口 |
| `gop` | 440 × 8 | 省 × 年 × 指标 | 长表：海洋生产总值及三次产业 |
| `gop_supplement` | 15 × 8 | 省 × 年 × 指标 | `gop` 的人工补丁表 |
| `tech` | 440 × 8 | 省 × 年 × 指标 | 长表：R&D 投入与专利 4 个指标 |
| `trade` | 22 × 8 | 省 × 年 × 指标 | 长表：货物进出口总额（仅 2022–2023） |
| `panel_city` | 18 × — | 市 × 年 | 辽宁 6 市 × 2020–2022，估算值 |
| `gdp_prov` | 55 × 7 | 省 × 年 | 省级 GDP 与人均 GDP（2020–2024） |

**`panel_hqd` 是宽表**（一行 = 一个省一年，所有指标铺开），**`macro` / `gop` / `tech` / `trade` 是长表**（一行 = 一个省一年的一个指标）。第 13 题就是练这个长转宽。

---

## 20 题

| # | 业务问题 | 考点 | 结果 | 文件 |
|---|---|---|---|---|
| 1 | 2024 年各省 GDP 排行 | WHERE + ORDER BY | 11 × 2 | [`q01`](01_basic_filter/q01_gdp_ranking_2024.sql) |
| 2 | 辽宁十年人均 GDP 走势 | 字符串筛选 + 时序排序 | 10 × 2 | [`q02`](01_basic_filter/q02_liaoning_gdp_per_capita.sql) |
| 3 | 2024 年 GDP 超 5 万亿的省 | 多条件 AND + 单位换算 | 6 × 2 | [`q03`](01_basic_filter/q03_provinces_above_5t.sql) |
| 4 | 2024 年人均 GDP 前三 | TOP N：ORDER BY + LIMIT | 3 × 2 | [`q04`](01_basic_filter/q04_top3_gdp_per_capita.sql) |
| 5 | 找出海洋生产总值缺失的行 | IS NULL | 25 × 2 | [`q05`](01_basic_filter/q05_missing_gop_rows.sql) |
| 6 | 每个区域有几个省 | COUNT(DISTINCT) | 3 × 2 | [`q06`](02_aggregation/q06_provinces_per_region.sql) |
| 7 | 各省十年平均 GDP | GROUP BY + AVG | 11 × 2 | [`q07`](02_aggregation/q07_avg_gdp_by_province.sql) |
| 8 | 11 省 GDP 年度合计 | GROUP BY + SUM | 10 × 2 | [`q08`](02_aggregation/q08_annual_gdp_total.sql) |
| 9 | 海洋数据覆盖 ≥ 8 年的省 | COUNT(列) + HAVING | 6 × 2 | [`q09`](02_aggregation/q09_gop_coverage.sql) |
| 10 | 各省 R&D 强度波动幅度 | MAX / MIN 与四则运算 | 11 × 4 | [`q10`](02_aggregation/q10_rd_intensity_range.sql) |
| 11 | 区域 GDP 合计（跨表） | 两表 JOIN，双键关联 | 3 × 2 | [`q11`](03_join/q11_region_gdp_join.sql) |
| 12 | 两张来源表合并后各省记录数 | UNION ALL + 子查询 | 11 × 2 | [`q12`](03_join/q12_union_gop_sources.sql) |
| 13 | 长表转宽表：R&D 四项指标 | CASE WHEN 条件聚合 | 110 × 6 | [`q13`](03_join/q13_pivot_rd_indicators.sql) |
| 14 | 外贸依存度 | JOIN 后做除法，构造派生指标 | 11 × 4 | [`q14`](03_join/q14_trade_dependency.sql) |
| 15 | 2024 年 GDP 排名 | RANK() | 11 × 3 | [`q15`](04_window_functions/q15_rank_gdp.sql) |
| 16 | 各省 GDP 同比增速 | LAG() | 99 × 3 | [`q16`](04_window_functions/q16_yoy_growth.sql) |
| 17 | 每个区域 GDP 最高的省 | ROW_NUMBER() + PARTITION BY | 3 × 3 | [`q17`](04_window_functions/q17_top_per_region.sql) |
| 18 | 海洋占比高于平均的省 | CTE + 子查询比较平均值 | 4 × 2 | [`q18`](05_advanced/q18_above_avg_ocean_share.sql) |
| 19 | 2024 增速 vs 本省十年均值 | 窗口函数 + 聚合 JOIN | 11 × 3 | [`q19`](05_advanced/q19_growth_vs_own_avg.sql) |
| 20 | 区域加权 R&D 投入强度 | 加权平均：Σ分子 / Σ分母 | 3 × 2 | [`q20`](05_advanced/q20_weighted_rd_intensity.sql) |

---

## 怎么跑

需要一个 Python 环境（3.9+）和 `pandas`、`duckdb`：

```bash
pip install pandas duckdb
```

**第一步：建库**

```bash
cd setup
python 01_build_db.py
```

会在 `sql-practice/` 下生成 `haiyang.duckdb`（库文件不进 git，需要自己生成）。

**第二步：跑某一题**

```bash
python -c "
import duckdb
con = duckdb.connect('haiyang.duckdb', read_only=True)
print(con.execute(open('04_window_functions/q16_yoy_growth.sql').read()).df())
"
```

**或者一把梭跑全部 20 题**，确认每题的返回行数：

```bash
cd setup
python 02_run_all.py
```

预期末尾输出 `全部 20 题通过`，中间每行形如：

```
q16_yoy_growth.sql                   99    3  OK
```

---

## 6 个真踩过的坑

这些不是从教程里抄的，是写完 20 题之后回头整理出来的。

### 1. `= NULL` 永远查不出东西，而且不报错

```sql
-- 错：返回 0 行，不报错，最容易被忽略
WHERE 海洋生产总值_亿元 = NULL

-- 对
WHERE 海洋生产总值_亿元 IS NULL
```

因为 SQL 里 `NULL = NULL` 的结果是 `UNKNOWN` 而不是 `TRUE`。这条规则在「缺失值排查」这种日常操作里天天遇到。

### 2. `COUNT(*)` / `COUNT(列)` / `COUNT(DISTINCT 列)` 是三个东西

第 6 题和第 9 题专门考这个。数据里一个省有 10 行（10 年）：

| 写法 | 含义 | 一省的结果 |
|---|---|---|
| `COUNT(*)` | 数行数，NULL 也算 | 10 |
| `COUNT(海洋生产总值_亿元)` | 数该列非空个数 | 8（有 2 年缺失） |
| `COUNT(DISTINCT 省份)` | 数去重后的非空个数 | 1 |

我在第 6 题第一次写成了 `COUNT(*)`，得到 40 而不是 4 —— 一个区 4 个省 × 10 年。

### 3. WHERE 里用不了 SELECT 起的别名

```sql
-- 错：报错 Binder Error: 别名 GDP合计 不存在
SELECT 区域, SUM(数值) AS GDP合计
FROM macro
WHERE GDP合计 > 100000

-- 对：WHERE 阶段这个别名还没算出来
SELECT 区域, SUM(数值) AS GDP合计
FROM macro
GROUP BY 区域
HAVING SUM(数值) > 100000
```

根因是执行顺序：`FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY → LIMIT`。**SELECT 排在 WHERE 后面**，所以 WHERE 看不到别名。想通了这一条，`WHERE` 和 `HAVING` 的区别就不用背了。

### 4. `>=` 和 `>` 结果一样，不代表逻辑对

第 3 题题目要求「GDP 超 5 万亿」，我写的是 `>= 50000`。跑出来 6 行，和答案一样，判分通过。

看起来没问题，实际上——**这批数据里恰好没有 GDP 正好等于 50000 的省**，所以两种写法结果相同。换成别的年份、别的阈值，就会多出一个边界行。

「结果相符」和「逻辑正确」是两件事。**判分器只能验证前者，后者要自己盯。**

### 5. 漏写 ORDER BY，判分照样能过

第 5、9、17 题我都漏了排序，或者写反了方向（题目要降序，我写了默认升序）。

我的判分函数是先排序再逐格比对，所以顺序错误不会报错。但真实的业务场景里，**一张没排序的结果表交给业务方等于没做完** —— 他要的「Top 3 是谁」和「Bottom 3 是谁」，数据一模一样，顺序全反。

### 6. 窗口函数写两遍，等于自己给自己挖坑

第 19 题第一版我这么写的：

```sql
-- 又长又容易改漏
select 省份, 年份,
       (GDP - lag(GDP) over w) / lag(GDP) over w * 100
from panel_hqd
window w as (partition by 省份 order by 年份)
```

`lag()` 出现两次，改一处忘另一处就静默算错。后来改成子查询先把 `lag` 算成一列：

```sql
select 省份, 年份,
       round((GDP_亿元 - last_gdp) / last_gdp * 100, 2) as 增速
from (
    select 省份, 年份, GDP_亿元,
           lag(GDP_亿元, 1) over (partition by 省份 order by 年份) as last_gdp
    from panel_hqd
) t
```

**原则：同一个窗口函数只用写一次。** 需要复用就套子查询或 CTE。

---

## 还可以往下做

- [ ] 补 LeetCode SQL 的 Medium 题，重点在窗口函数和自连接
- [ ] 把这 20 题改写成 pandas 版本，对比 SQL 和 DataFrame 的思维差异
- [ ] 在 `panel_hqd` 上做留存/同期群分析，练「累计口径 vs 精确第 N 天」

---

## 数据说明

数据整理自各省统计年鉴、统计公报及公开数据库，为**省级宏观统计数据**，不含任何个人信息。原始 CSV 在 `data/raw/` 下，字段含义见各表列名。

其中海洋三次产业增加值缺失严重（110 行仅 9 行有值），因此本数据集**只适合做总量层面的描述性分析，不适合做产业结构回归**。这一点在做任何分析前都应该先确认。
