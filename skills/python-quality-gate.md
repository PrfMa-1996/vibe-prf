# Python 项目质量门禁模板

## 目的

这份 Skill 用于为 Python 项目建立可复用的质量门禁。目标是在本地提交前和 GitHub Actions CI 中统一运行测试、格式化检查和代码规范检查，尽早发现语法错误、格式漂移、依赖缺失和无界面环境下的运行问题。

## 安装步骤

### 1. 安装测试与门禁工具

```bash
pip install pytest pre-commit black flake8
```

如果项目使用 `requirements.txt`，建议加入：

```text
pytest
pre-commit
black
flake8
```

### 2. 初始化 pre-commit

```bash
pre-commit install
```

### 3. 本地验证

```bash
pytest
pre-commit run --all-files
black --check .
flake8 .
```

## GitHub Actions CI 配置

示例 `.github/workflows/python-quality.yml`：

```yaml
name: Python Quality Gate

on:
  push:
    branches: [main, master]
  pull_request:

jobs:
  quality:
    runs-on: ubuntu-latest

    env:
      MPLBACKEND: Agg
      PIP_DISABLE_PIP_VERSION_CHECK: "1"
      HTTP_PROXY: ${{ secrets.HTTP_PROXY }}
      HTTPS_PROXY: ${{ secrets.HTTPS_PROXY }}

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: pip

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
          pip install pytest pre-commit black flake8

      - name: Run tests
        run: pytest

      - name: Run pre-commit
        run: pre-commit run --all-files

      - name: Check formatting
        run: black --check .

      - name: Run flake8
        run: flake8 .
```

### 已知的坑

- TkAgg 无界面问题：GitHub Actions 的 Linux runner 没有桌面显示，Tkinter/Matplotlib 如果强制使用 `TkAgg` 容易失败。
- `MPLBACKEND` 环境变量：CI 中设置 `MPLBACKEND=Agg`，让 Matplotlib 使用无界面后端。
- 代码内后端切换：如果代码里有 `matplotlib.use("TkAgg")`，应在设置前检查 `MPLBACKEND`，避免 CI 覆盖失败。
- 网络代理设置：如果依赖下载受限，把 `HTTP_PROXY` 和 `HTTPS_PROXY` 放到 repository secrets，再在 workflow 的 `env` 中引用。
- 不要在 CI 中下载大型模型权重：模型权重应提前缓存、作为 release asset 管理，或把依赖模型的测试标记为可选。

## pre-commit 配置

示例 `.pre-commit-config.yaml`：

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 25.11.0
    hooks:
      - id: black

  - repo: https://github.com/pycqa/flake8
    rev: 7.3.0
    hooks:
      - id: flake8
```

常用命令：

```bash
pre-commit install
pre-commit run --all-files
pre-commit autoupdate
```

## 常见问题排查

### pre-commit 首次提交很慢

原因：首次运行会下载并创建 hook 虚拟环境。

解决：

```bash
pre-commit run --all-files
```

先手动初始化，后续提交会复用环境。

### pre-commit 无法访问 GitHub

原因：black/flake8 hook 仓库需要从 GitHub 拉取。

解决：

- 检查网络和代理。
- 配置 `HTTP_PROXY` / `HTTPS_PROXY`。
- 在 CI 中使用 secrets 注入代理。
- 不要用 `--no-verify` 掩盖长期问题；只在明确知道本次提交不受 hook 影响时临时使用。

### Matplotlib 在 CI 报 TkAgg 或 display 错误

原因：CI 无图形界面。

解决：

- 在 workflow 中设置 `MPLBACKEND=Agg`。
- 在代码中避免无条件调用 `matplotlib.use("TkAgg")`。
- 对 GUI 测试使用 mock、跳过标记或 xvfb。

### flake8 和 black 规则冲突

原因：flake8 默认行宽或某些规则与 black 不一致。

解决：在 `.flake8` 或 `setup.cfg` 中配置：

```ini
[flake8]
max-line-length = 88
extend-ignore = E203
```

### pytest 导入失败

原因：CI 工作目录、包结构或依赖安装方式和本地不同。

解决：

- 确认 `requirements.txt` 包含测试所需依赖。
- 使用 `python -m pytest` 验证解释器一致性。
- 如果项目是包结构，使用可编辑安装：`pip install -e .`。

### 质量门禁应该检查什么

最低门禁：

- `pytest`
- `black --check .`
- `flake8 .`
- `pre-commit run --all-files`

高风险项目可增加：

- 覆盖率阈值
- 类型检查
- 安全扫描
- 依赖漏洞扫描
- 关键生成文件或模型输出的存在性检查
