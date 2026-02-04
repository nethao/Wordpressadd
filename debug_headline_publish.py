#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
头条发布功能调试脚本
用于测试头条发布功能是否正常工作
"""

import asyncio
import json
from main_v2_4_final import wp_client

async def test_headline_publish():
    """测试头条发布功能"""
    print("🧪 开始测试头条发布功能...")
    
    # 测试数据
    test_title = "测试头条文章 - " + str(int(asyncio.get_event_loop().time()))
    test_content = "<p>这是一个测试头条文章的内容。</p><p>应该保存为草稿状态，分类ID为16035。</p>"
    
    try:
        # 测试普通发布
        print("\n📤 测试普通发布...")
        normal_result = await wp_client.create_post(
            title=f"普通文章 - {test_title}",
            content=test_content,
            publish_type="normal"
        )
        print(f"普通发布结果: {json.dumps(normal_result, indent=2, ensure_ascii=False)}")
        
        # 测试头条发布
        print("\n📋 测试头条发布...")
        headline_result = await wp_client.create_post(
            title=f"头条文章 - {test_title}",
            content=test_content,
            publish_type="headline"
        )
        print(f"头条发布结果: {json.dumps(headline_result, indent=2, ensure_ascii=False)}")
        
        # 检查结果
        if headline_result.get("error"):
            print(f"❌ 头条发布失败: {headline_result.get('message')}")
        else:
            print(f"✅ 头条发布成功!")
            print(f"   文章ID: {headline_result.get('id')}")
            print(f"   文章状态: {headline_result.get('status')}")
            print(f"   分类: {headline_result.get('categories', [])}")
            
    except Exception as e:
        print(f"❌ 测试过程中出现异常: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # 运行测试
    asyncio.run(test_headline_publish())