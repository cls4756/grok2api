# 图片生成403错误诊断

## 问题描述
- 瀑布流可以成功生成图片 ✓
- API调用失败，返回403错误 ✗
- 两者使用相同的JWT token
- 配置正常（image_ws: true, image_ws_nsfw: true）

## 代码修改
已添加详细的调试日志到以下文件：
1. `app/api/v1/chat.py` - 记录图片模型检测和参数
2. `app/api/v1/image.py` - 记录use_ws配置和执行路径

## 诊断步骤

### 步骤1: 重启服务并测试
```bash
# 在服务器上运行
bash test_image_api.sh
```

这个脚本会：
1. 重启服务
2. 清空日志
3. 调用API
4. 显示相关日志

### 步骤2: 查看日志中的关键信息

查找以下日志行：

```bash
# 1. 检查是否检测到图片模型
docker compose logs grok2api | grep "Image model detected"

# 2. 检查use_ws配置
docker compose logs grok2api | grep "Image generation: stream="

# 3. 检查执行路径
docker compose logs grok2api | grep "Using.*mode"

# 4. 检查是否有403错误
docker compose logs grok2api | grep "Chat failed"
```

### 步骤3: 对比瀑布流和API的日志

**瀑布流成功时的日志应该包含：**
```
Image generation: prompt='...', n=6, ratio=2:3, nsfw=True
WebSocket request sent: ...
WebSocket collected X final images
```

**API调用的日志应该包含：**
```
Image model detected: model=grok-imagine-1.0, prompt='...', stream=False
Image generation: stream=False, use_ws=True/False, response_format=url, n=1, token=eyJ0eXAiOi...
Using WebSocket mode / Using HTTP API mode
```

## 可能的原因

### 原因1: use_ws配置为False
如果日志显示 `use_ws=False`，说明配置没有正确读取。

**解决方案：**
检查配置文件 `data/config.toml`，确保包含：
```toml
[image]
image_ws = true
image_ws_nsfw = true
```

### 原因2: 代码走了HTTP API路径
如果日志显示 `Using HTTP API mode`，说明代码没有使用WebSocket。

**可能原因：**
- `image_ws` 配置为 false
- 配置读取失败

### 原因3: response_format="url" 导致的问题
当前代码设置 `response_format="url"`，这会：
1. 接收WebSocket返回的base64图片
2. 保存到本地文件系统
3. 返回URL路径

这个过程不应该导致403，但可能有其他问题。

**测试方案：**
修改 `app/api/v1/chat.py`，将 `response_format="url"` 改为 `response_format="b64_json"`：

```python
image_request = ImageGenerationRequest(
    model=request.model,
    prompt=message,
    n=1,
    stream=request.stream,
    response_format="b64_json",  # 改为 b64_json
)
```

### 原因4: token格式问题（已排除）
你确认JWT token可以工作，所以这不是问题。

## 下一步

请运行 `bash test_image_api.sh` 并将完整输出发送给我，特别是：

1. API响应内容
2. 日志中的 "Image generation:" 行
3. 日志中的 "Using ... mode" 行
4. 任何403错误的详细信息

这样我就能准确定位问题所在。
