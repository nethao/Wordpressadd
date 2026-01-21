#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WordPress 软文发布中间件 V2.4 测试版本
"""

import os
from fastapi import FastAPI
from dotenv import load_dotenv
import uvicorn

# 加载环境变量
load_dotenv()

# 创建FastAPI应用
app = FastAPI(
    title="文章发布系统 V2.4 测试版",
    description="功能优化版本测试",
    version="2.4.0-test"
)

@app.get("/")
async def root():
    """根路径"""
    return {"message": "WordPress软文发布中间件V2.4测试版正在运行"}

@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": "文章发布系统 V2.4 测试版",
        "version": "2.4.0-test",
        "ai_check_enabled": os.getenv("ENABLE_AI_CHECK", "false").lower() == "true"
    }

@app.get("/api/info")
async def api_info():
    """API信息"""
    return {
        "service": "文章发布系统 V2.4 测试版",
        "version": "2.4.0-test",
        "features": [
            "编辑器HTML代码模式",
            "发布历史面板",
            "AI审核开关优化"
        ]
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8002))
    print(f"🚀 启动WordPress软文发布中间件V2.4测试版")
    print(f"📍 访问地址: http://localhost:{port}")
    print("=" * 50)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        reload=False
    )