# Module 06 - dbt 分层建模与 α 因子

该模块实现 Warehouse 侧模型层：

- staging：标准化实时/批量基础字段
- marts：输出 dashboard 与 α 因子分析表

## 目录

- `dbt_project.yml`
- `profiles.yml.example`
- `models/staging/stg_trade_events_stream.sql`
- `models/staging/schema.yml`
- `models/marts/fct_alpha_factors_daily.sql`
- `models/marts/schema.yml`

## 使用

```bash
cd quant-finance-pipeline/dbt-quant
cp profiles.yml.example ~/.dbt/profiles.yml

dbt deps

dbt run --select staging

dbt run --select marts

dbt test
```

