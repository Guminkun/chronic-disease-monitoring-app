"""
测试微信登录功能（模拟测试）
"""
import httpx
import asyncio

async def test_wechat_login():
    print("测试微信登录功能...")
    print("\n1. 测试未配置微信凭证的情况")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "http://localhost:8000/auth/wechat/login",
                json={"code": "test_code"}
            )
            print(f"响应状态: {response.status_code}")
            print(f"响应内容: {response.json()}")
        except Exception as e:
            print(f"错误: {e}")
    
    print("\n" + "="*50)
    print("\n配置说明:")
    print("1. 在 backend/.env 文件中添加:")
    print("   WECHAT_APPID=你的微信小程序AppID")
    print("   WECHAT_SECRET=你的微信小程序AppSecret")
    print("\n2. 重启后端服务")
    print("\n3. 在微信开发者工具中运行小程序")
    print("\n4. 点击微信登录按钮测试")

if __name__ == "__main__":
    asyncio.run(test_wechat_login())
