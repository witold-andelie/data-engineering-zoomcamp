# Module 08 - CI/CD + GitOps + Argo CD

本模块包含：

- GitHub Actions workflows（CI / Build&Publish / Deploy GitOps）
- Kubernetes manifests（collector + dashboard）
- Argo CD Application 定义

## 目录

- `.github/workflows/quant_ci.yml`
- `.github/workflows/quant_build_publish.yml`
- `.github/workflows/quant_deploy_gitops.yml`
- `gitops/base/*.yaml`
- `gitops/apps/quant-platform-app.yaml`

## GitOps 流程

1. `quant_build_publish.yml` 构建并推送镜像
2. `quant_deploy_gitops.yml` 更新 manifests 中镜像 tag
3. Argo CD 侦测 repo 变更并自动同步到集群

