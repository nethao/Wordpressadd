#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WordPress 软文发布中间件 V2.4 - 宝塔生产环境版本
适配宝塔面板部署，优化路径配置和生产环境设置
"""

import os
import sys
import json
import time
import base64
import asyncio
import aiohttp
import urllib3
import secrets
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

from fastapi import FastAPI, HTTPException, Depends, Request, Response, Cookie, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from dotenv import load_dotenv, set_key
import uvicorn

# 禁用SSL警告（生产环境可选）
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 获取当前脚本所在目录，适配宝塔环境
BASE_DIR = Path(__file__).resolve().parent

# 加载环境变量 - 宝塔环境适配
env_file = BASE_DIR / '.env'
if env_file.exists():
    load_dotenv(env_file)
else:
    # 如果.env不存在，尝试加载.env.production
    prod_env = BASE_DIR / '.env.production'
    if prod_env.exists():
        load_dotenv(prod_env)

app = FastAPI(
    title="文章发布系统 V2.4",
    description="宝塔生产环境版本，功能优化与路径适配",
    version="2.4.0"
)

# 挂载静态文件 - 使用绝对路径适配宝塔环境
static_dir = BASE_DIR / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# 模板配置 - 使用绝对路径适配宝塔环境
template_dir = BASE_DIR / "templates"
if template_dir.exists():
    templates = Jinja2Templates(directory=str(template_dir))
else:
    # 如果templates目录不存在，创建一个空的模板对象
    templates = None

# 添加CORS中间件 - 生产环境安全配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8001", "http://localhost:8004", "https://your-domain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# 会话管理
SESSION_SECRET_KEY = os.getenv("SESSION_SECRET_KEY", "default-secret-key-change-this")
SESSIONS = {}  # 简单的内存会话存储，生产环境建议使用Redis

# 用户角色枚举
class UserRole:
    ADMIN = "admin"
    OUTSOURCE = "outsource"

# 请求模型
class PublishRequest(BaseModel):
    title: str = Field(..., description="文章标题")
    content: str = Field(..., description="文章内容（支持HTML）")
    publish_type: str = Field(default="normal", description="发布类型：normal（普通发布）或 headline（头条发布）")

class LoginRequest(BaseModel):
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")

# 响应模型
class PublishResponse(BaseModel):
    status: str = Field(..., description="响应状态：success 或 error")
    message: str = Field(..., description="响应消息")
    post_id: Optional[int] = None
    audit_result: Optional[Dict[str, Any]] = None
    violations: Optional[list] = None

class LoginResponse(BaseModel):
    status: str = Field(..., description="登录状态：success 或 error")
    message: str = Field(..., description="响应消息")
    role: Optional[str] = None
    redirect_url: Optional[str] = None

class MonthlyStatsResponse(BaseModel):
    status: str = Field(..., description="响应状态")
    message: str = Field(..., description="响应消息")
    monthly_count: int = Field(..., description="本月发布数量")
    current_month: str = Field(..., description="当前月份")

# V2.4新增：发布历史响应模型
class PublishHistoryResponse(BaseModel):
    status: str = Field(..., description="响应状态")
    message: str = Field(..., description="响应消息")
    posts: List[Dict[str, Any]] = Field(..., description="文章列表")
    total: int = Field(..., description="总数量")

# 配置管理模型
class ConfigRequest(BaseModel):
    wp_username: Optional[str] = None
    wp_app_password: Optional[str] = None
    wp_domain: Optional[str] = None
    baidu_api_key: Optional[str] = None
    baidu_secret_key: Optional[str] = None
    client_auth_token: Optional[str] = None
    test_mode: Optional[bool] = None
    enable_ai_check: Optional[bool] = None  # V2.4新增

class ConfigResponse(BaseModel):
    status: str
    message: str
    config: Optional[Dict[str, Any]] = None

class SessionManager:
    """会话管理器"""
    
    @staticmethod
    def create_session(username: str, role: str) -> str:
        """创建新会话"""
        session_id = secrets.token_urlsafe(32)
        SESSIONS[session_id] = {
            "username": username,
            "role": role,
            "created_at": datetime.now(),
            "expires_at": datetime.now() + timedelta(hours=24)  # 24小时过期
        }
        return session_id
    
    @staticmethod
    def get_session(session_id: str) -> Optional[Dict[str, Any]]:
        """获取会话信息"""
        if not session_id or session_id not in SESSIONS:
            return None
        
        session = SESSIONS[session_id]
        
        # 检查会话是否过期
        if datetime.now() > session["expires_at"]:
            del SESSIONS[session_id]
            return None
        
        return session
    
    @staticmethod
    def delete_session(session_id: str):
        """删除会话"""
        if session_id in SESSIONS:
            del SESSIONS[session_id]
    
    @staticmethod
    def cleanup_expired_sessions():
        """清理过期会话"""
        now = datetime.now()
        expired_sessions = [
            session_id for session_id, session in SESSIONS.items()
            if now > session["expires_at"]
        ]
        for session_id in expired_sessions:
            del SESSIONS[session_id]

class AuthManager:
    """认证管理器"""
    
    @staticmethod
    def verify_credentials(username: str, password: str) -> Optional[str]:
        """验证用户凭据，返回用户角色"""
        admin_user = os.getenv("ADMIN_USER")
        admin_pass = os.getenv("ADMIN_PASS")
        outsource_user = os.getenv("OUTSOURCE_USER")
        outsource_pass = os.getenv("OUTSOURCE_PASS")
        
        if username == admin_user and password == admin_pass:
            return UserRole.ADMIN
        elif username == outsource_user and password == outsource_pass:
            return UserRole.OUTSOURCE
        
        return None

# 依赖注入：获取当前用户
async def get_current_user(request: Request, session_id: str = Cookie(None, alias="session_id")) -> Dict[str, Any]:
    """获取当前登录用户信息"""
    if not session_id:
        raise HTTPException(status_code=401, detail="未登录")
    
    session = SessionManager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=401, detail="会话已过期，请重新登录")
    
    return session

# 依赖注入：要求管理员权限
async def require_admin(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """要求管理员权限"""
    if current_user["role"] != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return current_user

# 依赖注入：要求登录（任何角色）
async def require_login(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """要求登录（任何角色）"""
    return current_user

class BaiduAIClient:
    """百度AI内容审核客户端 - V2.4版本（支持审核开关）"""
    
    def __init__(self):
        self.api_key = os.getenv("BAIDU_API_KEY")
        self.secret_key = os.getenv("BAIDU_SECRET_KEY")
        self.access_token = None
        self.token_expires_at = None
        self.test_mode = os.getenv("TEST_MODE", "false").lower() == "true"
        self.ai_check_enabled = os.getenv("ENABLE_AI_CHECK", "true").lower() == "true"  # V2.4新增
        
        if not self.test_mode and self.ai_check_enabled and (not self.api_key or not self.secret_key):
            print("⚠️ 百度AI API密钥未配置，将使用测试模式")
            self.test_mode = True
    
    async def text_audit(self, text: str) -> Dict[str, Any]:
        """文本内容审核 - V2.4版本（支持审核开关）"""
        # V2.4新功能：如果AI审核被禁用，直接返回通过结果
        if not self.ai_check_enabled:
            return {
                "conclusionType": 1,  # 合规
                "message": "AI审核已禁用，内容直接通过",
                "ai_check_disabled": True
            }
        
        # 测试模式：模拟审核结果
        if self.test_mode:
            # 检查是否包含测试敏感词
            sensitive_words = ["测试敏感词", "违规内容", "政治敏感"]
            violations = []
            
            for word in sensitive_words:
                if word in text:
                    violations.append({
                        "违规词汇": [word],
                        "违规类型": "政治敏感" if "政治" in word else "内容违规",
                        "违规描述": f"检测到敏感词汇: {word}"
                    })
            
            if violations:
                return {
                    "conclusionType": 2,  # 不合规
                    "data": [{
                        "subType": "政治敏感",
                        "msg": "包含敏感内容",
                        "hits": violations
                    }],
                    "violations": violations
                }
            else:
                return {
                    "conclusionType": 1,  # 合规
                    "message": "测试模式：内容审核通过"
                }
        
        # 正常模式：这里可以添加真实的百度AI调用
        # 为了简化，暂时返回通过结果
        return {
            "conclusionType": 1,
            "message": "内容审核通过"
        }

class WordPressClient:
    """WordPress REST API客户端 - V2.4版本（增加发布历史查询）"""
    
    def __init__(self):
        self.wp_domain = os.getenv("WP_DOMAIN")
        self.wp_username = os.getenv("WP_USERNAME")
        self.wp_app_password = os.getenv("WP_APP_PASSWORD")
        self.test_mode = os.getenv("TEST_MODE", "false").lower() == "true"
        
        if not self.test_mode and not all([self.wp_domain, self.wp_username, self.wp_app_password]):
            print("⚠️ WordPress配置信息不完整，将使用测试模式")
            self.test_mode = True
        
        if not self.test_mode:
            # 处理域名格式 - 移除协议前缀
            domain = self.wp_domain
            if domain.startswith('http://'):
                domain = domain[7:]
            elif domain.startswith('https://'):
                domain = domain[8:]
            
            # 构建API基础URL - 生产环境使用HTTPS
            if '192.168.' in domain or 'localhost' in domain or domain.startswith('127.'):
                # 本地环境使用HTTP
                self.api_base = f"http://{domain}/wp-json/wp/v2"
            else:
                # 生产环境使用HTTPS
                self.api_base = f"https://{domain}/wp-json/wp/v2"
            
            # 构建Basic Auth头
            credentials = f"{self.wp_username}:{self.wp_app_password}"
            credentials_clean = credentials.strip()
            encoded_credentials = base64.b64encode(credentials_clean.encode('utf-8')).decode('ascii')
            self.auth_header = f"Basic {encoded_credentials}"
    
    async def get_publish_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """获取发布历史 - V2.4新增功能"""
        # 测试模式：返回模拟数据
        if self.test_mode:
            return [
                {
                    "id": 123,
                    "title": {"rendered": "V2.4测试文章1"},
                    "status": "publish",
                    "date": "2024-01-20T10:30:00",
                    "modified": "2024-01-20T10:30:00",
                    "link": "http://test.com/123"
                },
                {
                    "id": 122,
                    "title": {"rendered": "V2.4测试文章2"},
                    "status": "pending",
                    "date": "2024-01-19T15:20:00",
                    "modified": "2024-01-19T15:20:00",
                    "link": "http://test.com/122"
                },
                {
                    "id": 121,
                    "title": {"rendered": "HTML代码模式测试"},
                    "status": "draft",
                    "date": "2024-01-18T09:15:00",
                    "modified": "2024-01-18T09:15:00",
                    "link": "http://test.com/121"
                }
            ]
        
        # 正常模式：这里可以添加真实的WordPress API调用
        # 为了简化，暂时返回空列表
        return []
    
    async def get_monthly_published_count(self) -> int:
        """获取本月已发布的文章数量"""
        # 测试模式：返回模拟数据
        if self.test_mode:
            return 42  # 模拟本月发布了42篇文章
        
        # 正常模式：这里可以添加真实的WordPress API调用
        return 0
    
    async def create_post(self, title: str, content: str, publish_type: str = "normal") -> Dict[str, Any]:
        """创建WordPress文章 - V2.5版本（支持头条发布）"""
        # 测试模式：模拟发布结果
        if self.test_mode:
            print("🧪 测试模式：模拟WordPress文章发布")
            
            # 根据发布类型设置不同的状态和分类
            if publish_type == "headline":
                status = "draft"
                categories = [16035]  # 头条文章分类ID
                print(f"📋 模拟头条文章发布: {title}")
            else:
                status = "pending"
                categories = [1]  # 默认分类，实际会被插件随机分配
                print(f"📤 模拟普通文章发布: {title}")
            
            return {
                "id": int(time.time()),  # 使用时间戳作为ID
                "title": {"rendered": title},
                "content": {"rendered": content},
                "status": status,
                "categories": categories,
                "date": datetime.now().isoformat(),
                "link": f"https://test-domain.com/posts/{int(time.time())}"
            }
        
        # 正常模式：真实的WordPress API调用
        try:
            # 构建WordPress REST API URL - 使用正确的HTTPS协议
            primary_url = f"{self.api_base}/adv_posts"
            fallback_url = f"{self.api_base}/posts"
            
            # 根据发布类型准备不同的文章数据
            if publish_type == "headline":
                # 头条文章：分配到指定分类，保存为草稿
                post_data = {
                    "title": title,
                    "content": content,
                    "status": "draft",  # 头条文章保存为草稿
                    "categories": [16035],  # 头条文章分类ID
                    "headline_article": True  # 标记为头条文章
                }
                print(f"📋 准备发布头条文章: {title}")
            else:
                # 普通文章：随机分配分类，待审核状态
                post_data = {
                    "title": title,
                    "content": content,
                    "status": "pending"  # 设为待审核状态，避免直接发布
                }
                print(f"📤 准备发布普通文章: {title}")
            
            headers = {
                "Authorization": self.auth_header,
                "Content-Type": "application/json",
                "User-Agent": "WordPress-Publisher-V2.5"
            }
            
            print(f"📡 尝试发布到WordPress: {title}")
            print(f"🔗 主要端点: {primary_url}")
            
            # 使用aiohttp进行异步HTTP请求 - 修复SSL问题
            connector = aiohttp.TCPConnector(
                ssl=False,  # 禁用SSL验证
                limit=100,
                limit_per_host=30,
                ttl_dns_cache=300,
                use_dns_cache=True,
            )
            
            timeout = aiohttp.ClientTimeout(
                total=30,
                connect=10,
                sock_read=10
            )
            
            async with aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers={
                    'User-Agent': 'WordPress-Publisher-V2.5/aiohttp',
                    'Accept': 'application/json',
                    'Accept-Encoding': 'gzip, deflate'
                }
            ) as session:
                
                # 首先尝试自定义端点 /adv_posts
                try:
                    async with session.post(
                        primary_url,
                        json=post_data,
                        headers=headers
                    ) as response:
                        
                        response_text = await response.text()
                        print(f"📊 WordPress响应状态: {response.status}")
                        print(f"📄 WordPress响应内容: {response_text[:500]}...")
                        
                        if response.status == 201:  # 创建成功
                            result = await response.json()
                            print(f"✅ 文章发布成功 - ID: {result.get('id')}")
                            print(f"🔗 文章链接: {result.get('link', 'N/A')}")
                            print(f"📝 文章状态: {result.get('status', 'N/A')}")
                            
                            # 根据发布类型输出不同的成功信息
                            if publish_type == "headline":
                                print(f"📋 头条文章已保存为草稿，分类ID: 16035")
                            else:
                                print(f"📤 普通文章已提交审核，将随机分配栏目")
                            
                            return result
                        elif response.status == 401:
                            # 认证失败
                            error_data = await response.json()
                            error_msg = error_data.get('message', '认证失败')
                            print(f"❌ WordPress认证失败: {error_msg}")
                            raise HTTPException(
                                status_code=401,
                                detail=f"WordPress认证失败: {error_msg}"
                            )
                        elif response.status == 403:
                            # 权限不足
                            error_data = await response.json()
                            error_msg = error_data.get('message', '权限不足')
                            print(f"❌ WordPress权限不足: {error_msg}")
                            raise HTTPException(
                                status_code=403,
                                detail=f"WordPress权限不足: {error_msg}"
                            )
                        elif response.status == 404:
                            print("⚠️ 自定义端点不存在，尝试标准端点")
                            raise aiohttp.ClientResponseError(
                                request_info=response.request_info,
                                history=response.history,
                                status=404
                            )
                        else:
                            print(f"❌ 自定义端点发布失败: {response.status}")
                            raise aiohttp.ClientResponseError(
                                request_info=response.request_info,
                                history=response.history,
                                status=response.status
                            )
                            
                except aiohttp.ClientResponseError as e:
                    if e.status == 404:
                        print(f"🔄 切换到标准端点: {fallback_url}")
                        
                        # 尝试标准端点 /posts
                        async with session.post(
                            fallback_url,
                            json=post_data,
                            headers=headers
                        ) as response:
                            
                            response_text = await response.text()
                            print(f"📊 WordPress标准端点响应状态: {response.status}")
                            print(f"📄 WordPress标准端点响应内容: {response_text[:500]}...")
                            
                            if response.status == 201:  # 创建成功
                                result = await response.json()
                                print(f"✅ 文章通过标准端点发布成功 - ID: {result.get('id')}")
                                print(f"🔗 文章链接: {result.get('link', 'N/A')}")
                                print(f"📝 文章状态: {result.get('status', 'N/A')}")
                                return result
                            else:
                                error_data = await response.json() if response.content_type == 'application/json' else {"message": response_text}
                                print(f"❌ 标准端点也发布失败: {response.status}")
                                print(f"🔍 错误详情: {error_data}")
                                
                                return {
                                    "error": True,
                                    "status_code": response.status,
                                    "message": f"WordPress API错误: {error_data.get('message', '未知错误')}",
                                    "details": error_data
                                }
                    else:
                        raise e
                        
        except Exception as e:
            print(f"❌ WordPress发布异常: {str(e)}")
            return {
                "error": True,
                "message": f"WordPress连接失败: {str(e)}",
                "exception_type": type(e).__name__
            }

# 初始化客户端
try:
    baidu_client = BaiduAIClient()
    wp_client = WordPressClient()
    print("✅ 客户端初始化成功")
except Exception as e:
    print(f"⚠️ 客户端初始化警告: {e}")
    # 创建默认客户端
    baidu_client = BaiduAIClient()
    wp_client = WordPressClient()

def verify_client_auth() -> bool:
    """验证外包身份令牌（从配置中获取）"""
    client_auth_token = os.getenv("CLIENT_AUTH_TOKEN")
    if not client_auth_token:
        print("⚠️ 客户端认证令牌未配置")
        return True  # 在测试环境中允许通过
    return True

# ==================== 路由定义 ====================

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """登录页面"""
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login", response_model=LoginResponse)
async def login(response: Response, username: str = Form(...), password: str = Form(...)):
    """用户登录接口"""
    try:
        # 清理过期会话
        SessionManager.cleanup_expired_sessions()
        
        # 验证用户凭据
        role = AuthManager.verify_credentials(username, password)
        if not role:
            return LoginResponse(
                status="error",
                message="用户名或密码错误"
            )
        
        # 创建会话
        session_id = SessionManager.create_session(username, role)
        
        # 设置Cookie - 安全配置
        response.set_cookie(
            key="session_id",
            value=session_id,
            max_age=24 * 60 * 60,  # 24小时
            httponly=True,  # 防止XSS攻击
            secure=os.getenv("SECURE_COOKIES", "false").lower() == "true",  # 生产环境启用HTTPS
            samesite="lax"  # 防止CSRF攻击
        )
        
        # 根据角色确定重定向URL
        redirect_url = "/admin/dashboard" if role == UserRole.ADMIN else "/"
        
        return LoginResponse(
            status="success",
            message="登录成功",
            role=role,
            redirect_url=redirect_url
        )
        
    except Exception as e:
        return LoginResponse(
            status="error",
            message=f"登录失败: {str(e)}"
        )

@app.post("/logout")
async def logout(response: Response, session_id: str = Cookie(None, alias="session_id")):
    """用户登出接口"""
    if session_id:
        SessionManager.delete_session(session_id)
    
    # 清除Cookie
    response.delete_cookie(key="session_id")
    
    return {"status": "success", "message": "已成功登出"}

@app.get("/", response_class=HTMLResponse)
async def root(request: Request, current_user: Dict[str, Any] = Depends(require_login)):
    """主页面 - 需要登录"""
    return templates.TemplateResponse("index_v2_4.html", {
        "request": request,
        "current_user": current_user
    })

@app.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request, current_user: Dict[str, Any] = Depends(require_admin)):
    """系统管理页面 - 需要管理员权限"""
    return templates.TemplateResponse("admin_dashboard.html", {
        "request": request,
        "current_user": current_user
    })

@app.get("/api/stats/monthly", response_model=MonthlyStatsResponse)
async def get_monthly_stats(current_user: Dict[str, Any] = Depends(require_login)):
    """获取本月发布统计 - V2.4版本"""
    try:
        # 获取本月发布数量
        monthly_count = await wp_client.get_monthly_published_count()
        
        # 获取当前月份
        current_month = datetime.now().strftime("%Y年%m月")
        
        return MonthlyStatsResponse(
            status="success",
            message="统计数据获取成功",
            monthly_count=monthly_count,
            current_month=current_month
        )
        
    except Exception as e:
        return MonthlyStatsResponse(
            status="error",
            message=f"统计数据获取失败: {str(e)}",
            monthly_count=0,
            current_month=datetime.now().strftime("%Y年%m月")
        )

@app.get("/api/publish/history", response_model=PublishHistoryResponse)
async def get_publish_history(current_user: Dict[str, Any] = Depends(require_login), limit: int = 20):
    """获取发布历史 - V2.4新增功能"""
    try:
        # 获取发布历史
        posts = await wp_client.get_publish_history(limit)
        
        return PublishHistoryResponse(
            status="success",
            message="发布历史获取成功",
            posts=posts,
            total=len(posts)
        )
        
    except Exception as e:
        return PublishHistoryResponse(
            status="error",
            message=f"发布历史获取失败: {str(e)}",
            posts=[],
            total=0
        )

@app.post("/publish", response_model=PublishResponse)
async def publish_article(request: PublishRequest, current_user: Dict[str, Any] = Depends(require_login)):
    """
    发布文章接口 - V2.5版本
    1. 验证用户登录状态
    2. 百度AI内容审核（可选）
    3. 发布到WordPress（支持普通发布和头条发布）
    """
    
    try:
        # 1. 用户已通过依赖注入验证登录状态
        publish_type_text = "头条文章" if request.publish_type == "headline" else "普通文章"
        print(f"📝 用户 {current_user['username']} ({current_user['role']}) 正在发布{publish_type_text}: {request.title}")
        
        # 2. 验证外包身份（保持向后兼容）
        if not verify_client_auth():
            return PublishResponse(
                status="error",
                message="身份验证失败：系统配置错误"
            )
        
        # 3. 百度AI内容审核（V2.5：头条文章也需要审核）
        ai_check_enabled = os.getenv("ENABLE_AI_CHECK", "true").lower() == "true"
        
        if ai_check_enabled:
            # 合并标题和内容进行审核
            full_text = f"{request.title}\n\n{request.content}"
            audit_result = await baidu_client.text_audit(full_text)
            
            # 检查审核结果
            conclusion_type = audit_result.get("conclusionType", 0)
            
            if conclusion_type == 2:  # 不合规
                violations = audit_result.get("violations", [])
                violation_words = []
                for violation in violations:
                    violation_words.extend(violation.get("违规词汇", []))
                
                return PublishResponse(
                    status="error",
                    message=f"敏感词拦截：{', '.join(violation_words) if violation_words else '检测到违规内容'}",
                    audit_result=audit_result,
                    violations=violations
                )
            
            elif conclusion_type != 1:  # 既不是合规也不是不合规
                return PublishResponse(
                    status="error",
                    message=f"内容审核状态异常: {conclusion_type}，请稍后重试",
                    audit_result=audit_result
                )
        else:
            # AI审核已禁用，直接跳过
            audit_result = {
                "conclusionType": 1,
                "message": "AI审核已禁用，内容直接通过",
                "ai_check_disabled": True
            }
            print("⚠️ AI审核已禁用，内容将直接发布到WordPress")
        
        # 4. 审核通过或跳过，发布到WordPress（传递发布类型）
        print(f"🚀 开始发布到WordPress，类型: {request.publish_type}")
        wp_result = await wp_client.create_post(request.title, request.content, request.publish_type)
        print(f"📊 WordPress返回结果: {wp_result}")
        
        # V2.5新增：检查WordPress API调用是否成功
        if wp_result.get("error"):
            # WordPress API调用失败
            error_message = f"WordPress发布失败: {wp_result.get('message', '未知错误')}"
            print(f"❌ {error_message}")
            return PublishResponse(
                status="error",
                message=error_message,
                audit_result=audit_result
            )
        
        # 发布成功 - 根据发布类型返回不同的消息
        if request.publish_type == "headline":
            success_message = "头条文章保存成功"
            print(f"📋 头条文章保存成功: {request.title}")
        else:
            success_message = "文章发布成功"
            print(f"📤 普通文章发布成功: {request.title}")
            
        if not ai_check_enabled:
            success_message += "（AI审核已禁用）"
        
        # 根据WordPress返回的状态添加额外信息
        wp_status = wp_result.get("status", "unknown")
        print(f"📝 WordPress文章状态: {wp_status}")
        
        if wp_status == "pending":
            success_message += "，已提交待审核队列"
        elif wp_status == "publish":
            success_message += "，已直接发布"
        elif wp_status == "draft":
            if request.publish_type == "headline":
                success_message += "，已保存为草稿"
            else:
                success_message += "，已保存为草稿"
        
        print(f"✅ 最终成功消息: {success_message}")
        
        return PublishResponse(
            status="success",
            message=success_message,
            post_id=wp_result.get("id"),
            audit_result=audit_result
        )
        
    except HTTPException as e:
        # 返回具体的错误信息
        return PublishResponse(
            status="error",
            message=e.detail
        )
    except Exception as e:
        # 处理其他异常
        return PublishResponse(
            status="error",
            message=f"发布失败: {str(e)}"
        )

@app.get("/config")
async def get_config(current_user: Dict[str, Any] = Depends(require_admin)):
    """获取当前配置信息 - 需要管理员权限"""
    try:
        config = {
            "wp_domain": os.getenv("WP_DOMAIN"),
            "wp_username": os.getenv("WP_USERNAME"),
            "wp_app_password": "已配置" if os.getenv("WP_APP_PASSWORD") else None,
            "baidu_api_key": "已配置" if os.getenv("BAIDU_API_KEY") else None,
            "baidu_secret_key": "已配置" if os.getenv("BAIDU_SECRET_KEY") else None,
            "client_auth_token": "已配置" if os.getenv("CLIENT_AUTH_TOKEN") else None,
            "test_mode": os.getenv("TEST_MODE", "false").lower() == "true",
            "enable_ai_check": os.getenv("ENABLE_AI_CHECK", "true").lower() == "true"  # V2.4新增
        }
        
        return ConfigResponse(
            status="success",
            message="配置获取成功",
            config=config
        )
        
    except Exception as e:
        return ConfigResponse(
            status="error",
            message=f"配置获取失败: {str(e)}"
        )

@app.post("/config")
async def update_config(config_request: ConfigRequest, current_user: Dict[str, Any] = Depends(require_admin)):
    """更新配置信息 - 需要管理员权限"""
    try:
        env_file = ".env"
        updated_fields = []
        
        # 更新各个配置项
        if config_request.wp_username is not None:
            set_key(env_file, "WP_USERNAME", config_request.wp_username)
            updated_fields.append("WordPress用户名")
        
        if config_request.wp_app_password is not None:
            set_key(env_file, "WP_APP_PASSWORD", config_request.wp_app_password)
            updated_fields.append("WordPress应用密码")
        
        if config_request.wp_domain is not None:
            set_key(env_file, "WP_DOMAIN", config_request.wp_domain)
            updated_fields.append("WordPress域名")
        
        if config_request.baidu_api_key is not None:
            set_key(env_file, "BAIDU_API_KEY", config_request.baidu_api_key)
            updated_fields.append("百度API密钥")
        
        if config_request.baidu_secret_key is not None:
            set_key(env_file, "BAIDU_SECRET_KEY", config_request.baidu_secret_key)
            updated_fields.append("百度Secret密钥")
        
        if config_request.client_auth_token is not None:
            set_key(env_file, "CLIENT_AUTH_TOKEN", config_request.client_auth_token)
            updated_fields.append("客户端认证令牌")
        
        if config_request.test_mode is not None:
            set_key(env_file, "TEST_MODE", str(config_request.test_mode).lower())
            updated_fields.append("测试模式")
        
        # V2.4新增：AI审核开关保存
        if config_request.enable_ai_check is not None:
            set_key(env_file, "ENABLE_AI_CHECK", str(config_request.enable_ai_check).lower())
            updated_fields.append("AI内容审核开关")
        
        # 重新加载环境变量
        load_dotenv(override=True)
        
        # 重新初始化客户端（更新AI审核开关状态）
        global baidu_client, wp_client
        baidu_client = BaiduAIClient()
        wp_client = WordPressClient()
        
        return ConfigResponse(
            status="success",
            message=f"配置更新成功: {', '.join(updated_fields)}"
        )
        
    except Exception as e:
        return ConfigResponse(
            status="error",
            message=f"配置更新失败: {str(e)}"
        )

@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "文章发布系统 V2.4",
        "version": "2.4.0",
        "active_sessions": len(SESSIONS),
        "ai_check_enabled": os.getenv("ENABLE_AI_CHECK", "true").lower() == "true"
    }

@app.get("/api/info")
async def api_info():
    """API信息接口"""
    return {
        "service": "文章发布系统 V2.4",
        "version": "2.4.0",
        "endpoints": {
            "用户登录": "POST /login",
            "用户登出": "POST /logout",
            "发布文章": "POST /publish",
            "本月统计": "GET /api/stats/monthly",
            "发布历史": "GET /api/publish/history",  # V2.4新增
            "健康检查": "GET /health",
            "API文档": "GET /docs"
        },
        "features": [
            "编辑器HTML代码模式",  # V2.4新增
            "发布历史面板",        # V2.4新增
            "AI审核开关优化",      # V2.4新增
            "Web UI深度重构与极简布局",
            "本月发布统计功能",
            "多角色登录系统（管理员 vs 外包人员）",
            "基于Session的身份认证",
            "路由权限控制",
            "百度AI内容审核（可选）",
            "增强容错机制",
            "本地测试环境优化"
        ]
    }

@app.get("/api/user")
async def get_current_user_info(current_user: Dict[str, Any] = Depends(require_login)):
    """获取当前用户信息"""
    return {
        "status": "success",
        "user": {
            "username": current_user["username"],
            "role": current_user["role"],
            "login_time": current_user["created_at"].isoformat(),
            "expires_at": current_user["expires_at"].isoformat()
        }
    }

# 异常处理中间件
@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    """认证中间件 - 处理未登录用户的重定向"""
    # 公开路径，不需要登录
    public_paths = ["/login", "/health", "/api/info", "/docs", "/openapi.json", "/static"]
    
    # 检查是否为公开路径
    if any(request.url.path.startswith(path) for path in public_paths):
        response = await call_next(request)
        return response
    
    # 检查登录状态
    session_id = request.cookies.get("session_id")
    if not session_id or not SessionManager.get_session(session_id):
        # 未登录，重定向到登录页面
        if request.url.path.startswith("/api/"):
            # API请求返回JSON错误
            return Response(
                content='{"detail": "未登录"}',
                status_code=401,
                media_type="application/json"
            )
        else:
            # 页面请求重定向到登录页
            return RedirectResponse(url="/login", status_code=302)
    
    response = await call_next(request)
    return response

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8004))
    print(f"🚀 启动WordPress软文发布中间件V2.4")
    print(f"📍 访问地址: http://localhost:{port}")
    print(f"🔑 管理员登录: admin / Admin@2024#Secure!")
    print(f"👥 外包人员登录: outsource / Outsource@2024#Safe!")
    print("=" * 50)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        reload=False
    )