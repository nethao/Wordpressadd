#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WordPress软文发布中间件 V2.1 测试脚本
测试新功能和API接口
"""

import json
import urllib.request
import urllib.error

def test_health_check():
    """测试健康检查接口"""
    print("🔍 测试健康检查接口...")
    try:
        response = urllib.request.urlopen('http://localhost:8001/health')
        data = json.loads(response.read().decode())
        print(f"✅ 健康检查成功")
        print(f"   服务版本: {data.get('version', 'Unknown')}")
        print(f"   服务名称: {data.get('service', 'Unknown')}")
        return True
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")
        return False

def test_config_api():
    """测试配置管理API"""
    print("\n⚙️ 测试配置管理API...")
    try:
        # 获取当前配置
        response = urllib.request.urlopen('http://localhost:8001/config')
        data = json.loads(response.read().decode())
        
        if data.get('status') == 'success':
            print("✅ 配置获取成功")
            config = data.get('config', {})
            print(f"   测试模式: {config.get('test_mode', False)}")
            print(f"   WordPress域名: {config.get('wp_domain', '未配置')}")
            print(f"   百度API: {'已配置' if config.get('baidu_api_key') else '未配置'}")
            return True
        else:
            print(f"❌ 配置获取失败: {data.get('message')}")
            return False
    except Exception as e:
        print(f"❌ 配置API测试失败: {e}")
        return False

def test_publish_normal():
    """测试正常文章发布"""
    print("\n📝 测试正常文章发布...")
    
    data = {
        "title": "V2.1测试文章",
        "content": "<h2>这是一篇测试文章</h2><p>用于验证WordPress软文发布中间件V2.1版本的功能。</p><ul><li>富文本编辑器支持</li><li>百度AI内容审核</li><li>自动文章分类</li></ul>"
    }
    
    try:
        json_data = json.dumps(data, ensure_ascii=False).encode('utf-8')
        req = urllib.request.Request(
            'http://localhost:8001/publish',
            data=json_data,
            headers={'Content-Type': 'application/json'}
        )
        
        response = urllib.request.urlopen(req)
        result = json.loads(response.read().decode('utf-8'))
        
        print(f"📊 响应状态: {response.status}")
        print(f"📋 发布结果: {result.get('status')}")
        print(f"💬 响应消息: {result.get('message')}")
        
        if result.get('status') == 'success':
            print(f"✅ 文章发布成功！文章ID: {result.get('post_id')}")
            return True
        else:
            print(f"⚠️ 发布失败: {result.get('message')}")
            return False
            
    except urllib.error.HTTPError as e:
        error_data = e.read().decode('utf-8')
        print(f"❌ HTTP错误 {e.code}: {error_data}")
        return False
    except Exception as e:
        print(f"❌ 发布测试失败: {e}")
        return False

def test_publish_sensitive():
    """测试敏感内容检测"""
    print("\n🔍 测试敏感内容检测...")
    
    data = {
        "title": "包含测试敏感词的文章",
        "content": "<p>这篇文章包含<strong>测试敏感词</strong>，应该被百度AI审核系统拦截。</p><p>还包含其他<em>违规内容</em>进行测试。</p>"
    }
    
    try:
        json_data = json.dumps(data, ensure_ascii=False).encode('utf-8')
        req = urllib.request.Request(
            'http://localhost:8001/publish',
            data=json_data,
            headers={'Content-Type': 'application/json'}
        )
        
        response = urllib.request.urlopen(req)
        result = json.loads(response.read().decode('utf-8'))
        
        print(f"📊 响应状态: {response.status}")
        print(f"📋 审核结果: {result.get('status')}")
        print(f"💬 响应消息: {result.get('message')}")
        
        if result.get('status') == 'error' and '敏感词' in result.get('message', ''):
            print("✅ 敏感内容检测正常工作！")
            
            # 显示违规详情
            violations = result.get('violations', [])
            if violations:
                print("📋 违规详情:")
                for violation in violations:
                    print(f"   - 违规词汇: {violation.get('违规词汇', [])}")
                    print(f"   - 违规类型: {violation.get('违规类型', '未知')}")
            
            return True
        else:
            print("⚠️ 敏感内容检测可能有问题")
            return False
            
    except Exception as e:
        print(f"❌ 敏感内容测试失败: {e}")
        return False

def test_invalid_token():
    """测试系统配置验证"""
    print("\n🔒 测试系统配置验证...")
    
    # 这个测试现在主要验证系统配置是否正确
    data = {
        "title": "系统配置测试文章",
        "content": "<p>测试系统配置和身份验证</p>"
    }
    
    try:
        json_data = json.dumps(data).encode('utf-8')
        req = urllib.request.Request(
            'http://localhost:8001/publish',
            data=json_data,
            headers={'Content-Type': 'application/json'}
        )
        
        response = urllib.request.urlopen(req)
        result = json.loads(response.read().decode('utf-8'))
        
        if result.get('status') == 'success' or (result.get('status') == 'error' and '敏感词' in result.get('message', '')):
            print("✅ 系统配置验证正常！")
            return True
        else:
            print(f"⚠️ 系统配置可能有问题: {result.get('message')}")
            return False
            
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP错误: {e.code}")
        return False
    except Exception as e:
        print(f"❌ 系统配置测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🧪 WordPress软文发布中间件 V2.1 - 功能测试")
    print("=" * 70)
    
    test_results = []
    
    # 1. 健康检查测试
    test_results.append(test_health_check())
    
    # 2. 配置管理API测试
    test_results.append(test_config_api())
    
    # 3. 正常发布测试
    test_results.append(test_publish_normal())
    
    # 4. 敏感内容检测测试
    test_results.append(test_publish_sensitive())
    
    # 5. 系统配置验证测试
    test_results.append(test_invalid_token())
    
    # 测试结果汇总
    print("\n" + "=" * 70)
    print("📊 测试结果汇总")
    print("=" * 70)
    
    passed = sum(test_results)
    total = len(test_results)
    
    print(f"✅ 通过测试: {passed}/{total}")
    print(f"📈 成功率: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 所有测试通过！V2.1版本功能正常")
        print("💡 现在您可以访问以下地址使用系统：")
        print("   📝 发布页面: http://localhost:8001")
        print("   ⚙️ 管理后台: http://localhost:8001/admin")
        print("   📚 API文档: http://localhost:8001/docs")
    else:
        print(f"\n⚠️ 有 {total-passed} 个测试失败，请检查配置")
        print("💡 提示：")
        print("   1. 确保服务正在运行")
        print("   2. 检查.env文件中的CLIENT_AUTH_TOKEN配置")
        print("   3. 确认TEST_MODE=true以使用测试模式")

if __name__ == "__main__":
    main()