# Module 02 - Terraform Cloud Baseline (GCP)

本模块提供最小可运行的 GCP 资源骨架，用于支撑后续批流一体数据管道：

- GCS Data Lake bucket
- BigQuery dataset（staging/core/marts）
- Pub/Sub topic + subscription（实时通道）
- Service Account（运行 collector/stream writer）

## 使用方式

1. 准备变量文件：

```bash
cp terraform.tfvars.example terraform.tfvars
```

2. 初始化与预览：

```bash
terraform init
terraform plan
```

3. 应用：

```bash
terraform apply
```

## 说明

- 当前为基础设施最小骨架，后续可扩展：
  - GKE
  - Artifact Registry
  - IAM 精细化绑定
  - Monitoring / Alert Policies
