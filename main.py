#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WordPress 软文发布代理程序
集成百度AI内容审核功能
"""

import os
import json
import time
import base64
import asyncio
import aiohttp
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv, set_key
import uvicorn

# 加载环境变量
load_dotenv()

app = FastAPI(
    title="WordPress 软文发布代理",
    description="集成百度AI审核的WordPress文章发布中间件",
    version="1.0.0"
)

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# 模板配置
templates = Jinja2Templates(directory="templates")

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 请求模型
class PublishRequest(BaseModel):
    title: str = Field(..., description="文章标题")
    content: str = Field(..., description="文章内容")
    author_token: str = Field(..., description="作者验证令牌")

# 响应模型
class PublishResponse(BaseModel):
    success: bool
    message: str
    post_id: Optional[int] = None
    audit_result: Optional[Dict[str, Any]] = None

# 配置管理模型
class ConfigRequest(BaseModel):
    baidu_api_key: Optional[str] = None
    baidu_secret_key: Optional[str] = None
    wp_domain: Optional[str] = None
    wp_username: Optional[str] = None
    wp_app_password: Optional[str] = None
    valid_author_tokens: Optional[str] = None
    test_mode: Optional[bool] = None

class ConfigResponse(BaseModel):
    success: bool
    message: str
    config: Optional[Dict[str, Any]] = None

class BaiduAIClient:
    """百度AI内容审核客户端"""
    
    def __init__(self):
        self.api_key = os.getenv("BAIDU_API_KEY")
        self.secret_key = os.getenv("BAIDU_SECRET_KEY")
        self.access_token = None
        self.token_expires_at = None
        self.test_mode = os.getenv("TEST_MODE", "false").lower() == "true"
        
        if not self.test_mode and (not self.api_key or not self.secret_key):
            raise ValueError("百度AI API密钥未配置")
    
    async def get_access_token(self) -> str:
        """获取百度AI访问令牌，自动处理过期"""
        # 检查token是否过期
        if (self.access_token and self.token_expires_at and 
            datetime.now() < self.token_expires_at):
            return self.access_token
        
        # 获取新的access_token
        url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {
            "grant_type": "client_credentials",
            "client_id": self.api_key,
            "client_secret": self.secret_key
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, params=params, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.access_token = data["access_token"]
                        # 设置过期时间（提前5分钟刷新）
                        expires_in = data.get("expires_in", 2592000)  # 默认30天
                        self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 300)
                        return self.access_token
                    else:
                        raise HTTPException(status_code=500, detail="获取百度AI访问令牌失败")
            except asyncio.TimeoutError:
                raise HTTPException(status_code=500, detail="百度AI服务连接超时")
    
    async def text_audit(self, text: str) -> Dict[str, Any]:
        """文本内容审核"""
        # 测试模式：模拟审核结果
        if self.test_mode:
            # 检查是否包含测试敏感词
            sensitive_words = ["测试敏感词", "违规内容", "政治敏感"]
            has_sensitive = any(word in text for word in sensitive_words)
            
            if has_sensitive:
                return {
                    "conclusionType": 2,  # 不合规
                    "data": [{
                        "subType": "政治敏感",
                        "msg": "包含敏感内容",
                        "hits": [{
                            "words": [word for word in sensitive_words if word in text]
                        }]
                    }]
                }
            else:
                return {
                    "conclusionType": 1,  # 合规
                    "message": "测试模式：内容审核通过"
                }
        
        # 正常模式：调用百度API
        access_token = await self.get_access_token()
        url = f"https://aip.baidubce.com/rest/2.0/solution/v1/text_censor/v2/user_defined"
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json"
        }
        
        data = {
            "text": text,
            "access_token": access_token
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, headers=headers, data=data, timeout=30) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result
                    else:
                        error_text = await response.text()
                        raise HTTPException(
                            status_code=500, 
                            detail=f"百度AI审核服务错误: {error_text}"
                        )
            except asyncio.TimeoutError:
                raise HTTPException(status_code=500, detail="百度AI审核服务超时")

class WordPressClient:
    """WordPress REST API客户端"""
    
    def __init__(self):
        self.wp_domain = os.getenv("WP_DOMAIN")
        self.wp_username = os.getenv("WP_USERNAME")
        self.wp_app_password = os.getenv("WP_APP_PASSWORD")
        self.test_mode = os.getenv("TEST_MODE", "false").lower() == "true"
        
        if not self.test_mode and not all([self.wp_domain, self.wp_username, self.wp_app_password]):
            raise ValueError("WordPress配置信息不完整")
        
        if not self.test_mode:
            # 构建API基础URL
            self.api_base = f"https://{self.wp_domain}/wp-json/wp/v2"
            
            # 构建Basic Auth头
            credentials = f"{self.wp_username}:{self.wp_app_password}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()
            self.auth_header = f"Basic {encoded_credentials}"
    
    async def create_post(self, title: str, content: str) -> Dict[str, Any]:
        """创建WordPress文章"""
        # 测试模式：模拟发布结果
        if self.test_mode:
            # 模拟成功发布
            return {
                "id": 12345,
                "title": {"rendered": title},
                "content": {"rendered": content},
                "status": "pending",
                "date": datetime.now().isoformat(),
                "link": f"https://test-domain.com/posts/12345"
            }
        
        # 正常模式：调用WordPress API
        url = f"{self.api_base}/adv_posts"
        
        headers = {
            "Authorization": self.auth_header,
            "Content-Type": "application/json"
        }
        
        # 构建文章数据，强制设置为待审核状态
        post_data = {
            "title": title,
            "content": content,
            "status": "pending",  # 强制设为待审核
            "date": datetime.now().isoformat()
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, headers=headers, json=post_data, timeout=30) as response:
                    if response.status in [200, 201]:
                        result = await response.json()
                        return result
                    else:
                        error_text = await response.text()
                        raise HTTPException(
                            status_code=response.status,
                            detail=f"WordPress API错误: {error_text}"
                        )
            except asyncio.TimeoutError:
                raise HTTPException(status_code=500, detail="WordPress服务连接超时")

# 初始化客户端
baidu_client = BaiduAIClient()
wp_client = WordPressClient()

def verify_author_token(token: str) -> bool:
    """验证作者令牌"""
    valid_tokens = os.getenv("VALID_AUTHOR_TOKENS", "").split(",")
    return token.strip() in [t.strip() for t in valid_tokens if t.strip()]

@app.post("/publish", response_model=PublishResponse)
async def publish_article(request: PublishRequest):
    """
    发布文章接口
    1. 验证作者令牌
    2. 百度AI内容审核
    3. 发布到WordPress
    """
    
    # 1. 验证作者令牌
    if not verify_author_token(request.author_token):
        raise HTTPException(status_code=401, detail="无效的作者令牌")
    
    try:
        # 2. 百度AI内容审核
        # 合并标题和内容进行审核
        full_text = f"{request.title}\n\n{request.content}"
        audit_result = await baidu_client.text_audit(full_text)
        
        # 检查审核结果
        conclusion_type = audit_result.get("conclusionType", 0)
        
        if conclusion_type == 2:  # 不合规
            # 提取违规详情
            violation_details = []
            if "data" in audit_result:
                for item in audit_result["data"]:
                    if "hits" in item:
                        for hit in item["hits"]:
                            violation_details.append({
                                "违规词汇": hit.get("words", []),
                                "违规类型": item.get("subType", "未知"),
                                "违规描述": item.get("msg", "")
                            })
            
            return PublishResponse(
                success=False,
                message="内容审核未通过，包含敏感信息",
                audit_result={
                    "conclusion_type": conclusion_type,
                    "violations": violation_details
                }
            )
        
        elif conclusion_type != 1:  # 既不是合规也不是不合规
            return PublishResponse(
                success=False,
                message=f"内容审核状态异常: {conclusion_type}",
                audit_result=audit_result
            )
        
        # 3. 审核通过，发布到WordPress
        wp_result = await wp_client.create_post(request.title, request.content)
        
        return PublishResponse(
            success=True,
            message="文章发布成功，状态为待审核",
            post_id=wp_result.get("id"),
            audit_result={
                "conclusion_type": conclusion_type,
                "message": "内容审核通过"
            }
        )
        
    except HTTPException:
        # 重新抛出HTTP异常
        raise
    except Exception as e:
        # 处理其他异常
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """主页面"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request):
    """管理后台页面"""
    return templates.TemplateResponse("admin.html", {"request": request})

@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "WordPress软文发布代理"
    }

@app.get("/api/info")
async def api_info():
    """API信息接口"""
    return {
        "service": "WordPress软文发布代理",
        "version": "1.0.0",
        "endpoints": {
            "发布文章": "POST /publish",
            "健康检查": "GET /health",
            "API文档": "GET /docs"
        }
    }

if __name__ == "__main__":
    # 启动服务
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("DEBUG", "false").lower() == "true"
    )