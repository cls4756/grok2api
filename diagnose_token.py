#!/usr/bin/env python3
"""
Token诊断脚本 - 帮助理解为什么瀑布流可以工作但API失败

这个脚本会：
1. 检查token格式
2. 解码JWT token
3. 验证token是否是有效的Grok SSO token
"""

import base64
import json
import sys


def decode_jwt(token: str) -> dict:
    """解码JWT token"""
    try:
        parts = token.split('.')
        if len(parts) != 3:
            return {"error": "Invalid JWT format - should have 3 parts"}
        
        # Decode header
        header_data = parts[0] + '=' * (4 - len(parts[0]) % 4)
        header = json.loads(base64.urlsafe_b64decode(header_data))
        
        # Decode payload
        payload_data = parts[1] + '=' * (4 - len(parts[1]) % 4)
        payload = json.loads(base64.urlsafe_b64decode(payload_data))
        
        return {
            "header": header,
            "payload": payload,
            "is_jwt": True
        }
    except Exception as e:
        return {"error": f"Failed to decode JWT: {e}"}


def analyze_token(token: str) -> dict:
    """分析token格式"""
    result = {
        "token_preview": f"{token[:20]}..." if len(token) > 20 else token,
        "token_length": len(token),
        "format": "unknown"
    }
    
    # Check if it's a JWT
    if token.startswith("eyJ"):
        result["format"] = "JWT"
        result["jwt_info"] = decode_jwt(token)
        result["is_valid_grok_token"] = False
        result["reason"] = "JWT tokens are NOT valid Grok SSO tokens. Grok SSO tokens are long alphanumeric strings."
    
    # Check if it's a Grok SSO token (typically starts with AQAA or similar)
    elif len(token) > 100 and token.isalnum():
        result["format"] = "Possible Grok SSO Token"
        result["is_valid_grok_token"] = True
        result["reason"] = "This looks like a valid Grok SSO token format"
    
    else:
        result["format"] = "Unknown"
        result["is_valid_grok_token"] = False
        result["reason"] = "Token format doesn't match known patterns"
    
    return result


def main():
    print("=" * 80)
    print("Token 诊断工具")
    print("=" * 80)
    print()
    
    # Example token from user
    example_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzZXNzaW9uX2lkIjoiMTg2NWIxZmEtOGY1Yy00YTk1LTk1YTItODlhMWUxMDM5ZTYyIn0.d8TvJSIvDmXL40SvWO_9gpk8xqBZR0rcU3CMt3prRgs"
    
    print("分析示例token:")
    print("-" * 80)
    result = analyze_token(example_token)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print()
    
    print("=" * 80)
    print("关键发现:")
    print("=" * 80)
    print()
    print("1. 你的token是JWT格式，包含 session_id")
    print("2. JWT token 不是有效的 Grok SSO token")
    print("3. 有效的 Grok SSO token 应该是:")
    print("   - 长度通常 > 100 字符")
    print("   - 纯字母数字字符串")
    print("   - 不是JWT格式")
    print()
    print("4. 这解释了为什么:")
    print("   - API调用失败 (403): Grok.com 不认识这个JWT token")
    print("   - Token刷新返回false: Grok.com 认为这是无效token")
    print()
    print("=" * 80)
    print("疑问: 为什么瀑布流可以工作?")
    print("=" * 80)
    print()
    print("可能的原因:")
    print("1. 瀑布流实际上也失败了，但前端没有显示错误")
    print("2. 系统中还有其他有效的Grok SSO token，但/api/v1/admin/tokens没有显示完整")
    print("3. 有某种token转换机制我们还没发现")
    print()
    print("建议:")
    print("1. 检查瀑布流的实际网络请求，看是否真的成功")
    print("2. 检查系统中是否有其他token池")
    print("3. 获取一个真正的Grok SSO token (从grok.com登录后获取)")
    print()


if __name__ == "__main__":
    main()
