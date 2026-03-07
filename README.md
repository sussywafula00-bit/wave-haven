# Wave-Haven CLI

**Unified Command Line Interface for Wave-Haven System**

🌊 Wave-Haven 系统的统一命令行管理工具

---

## Features | 特性

- ✅ **统一入口** - 一个命令管理 Wave 和 Haven 系统
- ✅ **状态监控** - 实时查看系统运行状态（美观表格 + JSON）
- ✅ **配置管理** - 统一的 YAML 配置管理
- ✅ **启动/停止** - 一键控制整个系统

---

## Installation | 安装

```bash
# 创建快捷命令
ln -s ~/.openclaw/workspace_shared/skills/wave-haven-cli/wave-haven ~/.local/bin/

# 或者使用完整路径
python3 ~/.openclaw/workspace_shared/skills/wave-haven-cli/wave-haven --help
```

---

## Usage | 用法

### 查看状态
```bash
# 美观的表格输出
wave-haven status

# JSON 格式（用于脚本）
wave-haven status --json
```

### 启动/停止系统
```bash
# 启动全部
wave-haven start

# 只启动 Wave
wave-haven start --wave

# 只启动 Haven
wave-haven start --haven

# 停止
wave-haven stop
```

### 配置管理
```bash
# 初始化配置
wave-haven config init

# 查看配置
wave-haven config show
```

---

## Configuration | 配置

配置文件位置: `~/.openclaw/config/wave-haven.yaml`

```yaml
system:
  base_path: ~/.openclaw
  log_level: INFO

wave:
  enabled: true
  max_concurrent_waves: 10
  default_timeout: 3600
  port: 8000

haven:
  enabled: true
  memory_layers: 4
  auto_optimize: true
  cache_size: 100MB

agents:
  nova: {enabled: true, role: coordinator}
  luna: {enabled: true, role: memory_keeper}
  dreamnova: {enabled: true, role: explorer}
  kiki: {enabled: true, role: optimizer}
  coco: {enabled: true, role: executor}
```

---

## License | 许可证

MIT
