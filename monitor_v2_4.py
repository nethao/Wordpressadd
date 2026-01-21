#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WordPress 软文发布中间件 V2.4 性能监控脚本
监控系统运行状态和性能指标
"""

import time
import json
import psutil
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any
from pathlib import Path

class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.metrics_file = Path("metrics_v2_4.json")
        self.alert_thresholds = {
            "cpu_percent": 80.0,
            "memory_percent": 85.0,
            "response_time": 2.0,  # 秒
            "error_rate": 5.0,     # 百分比
            "disk_usage": 90.0     # 百分比
        }
        
    def get_system_metrics(self) -> Dict[str, Any]:
        """获取系统指标"""
        try:
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # 内存使用率
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # 磁盘使用率
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            
            # 网络统计
            network = psutil.net_io_counters()
            
            return {
                "timestamp": datetime.now().isoformat(),
                "cpu_percent": cpu_percent,
                "memory_percent": memory_percent,
                "memory_available_gb": memory.available / (1024**3),
                "disk_percent": disk_percent,
                "disk_free_gb": disk.free / (1024**3),
                "network_bytes_sent": network.bytes_sent,
                "network_bytes_recv": network.bytes_recv
            }
        except Exception as e:
            print(f"获取系统指标失败: {e}")
            return {}
    
    def get_app_metrics(self) -> Dict[str, Any]:
        """获取应用指标"""
        try:
            # 健康检查
            start_time = time.time()
            response = requests.get(f"{self.base_url}/health", timeout=5)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                health_data = response.json()
                return {
                    "timestamp": datetime.now().isoformat(),
                    "status": "healthy",
                    "response_time": response_time,
                    "version": health_data.get("version", "unknown"),
                    "active_sessions": health_data.get("active_sessions", 0),
                    "ai_check_enabled": health_data.get("ai_check_enabled", False)
                }
            else:
                return {
                    "timestamp": datetime.now().isoformat(),
                    "status": "unhealthy",
                    "response_time": response_time,
                    "status_code": response.status_code
                }
                
        except requests.exceptions.RequestException as e:
            return {
                "timestamp": datetime.now().isoformat(),
                "status": "error",
                "error": str(e)
            }
    
    def test_api_endpoints(self) -> Dict[str, Any]:
        """测试API端点"""
        endpoints = [
            ("/health", "GET"),
            ("/api/info", "GET"),
            ("/login", "GET")
        ]
        
        results = {}
        
        for endpoint, method in endpoints:
            try:
                start_time = time.time()
                
                if method == "GET":
                    response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                else:
                    response = requests.post(f"{self.base_url}{endpoint}", timeout=5)
                    
                response_time = time.time() - start_time
                
                results[endpoint] = {
                    "status_code": response.status_code,
                    "response_time": response_time,
                    "success": response.status_code < 400
                }
                
            except Exception as e:
                results[endpoint] = {
                    "error": str(e),
                    "success": False
                }
                
        return results
    
    def calculate_availability(self, hours: int = 24) -> float:
        """计算可用性"""
        if not self.metrics_file.exists():
            return 0.0
            
        try:
            with open(self.metrics_file, 'r', encoding='utf-8') as f:
                metrics = json.load(f)
                
            cutoff_time = datetime.now() - timedelta(hours=hours)
            recent_metrics = [
                m for m in metrics 
                if datetime.fromisoformat(m.get("timestamp", "")) > cutoff_time
            ]
            
            if not recent_metrics:
                return 0.0
                
            healthy_count = sum(
                1 for m in recent_metrics 
                if m.get("app_metrics", {}).get("status") == "healthy"
            )
            
            return (healthy_count / len(recent_metrics)) * 100
            
        except Exception as e:
            print(f"计算可用性失败: {e}")
            return 0.0
    
    def check_alerts(self, system_metrics: Dict, app_metrics: Dict) -> List[str]:
        """检查告警条件"""
        alerts = []
        
        # 系统资源告警
        if system_metrics.get("cpu_percent", 0) > self.alert_thresholds["cpu_percent"]:
            alerts.append(f"CPU使用率过高: {system_metrics['cpu_percent']:.1f}%")
            
        if system_metrics.get("memory_percent", 0) > self.alert_thresholds["memory_percent"]:
            alerts.append(f"内存使用率过高: {system_metrics['memory_percent']:.1f}%")
            
        if system_metrics.get("disk_percent", 0) > self.alert_thresholds["disk_usage"]:
            alerts.append(f"磁盘使用率过高: {system_metrics['disk_percent']:.1f}%")
            
        # 应用性能告警
        if app_metrics.get("response_time", 0) > self.alert_thresholds["response_time"]:
            alerts.append(f"响应时间过长: {app_metrics['response_time']:.2f}秒")
            
        if app_metrics.get("status") != "healthy":
            alerts.append(f"应用状态异常: {app_metrics.get('status', 'unknown')}")
            
        return alerts
    
    def save_metrics(self, metrics: Dict[str, Any]):
        """保存指标数据"""
        try:
            # 读取现有数据
            if self.metrics_file.exists():
                with open(self.metrics_file, 'r', encoding='utf-8') as f:
                    all_metrics = json.load(f)
            else:
                all_metrics = []
                
            # 添加新指标
            all_metrics.append(metrics)
            
            # 只保留最近7天的数据
            cutoff_time = datetime.now() - timedelta(days=7)
            all_metrics = [
                m for m in all_metrics 
                if datetime.fromisoformat(m.get("timestamp", "")) > cutoff_time
            ]
            
            # 保存数据
            with open(self.metrics_file, 'w', encoding='utf-8') as f:
                json.dump(all_metrics, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"保存指标失败: {e}")
    
    def generate_report(self) -> Dict[str, Any]:
        """生成监控报告"""
        system_metrics = self.get_system_metrics()
        app_metrics = self.get_app_metrics()
        api_results = self.test_api_endpoints()
        availability = self.calculate_availability()
        alerts = self.check_alerts(system_metrics, app_metrics)
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "system_metrics": system_metrics,
            "app_metrics": app_metrics,
            "api_endpoints": api_results,
            "availability_24h": availability,
            "alerts": alerts,
            "summary": {
                "status": "healthy" if not alerts else "warning",
                "total_alerts": len(alerts),
                "api_success_rate": sum(
                    1 for r in api_results.values() if r.get("success", False)
                ) / len(api_results) * 100 if api_results else 0
            }
        }
        
        return report
    
    def print_report(self, report: Dict[str, Any]):
        """打印监控报告"""
        print("📊 WordPress发布系统V2.4 - 性能监控报告")
        print("=" * 60)
        print(f"时间: {report['timestamp']}")
        print()
        
        # 系统指标
        sys_metrics = report.get("system_metrics", {})
        if sys_metrics:
            print("🖥️ 系统指标:")
            print(f"  CPU使用率: {sys_metrics.get('cpu_percent', 0):.1f}%")
            print(f"  内存使用率: {sys_metrics.get('memory_percent', 0):.1f}%")
            print(f"  可用内存: {sys_metrics.get('memory_available_gb', 0):.1f}GB")
            print(f"  磁盘使用率: {sys_metrics.get('disk_percent', 0):.1f}%")
            print(f"  可用磁盘: {sys_metrics.get('disk_free_gb', 0):.1f}GB")
            print()
        
        # 应用指标
        app_metrics = report.get("app_metrics", {})
        if app_metrics:
            print("🚀 应用指标:")
            print(f"  状态: {app_metrics.get('status', 'unknown')}")
            print(f"  响应时间: {app_metrics.get('response_time', 0):.3f}秒")
            print(f"  版本: {app_metrics.get('version', 'unknown')}")
            print(f"  活跃会话: {app_metrics.get('active_sessions', 0)}")
            print(f"  AI审核: {'启用' if app_metrics.get('ai_check_enabled') else '禁用'}")
            print()
        
        # API端点测试
        api_results = report.get("api_endpoints", {})
        if api_results:
            print("🔗 API端点测试:")
            for endpoint, result in api_results.items():
                status = "✅" if result.get("success") else "❌"
                time_info = f"({result.get('response_time', 0):.3f}s)" if 'response_time' in result else ""
                print(f"  {status} {endpoint} {time_info}")
            print()
        
        # 可用性
        availability = report.get("availability_24h", 0)
        print(f"📈 24小时可用性: {availability:.2f}%")
        print()
        
        # 告警
        alerts = report.get("alerts", [])
        if alerts:
            print("🚨 告警信息:")
            for alert in alerts:
                print(f"  ⚠️ {alert}")
        else:
            print("✅ 无告警信息")
        
        print("=" * 60)
    
    def run_monitoring(self, interval: int = 60, duration: int = 0):
        """运行持续监控"""
        print(f"🔄 开始监控 (间隔: {interval}秒)")
        
        start_time = time.time()
        
        try:
            while True:
                # 生成报告
                report = self.generate_report()
                
                # 保存指标
                self.save_metrics(report)
                
                # 打印报告
                self.print_report(report)
                
                # 检查是否需要停止
                if duration > 0 and (time.time() - start_time) >= duration:
                    break
                    
                # 等待下次监控
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n⏹️ 监控被用户中断")
    
    def run_single_check(self):
        """运行单次检查"""
        report = self.generate_report()
        self.save_metrics(report)
        self.print_report(report)
        return report

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="WordPress发布系统V2.4性能监控")
    parser.add_argument("--url", default="http://localhost:8001", help="应用URL")
    parser.add_argument("--interval", type=int, default=60, help="监控间隔(秒)")
    parser.add_argument("--duration", type=int, default=0, help="监控持续时间(秒)，0表示持续监控")
    parser.add_argument("--single", action="store_true", help="运行单次检查")
    
    args = parser.parse_args()
    
    monitor = PerformanceMonitor(args.url)
    
    try:
        if args.single:
            monitor.run_single_check()
        else:
            monitor.run_monitoring(args.interval, args.duration)
    except Exception as e:
        print(f"❌ 监控失败: {e}")

if __name__ == "__main__":
    main()