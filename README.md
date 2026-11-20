# dutyrota

[![CI](https://github.com/eastyou/dutyrota/actions/workflows/ci.yml/badge.svg)](https://github.com/eastyou/dutyrota/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9%2B-brightgreen.svg)](pyproject.toml)

给班主任用的值日轮值表生成器：把班级名单交给它，指定周数、每周天数和每天人数，一条命令生成一页 A4 值日表。**零依赖，不联网，单文件 HTML。**

排班不是简单地按顺序切分：每个人值日次数最多相差 1 次，同一天不会安排同一个人两次，换座位、换组长都不用重新手抄。

## 特性

- **均衡轮转**：总岗位数平均分配，任意两人的值日次数最多相差 1 次
- **同日不重复**：同一天不会出现同一个人两次
- **日期标注**：给出起始日期后，自动计算每周的日期范围和每天的具体日期
- **名单灵活**：支持每行一个名字的 TXT，也支持第一列为姓名的 CSV；`#` 开头是注释
- **重名提醒**：发现重名会明确指出，建议加 `A`/`B` 后缀，不会把两个人合并
- **次数统计**：表格下方自动汇总每个人的值日次数
- **可复现**：`--seed` 固定随机种子，同一份名单可以生成相同排班
- **A4 打印**：表头跨页重复，行不跨页，24 人 4 周也能排得清楚
- **43 个单元测试**：覆盖名单解析、均衡性、同日去重、日期计算与命令行

## 安装

```bash
pip install dutyrota
```

也可以下载源码后直接运行：

```bash
python -m dutyrota --help
```

## 名单格式

TXT，每行一个名字：

```text
# 初二(3)班值日名单
张伟
王芳
李娜
```

也支持 CSV，取第一列作为姓名，表头 `姓名` 会自动跳过：

```csv
姓名,备注
张伟,班长
王芳,
```

仓库里的 [examples/names.txt](examples/names.txt) 有 24 位同学，可以直接改。

## 用法

生成 4 周、每周 5 天、每天 2 人的值日表：

```bash
dutyrota -i examples/names.txt -o 值日表.html --weeks 4 --per-day 2
```

从 2026-11-23（周一）开始，自动标注每周日期：

```bash
dutyrota -i 名单.txt -o 值日表.html --weeks 4 --per-day 2 --start 2026-11-23
```

每天 3 人、排 6 周，固定随机种子便于和同事核对：

```bash
dutyrota -i 名单.txt -o 值日表.html --weeks 6 --per-day 3 --seed 2026
```

## 参数

| 参数 | 默认值 | 说明 |
| --- | --- | --- |
| `-i, --input` | 必填 | 名单文件，TXT 或 CSV |
| `-o, --output` | `值日表.html` | 输出 HTML 路径 |
| `--title` | `班级值日表` | 表格标题 |
| `--weeks` | `4` | 排几周，1~30 |
| `--days` | `5` | 每周几天，1~7 |
| `--per-day` | `2` | 每天几个人，1~10，不能超过名单人数 |
| `--start` | 无 | 起始日期，格式 `YYYY-MM-DD` |
| `--seed` | 无 | 随机种子，用于复现排班 |

## 排班规则

1. 总岗位数 = 周数 × 每周天数 × 每天人数
2. 总岗位数平均分给名单中的每个人，余数随机分配，因此任意两人次数最多相差 1
3. 依次填表时跳过当天已出现的人，保证同一天不重复
4. 如果每天人数超过名单人数，会直接报错，而不是生成有空缺的表

## 打印

浏览器打开生成的 HTML，按 `Ctrl/Cmd + P`：

- 纸张：A4 纵向
- 缩放：100%
- 勾选「背景图形」，表头和姓名标签的底色才会显示

周数较多时表格会自动分页，表头在每页重复出现。

## 开发

```bash
python -m unittest discover -s tests -v
```

## License

[MIT](LICENSE) © 2026 eastyou
