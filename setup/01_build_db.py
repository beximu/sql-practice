# -*- coding: utf-8 -*-
"""
01_build_db.py —— 把 data/raw/ 里的 8 个 CSV 建成一个 DuckDB 数据库。

为什么不用 DuckDB 的 read_csv 直接读：
    DuckDB 的 read_csv 对 gop.csv / tech.csv 会自动整行读成一列
    （分隔符识别失败），所以统一用 pandas 读进来再写入 DuckDB。

为什么 tech.csv 要特殊处理：
    tech.csv 里有一条记录的「备注」字段带半角逗号，把 8 列撑成 9 列。
    不修的话 pandas 直接抛错，或者更糟 —— 静默丢掉整行。

运行：
    cd setup
    python 01_build_db.py

产物：
    haiyang.duckdb（库文件，已在 .gitignore 里排除，需要自己生成）
"""
import sys
from pathlib import Path

import duckdb
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "data" / "raw"
DB = HERE.parent / "haiyang.duckdb"


def read(rel, **kw):
    """统一读表：utf-8-sig 编码（处理 BOM），低内存模式。"""
    opt = dict(encoding="utf-8-sig", low_memory=False)
    opt.update(kw)
    return pd.read_csv(DATA / rel, **opt)


def fix_bad_line(line):
    """tech.csv 的备注字段含半角逗号，把 8 列撑成 9 列。这里把后两列拼回一列。"""
    return line[:7] + [",".join(line[7:])] if len(line) > 8 else line


def normalize_columns(df):
    """
    SQL 里带 & 和 % 的列名必须每次加引号才能用，很难写。
    统一改掉：去掉 &，把 _% 换成 _pct。
        R&D经费内部支出_亿元  →  RD经费内部支出_亿元
        第二产业占比_%        →  第二产业占比_pct
    """
    df = df.copy()
    df.columns = [str(c).replace("&", "").replace("_%", "_pct").strip() for c in df.columns]
    return df


def main():
    print(f"数据目录: {DATA}")
    print("读取 CSV ...")

    panel = read("panel_hqd.csv")
    macro = read("macro.csv")
    gop = read("gop.csv")
    gop_supplement = read("gop_supplement.csv")
    trade = read("trade.csv")
    city = read("panel_city_liaoning.csv")
    gdp_prov = read("01_沿海省份GDP与人均GDP_2020_2024.csv")

    # tech 必须用 python 引擎 + 回调修坏行，否则丢 110 行
    tech = pd.read_csv(
        DATA / "tech.csv",
        encoding="utf-8-sig", dtype=str,
        engine="python", on_bad_lines=fix_bad_line,
    )
    tech["年份"] = pd.to_numeric(tech["年份"], errors="coerce").astype("Int64")
    tech["数值"] = pd.to_numeric(tech["数值"], errors="coerce")

    # gop 的「未检索到」占位符统一转成 NULL，否则 COUNT / IS NULL 全算错
    for col in ["来源名称", "来源URL", "备注"]:
        if col in gop.columns:
            gop[col] = gop[col].astype("object").where(
                ~gop[col].astype(str).str.startswith("未检索到"), None
            )

    tables = {
        "panel_hqd": normalize_columns(panel),
        "macro": normalize_columns(macro),
        "gop": normalize_columns(gop),
        "gop_supplement": normalize_columns(gop_supplement),
        "tech": normalize_columns(tech),
        "trade": normalize_columns(trade),
        "panel_city": normalize_columns(city),
        "gdp_prov": normalize_columns(gdp_prov),
    }

    if DB.exists():
        DB.unlink()
    con = duckdb.connect(str(DB))
    for name, df in tables.items():
        con.register("_tmp", df)
        con.execute(f'CREATE TABLE "{name}" AS SELECT * FROM _tmp')
        con.unregister("_tmp")

    print(f"\n已写入 {DB.name}\n")
    print(f"{'表名':<18}{'行数':>7}{'列数':>7}")
    print("-" * 34)
    for name in tables:
        n = con.execute(f'SELECT COUNT(*) FROM "{name}"').fetchone()[0]
        c = len(con.execute(f'DESCRIBE "{name}"').fetchall())
        print(f"{name:<20}{n:>7}{c:>7}")

    con.close()
    print("\n完成。现在可以运行 20 个 .sql 文件了。")


if __name__ == "__main__":
    main()
