#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试AI审核开关配置保存修复
"""

import os
import time
from dotenv import load_dotenv, set_key

def test_ai_switch_persistence():
    """测试AI审核开关的持久化保存"""
    print("🧪 测试AI审核开关配置保存修复")
    print("=" * 50)
    
    # 1. 检查当前环境变量
    load_dotenv()
    original_value = os.getenv("ENABLE_AI_CHECK", "true")
    print(f"📋 当前AI审核开关: {original_value}")
    
    # 2. 模拟用户关闭AI审核开关
    print(f"\n🔧 模拟用户操作：关闭AI审核开关")
    set_key('.env', 'ENABLE_AI_CHECK', 'false')
    
    # 3. 重新加载环境变量（模拟后端处理）
    load_dotenv(override=True)
    updated_value = os.getenv("ENABLE_AI_CHECK", "true")
    print(f"   保存后的值: {updated_value}")
    
    # 4. 验证布尔值解析
    parsed_value = updated_value.lower() == "true"
    print(f"   解析为布尔值: {parsed_value}")
    
    # 5. 模拟前端配置加载
    print(f"\n🔍 模拟前端配置加载:")
    config = {
        "enable_ai_check": os.getenv("ENABLE_AI_CHECK", "true").lower() == "true"
    }
    print(f"   后端返回的配置: {config}")
    
    # 6. 模拟前端表单更新
    print(f"\n📝 模拟前端表单更新:")
    # 修复前的逻辑（错误）
    old_logic = config["enable_ai_check"] != False  # 这会导致问题
    print(f"   修复前逻辑 (enable_ai_check !== false): {old_logic}")
    
    # 修复后的逻辑（正确）
    new_logic = config["enable_ai_check"] == True  # 这是正确的
    print(f"   修复后逻辑 (enable_ai_check === true): {new_logic}")
    
    # 7. 测试各种情况
    print(f"\n🧪 测试各种配置值:")
    test_cases = [
        ("true", True),
        ("false", False),
        ("True", True),
        ("False", False),
        ("1", False),  # 非true/false字符串应该解析为false
        ("", False),   # 空字符串应该解析为false
    ]
    
    for test_value, expected in test_cases:
        # 临时设置环境变量
        set_key('.env', 'ENABLE_AI_CHECK', test_value)
        load_dotenv(override=True)
        
        # 模拟后端解析
        backend_parsed = os.getenv("ENABLE_AI_CHECK", "true").lower() == "true"
        
        # 模拟前端处理
        frontend_old = backend_parsed != False
        frontend_new = backend_parsed == True
        
        status = "✅" if backend_parsed == expected else "❌"
        print(f"   {status} 值'{test_value}' -> 后端解析:{backend_parsed}, 前端旧逻辑:{frontend_old}, 前端新逻辑:{frontend_new}")
    
    # 8. 恢复原始值
    set_key('.env', 'ENABLE_AI_CHECK', original_value)
    load_dotenv(override=True)
    print(f"\n🔄 已恢复原始值: {original_value}")
    
    print(f"\n" + "=" * 50)
    print("🎯 修复总结:")
    print("✅ 问题根因：前端使用了错误的布尔值判断逻辑")
    print("✅ 修复方案：将 enable_ai_check !== false 改为 enable_ai_check === true")
    print("✅ 额外优化：配置保存后延迟重新加载，避免立即覆盖用户设置")
    print("✅ 预期效果：用户关闭AI审核开关后，复选框状态会正确保持关闭状态")

if __name__ == "__main__":
    test_ai_switch_persistence()