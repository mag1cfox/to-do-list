# Tests Directory

## 测试文件结构

```
tests/
├── backend/                 # 后端测试
│   ├── unit/               # 单元测试
│   ├── conftest.py         # pytest配置
│   └── fixtures/           # 测试数据
├── frontend/               # 前端测试
│   ├── components/         # 组件测试
│   └── pages/              # 页面测试
├── api/                    # API测试
├── integration/            # 集成测试
└── docs/                   # 测试文档
    └── reports/            # 测试报告
```

## 运行测试

### 后端测试
```bash
cd tests/backend
python -m pytest unit/ -v
```

### API测试
```bash
cd tests/api
python -m pytest -v
```

### 集成测试
```bash
cd tests/integration
python -m pytest -v
```

### 所有测试
```bash
cd tests
python -m pytest -v --tb=short
```