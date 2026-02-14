# 代码修改总结

## 目的
添加详细的调试日志，帮助诊断为什么瀑布流可以成功生成图片，但通过OpenAI兼容API调用时返回403错误。

## 修改的文件

### 1. app/api/v1/chat.py
**修改位置**: 第278-305行（图片模型处理部分）

**添加内容**:
```python
logger.info(
    f"Image model detected: model={request.model}, prompt='{message[:50]}...', "
    f"stream={request.stream}"
)
```

**作用**: 记录何时检测到图片模型，以及请求参数

### 2. app/api/v1/image.py
**修改位置**: 
- 第323-329行：添加主要调试日志
- 第381行：添加WebSocket模式日志
- 第440行：添加HTTP API模式日志

**添加内容**:
```python
# 主要调试日志
logger.info(
    f"Image generation: stream={request.stream}, use_ws={use_ws}, "
    f"response_format={response_format}, n={request.n}, token={token[:10]}..."
)

# WebSocket模式
logger.info(f"Using WebSocket mode for image generation (non-streaming)")

# HTTP API模式
logger.info(f"Using HTTP API mode for image generation (non-streaming)")
```

**作用**: 
- 记录关键配置参数（use_ws, stream, response_format）
- 记录实际执行的代码路径（WebSocket vs HTTP API）
- 记录使用的token（前10个字符）

### 3. 新增文件

#### test_image_api.sh
测试脚本，用于：
1. 重启服务
2. 清空日志
3. 调用API
4. 显示相关日志

#### diagnose_token.py
Token格式诊断工具，用于分析JWT token格式

#### DIAGNOSIS.md
完整的诊断文档，包含：
- 问题描述
- 诊断步骤
- 可能的原因
- 解决方案

## 预期效果

运行测试后，日志中会显示：

**成功的WebSocket路径**:
```
Image model detected: model=grok-imagine-1.0, prompt='一只可爱的猫咪', stream=False
Image generation: stream=False, use_ws=True, response_format=url, n=1, token=eyJ0eXAiOi...
Using WebSocket mode for image generation (non-streaming)
Image generation: prompt='一只可爱的猫咪', n=1, ratio=2:3, nsfw=True
WebSocket request sent: ...
WebSocket collected 1 final images
```

**失败的HTTP API路径**:
```
Image model detected: model=grok-imagine-1.0, prompt='一只可爱的猫咪', stream=False
Image generation: stream=False, use_ws=False, response_format=url, n=1, token=eyJ0eXAiOi...
Using HTTP API mode for image generation (non-streaming)
Chat failed: status=403, token=eyJ0eXAiOi...
```

## 下一步

1. 重启服务: `docker compose restart grok2api`
2. 运行测试: `bash test_image_api.sh`
3. 查看日志，确认：
   - `use_ws` 的实际值
   - 代码走的路径（WebSocket vs HTTP API）
   - 是否有403错误

## 关键诊断点

根据日志中的 `use_ws=True/False` 和 `Using ... mode`，我们可以确定：

- 如果 `use_ws=True` 且 `Using WebSocket mode` → 应该成功（和瀑布流一样）
- 如果 `use_ws=False` 且 `Using HTTP API mode` → 会失败403（配置问题）

这样就能准确定位问题根源。
