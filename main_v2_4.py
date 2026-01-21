#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WordPress 软文发布中间件 V2.3
Web UI 深度重构与功能增强
集成多角色登录系统和本月发布统计功能
"""

import os
import json
import time
import base64
import asyncio
import aiohttp
import urllib3
import secrets
from typing import Dict, Any, Optional
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

# 禁用SSL警告（本地测试环境）
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 加载环境变量
load_dotenv()

app = FastAPI(
    title="文章发布系统 V2.3",
    description="Web UI深度重构版本，集成本月发布统计和极简布局设计",
    version="2.3.0"
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

# 配置管理模型
class ConfigRequest(BaseModel):
    wp_username: Optional[str] = None
    wp_app_password: Optional[str] = None
    wp_domain: Optional[str] = None
    baidu_api_key: Optional[str] = None
    baidu_secret_key: Optional[str] = None
    client_auth_token: Optional[str] = None
    test_mode: Optional[bool] = None

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
    """百度AI内容审核客户端 - 增强版"""
    
    def __init__(self):
        self.api_key = os.getenv("BAIDU_API_KEY")
        self.secret_key = os.getenv("BAIDU_SECRET_KEY")
        self.access_token = None
        self.token_expires_at = None
        self.test_mode = os.getenv("TEST_MODE", "false").lower() == "true"
        
        if not self.test_mode and (not self.api_key or not self.secret_key):
            raise ValueError("百度AI API密钥未配置")
    
    async def get_access_token(self, force_refresh: bool = False) -> str:
        """获取百度AI访问令牌，支持自动刷新"""
        # 检查是否需要刷新token
        if (not force_refresh and self.access_token and self.token_expires_at and 
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
                async with session.post(url, params=params, timeout=15, ssl=False) as response:
                    if response.status == 200:
                        data = await response.json()
                        if "access_token" in data:
                            self.access_token = data["access_token"]
                            # 设置过期时间（提前10分钟刷新）
                            expires_in = data.get("expires_in", 2592000)  # 默认30天
                            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 600)
                            return self.access_token
                        else:
                            raise HTTPException(
                                status_code=500, 
                                detail=f"百度AI Token获取失败: {data.get('error_description', '未知错误')}"
                            )
                    else:
                        error_text = await response.text()
                        raise HTTPException(
                            status_code=500, 
                            detail=f"百度AI Token请求失败: HTTP {response.status} - {error_text}"
                        )
            except asyncio.TimeoutError:
                raise HTTPException(status_code=500, detail="百度AI Token获取超时")
            except Exception as e:
                if not isinstance(e, HTTPException):
                    raise HTTPException(status_code=500, detail=f"百度AI Token获取异常: {str(e)}")
                raise
    
    async def text_audit(self, text: str, retry_count: int = 1) -> Dict[str, Any]:
        """文本内容审核 - 增强容错"""
        # 测试模式：模拟审核结果
        if self.test_mode:
            # 检查是否包含测试敏感词
            sensitive_words = ["测试敏感词", "违规内容", "政治敏感", "敏感", "违法"]
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
        
        # 正常模式：调用百度API
        try:
            access_token = await self.get_access_token()
        except Exception as e:
            # Token获取失败，尝试强制刷新一次
            if retry_count > 0:
                try:
                    access_token = await self.get_access_token(force_refresh=True)
                except Exception:
                    raise HTTPException(
                        status_code=500, 
                        detail="百度AI访问令牌获取失败，请检查API密钥配置"
                    )
            else:
                raise HTTPException(status_code=500, detail=f"百度AI认证失败: {str(e)}")
        
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
                async with session.post(url, headers=headers, data=data, timeout=30, ssl=False) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        # 处理违规信息
                        if result.get("conclusionType") == 2 and "data" in result:
                            violations = []
                            for item in result["data"]:
                                if "hits" in item:
                                    for hit in item["hits"]:
                                        violations.append({
                                            "违规词汇": hit.get("words", []),
                                            "违规类型": item.get("subType", "未知"),
                                            "违规描述": item.get("msg", "")
                                        })
                            result["violations"] = violations
                        
                        return result
                    elif response.status == 401:
                        # Token过期，尝试刷新
                        if retry_count > 0:
                            return await self.text_audit(text, retry_count - 1)
                        else:
                            raise HTTPException(status_code=500, detail="百度AI访问令牌已过期")
                    else:
                        error_text = await response.text()
                        raise HTTPException(
                            status_code=500, 
                            detail=f"百度AI审核服务错误: HTTP {response.status} - {error_text}"
                        )
            except asyncio.TimeoutError:
                raise HTTPException(status_code=500, detail="百度AI审核服务超时")
            except Exception as e:
                if not isinstance(e, HTTPException):
                    raise HTTPException(status_code=500, detail=f"百度AI审核异常: {str(e)}")
                raise

class WordPressClient:
    """WordPress REST API客户端 - V2.3版本"""
    
    def __init__(self):
        self.wp_domain = os.getenv("WP_DOMAIN")
        self.wp_username = os.getenv("WP_USERNAME")
        self.wp_app_password = os.getenv("WP_APP_PASSWORD")
        self.test_mode = os.getenv("TEST_MODE", "false").lower() == "true"
        
        if not self.test_mode and not all([self.wp_domain, self.wp_username, self.wp_app_password]):
            raise ValueError("WordPress配置信息不完整")
        
        if not self.test_mode:
            # 处理域名格式 - 移除协议前缀
            domain = self.wp_domain
            if domain.startswith('http://'):
                domain = domain[7:]
            elif domain.startswith('https://'):
                domain = domain[8:]
            
            # 移除末尾的斜杠
            domain = domain.rstrip('/')
            
            # 构建API基础URL - 根据域名判断协议
            if '192.168.' in domain or 'localhost' in domain or domain.startswith('127.'):
                # 本地环境使用HTTP
                self.api_base = f"http://{domain}/wp-json/wp/v2"
            else:
                # 生产环境使用HTTPS
                self.api_base = f"https://{domain}/wp-json/wp/v2"
            
            # 构建Basic Auth头
            credentials = f"{self.wp_username}:{self.wp_app_password}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()
            self.auth_header = f"Basic {encoded_credentials}"
    
    async def get_monthly_published_count(self) -> int:
        """获取本月已发布的文章数量"""
        # 测试模式：返回模拟数据
        if self.test_mode:
            return 42  # 模拟本月发布了42篇文章
        
        # 计算本月的开始和结束时间
        now = datetime.now()
        month_start = datetime(now.year, now.month, 1)
        if now.month == 12:
            month_end = datetime(now.year + 1, 1, 1)
        else:
            month_end = datetime(now.year, now.month + 1, 1)
        
        # 格式化为ISO字符串
        after = month_start.isoformat()
        before = month_end.isoformat()
        
        # 构建认证头
        credentials = f"{self.wp_username}:{self.wp_app_password}"
        credentials_clean = credentials.strip()
        encoded_credentials = base64.b64encode(credentials_clean.encode('utf-8')).decode('ascii')
        
        headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Accept": "application/json",
            "User-Agent": "WordPress-Publisher-V2.3"
        }
        
        # 尝试多个端点
        endpoints_to_try = [
            f"{self.api_base}/adv_posts",  # 自定义端点
            f"{self.api_base}/posts"       # 标准端点（备用）
        ]
        
        for i, base_url in enumerate(endpoints_to_try):
            endpoint_name = "自定义端点(/adv_posts)" if i == 0 else "标准端点(/posts)"
            
            # 构建查询参数
            params = {
                "status": "publish",
                "after": after,
                "before": before,
                "per_page": 1,  # 只需要获取总数，不需要内容
                "_fields": "id"  # 只返回ID字段，减少数据传输
            }
            
            url = f"{base_url}?" + "&".join([f"{k}={v}" for k, v in params.items()])
            
            print(f"🔍 查询{endpoint_name}本月发布数: {url}")
            
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(
                        url,
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=30),
                        ssl=False
                    ) as response:
                        print(f"📊 {endpoint_name}响应状态: {response.status}")
                        
                        if response.status == 200:
                            # 从响应头获取总数
                            total_header = response.headers.get('X-WP-Total', '0')
                            try:
                                total_count = int(total_header)
                                print(f"✅ {endpoint_name}查询成功，本月发布: {total_count} 篇")
                                return total_count
                            except ValueError:
                                print(f"⚠️ {endpoint_name}总数解析失败: {total_header}")
                                # 尝试解析响应体
                                try:
                                    data = await response.json()
                                    return len(data) if isinstance(data, list) else 0
                                except:
                                    return 0
                        elif response.status == 500 and i == 0:
                            # 自定义端点500错误，尝试标准端点
                            print(f"⚠️ {endpoint_name}遇到错误，尝试标准端点...")
                            continue
                        else:
                            error_text = await response.text()
                            print(f"❌ {endpoint_name}查询失败: HTTP {response.status} - {error_text[:200]}...")
                            if i == len(endpoints_to_try) - 1:  # 最后一个端点也失败了
                                return 0
                            continue
                            
                except asyncio.TimeoutError:
                    print(f"❌ {endpoint_name}查询超时")
                    if i == len(endpoints_to_try) - 1:
                        return 0
                    continue
                except Exception as e:
                    print(f"❌ {endpoint_name}查询异常: {str(e)}")
                    if i == len(endpoints_to_try) - 1:
                        return 0
                    continue
        
        # 所有端点都失败了
        return 0
    
    async def create_post(self, title: str, content: str) -> Dict[str, Any]:
        """创建WordPress文章 - 适配V2.3版本"""
        # 测试模式：模拟发布结果
        if self.test_mode:
            return {
                "id": 12345,
                "title": {"rendered": title},
                "content": {"rendered": content},
                "status": "pending",
                "date": datetime.now().isoformat(),
                "link": f"https://test-domain.com/adv_posts/12345"
            }
        
        # 正常模式：先尝试自定义端点，失败则使用标准端点
        endpoints_to_try = [
            f"{self.api_base}/adv_posts",  # 自定义端点
            f"{self.api_base}/posts"       # 标准端点（备用）
        ]
        
        # 重新构建认证头，确保格式正确
        credentials = f"{self.wp_username}:{self.wp_app_password}"
        credentials_clean = credentials.strip()
        encoded_credentials = base64.b64encode(credentials_clean.encode('utf-8')).decode('ascii')
        
        headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "WordPress-Publisher-V2.3"
        }
        
        # 构建文章数据
        post_data = {
            "title": title,
            "content": content,
            "status": "pending",  # 强制设为待审核
            "date": datetime.now().isoformat(),
            "author": 1  # 默认作者ID
        }
        
        last_error = None
        
        for i, url in enumerate(endpoints_to_try):
            endpoint_name = "自定义端点(/adv_posts)" if i == 0 else "标准端点(/posts)"
            print(f"🔍 尝试{endpoint_name}: {url}")
            
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.post(
                        url, 
                        headers=headers, 
                        json=post_data, 
                        timeout=aiohttp.ClientTimeout(total=60),
                        ssl=False
                    ) as response:
                        response_text = await response.text()
                        print(f"📊 {endpoint_name}响应状态: {response.status}")
                        
                        if response.status in [200, 201]:
                            try:
                                result = await response.json()
                                print(f"✅ {endpoint_name}发布成功！")
                                return result
                            except:
                                return {
                                    "id": "unknown",
                                    "title": {"rendered": title},
                                    "status": "pending",
                                    "message": f"通过{endpoint_name}发布成功"
                                }
                        elif response.status == 500 and i == 0:
                            # 自定义端点500错误，尝试标准端点
                            print(f"⚠️ {endpoint_name}遇到插件错误，尝试标准端点...")
                            last_error = f"{endpoint_name}插件错误: {response_text[:200]}..."
                            continue
                        elif response.status == 401:
                            # 认证错误，不需要尝试其他端点
                            try:
                                error_data = await response.json()
                                error_message = error_data.get('message', '认证失败')
                                if '\\u' in error_message:
                                    error_message = error_message.encode().decode('unicode_escape')
                            except:
                                error_message = "WordPress认证失败，请检查用户名和应用密码"
                            
                            raise HTTPException(
                                status_code=401,
                                detail=f"WordPress认证错误: {error_message}"
                            )
                        else:
                            last_error = f"{endpoint_name}错误: HTTP {response.status} - {response_text[:200]}..."
                            if i == len(endpoints_to_try) - 1:  # 最后一个端点也失败了
                                raise HTTPException(
                                    status_code=response.status,
                                    detail=last_error
                                )
                            continue
                            
                except asyncio.TimeoutError:
                    last_error = f"{endpoint_name}连接超时"
                    if i == len(endpoints_to_try) - 1:
                        raise HTTPException(status_code=500, detail="WordPress服务连接超时")
                    continue
                except aiohttp.ClientError as e:
                    last_error = f"{endpoint_name}连接错误: {str(e)}"
                    if i == len(endpoints_to_try) - 1:
                        raise HTTPException(status_code=500, detail=last_error)
                    continue
                except Exception as e:
                    if isinstance(e, HTTPException):
                        raise
                    last_error = f"{endpoint_name}异常: {str(e)}"
                    if i == len(endpoints_to_try) - 1:
                        raise HTTPException(status_code=500, detail=last_error)
                    continue
        
        # 如果所有端点都失败了
        raise HTTPException(status_code=500, detail=f"所有WordPress端点都失败: {last_error}")

# 初始化客户端
baidu_client = BaiduAIClient()
wp_client = WordPressClient()

def verify_client_auth() -> bool:
    """验证外包身份令牌（从配置中获取）"""
    client_auth_token = os.getenv("CLIENT_AUTH_TOKEN")
    if not client_auth_token:
        raise HTTPException(status_code=500, detail="服务器未配置客户端认证令牌")
    
    # 在实际部署中，这里可以添加更复杂的验证逻辑
    # 比如检查IP白名单、时间戳验证等
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
        
        # 设置Cookie
        response.set_cookie(
            key="session_id",
            value=session_id,
            max_age=24 * 60 * 60,  # 24小时
            httponly=True,
            secure=False,  # 本地测试环境设为False
            samesite="lax"
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
    """获取本月发布统计 - V2.3新增"""
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

@app.post("/publish", response_model=PublishResponse)
async def publish_article(request: PublishRequest, current_user: Dict[str, Any] = Depends(require_login)):
    """
    发布文章接口 - V2.3版本
    1. 验证用户登录状态
    2. 百度AI内容审核
    3. 发布到WordPress（自动分类）
    """
    
    try:
        # 1. 用户已通过依赖注入验证登录状态
        print(f"📝 用户 {current_user['username']} ({current_user['role']}) 正在发布文章: {request.title}")
        
        # 2. 验证外包身份（保持向后兼容）
        if not verify_client_auth():
            return PublishResponse(
                status="error",
                message="身份验证失败：系统配置错误"
            )
        
        # 3. 百度AI内容审核
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
        
        # 4. 审核通过，发布到WordPress
        wp_result = await wp_client.create_post(request.title, request.content)
        
        return PublishResponse(
            status="success",
            message="文章发布成功，已提交待审核队列",
            post_id=wp_result.get("id"),
            audit_result={
                "conclusion_type": conclusion_type,
                "message": "内容审核通过"
            }
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
            message=f"服务器内部错误: {str(e)}"
        )

@app.get("/config")
async def get_config(current_user: Dict[str, Any] = Depends(require_admin)):
    """获取当前配置信息（脱敏） - 需要管理员权限"""
    try:
        config = {
            "wp_domain": os.getenv("WP_DOMAIN", ""),
            "wp_username": os.getenv("WP_USERNAME", ""),
            "wp_app_password": "***" if os.getenv("WP_APP_PASSWORD") else "",
            "baidu_api_key": "***" if os.getenv("BAIDU_API_KEY") else "",
            "baidu_secret_key": "***" if os.getenv("BAIDU_SECRET_KEY") else "",
            "client_auth_token": "***" if os.getenv("CLIENT_AUTH_TOKEN") else "",
            "test_mode": os.getenv("TEST_MODE", "false").lower() == "true",
            "port": os.getenv("PORT", "8001")
        }
        
        return ConfigResponse(
            status="success",
            message="配置信息获取成功",
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
        
        # 重新加载环境变量
        load_dotenv(override=True)
        
        # 重新初始化客户端
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

@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "文章发布系统 V2.3",
        "version": "2.3.0",
        "active_sessions": len(SESSIONS)
    }

@app.get("/api/info")
async def api_info():
    """API信息接口"""
    return {
        "service": "文章发布系统 V2.3",
        "version": "2.3.0",
        "endpoints": {
            "用户登录": "POST /login",
            "用户登出": "POST /logout",
            "发布文章": "POST /publish",
            "本月统计": "GET /api/stats/monthly",
            "获取配置": "GET /config",
            "更新配置": "POST /config",
            "用户信息": "GET /api/user",
            "健康检查": "GET /health",
            "API文档": "GET /docs"
        },
        "features": [
            "Web UI深度重构与极简布局",
            "本月发布统计功能",
            "多角色登录系统（管理员 vs 外包人员）",
            "基于Session的身份认证",
            "路由权限控制",
            "适配WordPress插件V2.1版本",
            "自动文章分类（插件处理）",
            "百度AI内容审核",
            "增强容错机制",
            "本地测试环境优化",
            "配置管理界面"
        ]
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
    # 启动服务
    uvicorn.run(
        "main_v2_3:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8001)),
        reload=os.getenv("DEBUG", "false").lower() == "true"
    )