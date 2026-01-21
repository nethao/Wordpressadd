#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WordPress 软文发布中间件 V2.4 简单测试
"""

import asyncio
import aiohttp
import json
from datetime import datetime

# 测试配置
BASE_URL = "http://localhost:8002"

async def test_v2_4_basic():
    """基础功能测试"""
    print("🧪 V2.4版本基础功能测试")
    print("=" * 40)
    
    async with aiohttp.ClientSession() as session:
        # 测试健康检查
        try:
            async with session.get(f"{BASE_URL}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ 健康检查通过 - 版本: {data.get('version')}")
                    print(f"🤖 AI审核状态: {'启用' if data.get('ai_check_enabled') else '禁用'}")
                else:
                    print(f"❌ 健康检查失败 - HTTP {response.status}")
        except Exception as e:
            print(f"❌ 连接失败: {e}")
            return False
        
        # 测试API信息
        try:
            async with session.get(f"{BASE_URL}/api/info") as response:
                if response.status == 200:
                    data = await response.json()
                    features = data.get('features', [])
                    v2_4_features = [
                        "编辑器HTML代码模式",
                        "发布历史面板", 
                        "AI审核开关优化"
                    ]
                    
                    has_v2_4 = all(f in features for f in v2_4_features)
                    print(f"✅ API信息获取成功 - V2.4功能: {'完整' if has_v2_4 else '部分缺失'}")
                else:
                    print(f"❌ API信息获取失败 - HTTP {response.status}")
        except Exception as e:
            print(f"❌ API信息获取异常: {e}")
        
        # 测试登录页面
        try:
            async with session.get(f"{BASE_URL}/login") as response:
                if response.status == 200:
                    print("✅ 登录页面访问正常")
                else:
                    print(f"❌ 登录页面访问失败 - HTTP {response.status}")
        except Exception as e:
            print(f"❌ 登录页面访问异常: {e}")
    
    print("\n🎯 V2.4版本基础测试完成")
    return True

if __name__ == "__main__":
    asyncio.run(test_v2_4_basic())