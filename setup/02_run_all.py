# -*- coding: utf-8 -*-
"""
02_run_all.py —— 一次跑完 20 个 .sql，检查每个文件的返回行数和列数。

用法：
    cd setup
    python 02_run_all.py

需要先运行 01_build_db.py 生成 haiyang.duckdb。
"""
import sys
from pathlib import Path

import duckdb

sys.stdout.reconfigure(encoding="utf-8")

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DB = ROOT / "haiyang.duckdb"

# 每题的预期 (行数, 列数)，用来验证 SQL 没有被改坏
EXPECT = {
    "q01": (11, 2), "q02": (10, 2), "q03": (6, 2),  "q04": (3, 2),  "q05": (25, 2),
    "q06": (3, 2),  "q07": (11, 2), "q08": (10, 2), "q09": (6, 2),  "q10": (11, 4),
    "q11": (3, 2),  "q12": (11, 2), "q13": (110, 6), "q14": (11, 4),
    "q15": (11, 3), "q16": (99, 3), "q17": (3, 3),
    "q18": (4, 2),  "q19": (11, 3), "q20": (3, 2),
}


def main():
    if not DB.exists():
        print(f"找不到 {DB.name}，请先运行 python 01_build_db.py")
        return 1

    con = duckdb.connect(str(DB), read_only=True)
    files = sorted(ROOT.rglob("q*.sql"))
    if not files:
        print("没有找到任何 .sql 文件")
        return 1

    print(f"共 {len(files)} 个文件\n")
    print(f"{'文件':<34}{'行':>5}{'列':>5}  结果")
    print("-" * 56)

    bad = 0
    for f in files:
        key = f.name[:3]
        try:
            df = con.execute(f.read_text(encoding="utf-8")).df()
        except Exception as e:
            bad += 1
            print(f"{f.name:<34}{'':>5}{'':>5}  ERR  {str(e).splitlines()[0][:60]}")
            continue

        n, c = df.shape
        want = EXPECT.get(key)
        if want and (n, c) != want:
            bad += 1
            print(f"{f.name:<34}{n:>5}{c:>5}  ✗ 预期 {want[0]} 行 × {want[1]} 列")
        else:
            print(f"{f.name:<34}{n:>5}{c:>5}  OK")

    con.close()
    print("-" * 56)
    print(f"{len(files) - bad} / {len(files)} 通过" if bad else f"全部 {len(files)} 题通过")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
