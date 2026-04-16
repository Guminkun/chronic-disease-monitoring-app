"""
MinIO Bucket策略检查和配置工具

用途：
1. 检查现有bucket的访问策略
2. 配置生产安全的自定义策略
3. 验证策略是否正确

使用方法：
python check_minio_policy.py
"""
from minio import Minio
from minio.error import S3Error
from app.config import settings
import json


def check_bucket_policy(client: Minio, bucket_name: str):
    """检查bucket的访问策略"""
    print(f"\n检查 bucket: {bucket_name}")
    print("-" * 60)
    
    try:
        # 检查bucket是否存在
        if not client.bucket_exists(bucket_name):
            print(f"  [X] Bucket不存在")
            return False
        
        print(f"  [OK] Bucket存在")
        
        # 获取bucket策略
        try:
            policy = client.get_bucket_policy(bucket_name)
            policy_dict = json.loads(policy)
            
            print(f"  [INFO] 当前策略: CUSTOM")
            print(f"  策略详情:")
            
            # 解析策略
            statements = policy_dict.get('Statement', [])
            for idx, stmt in enumerate(statements, 1):
                effect = stmt.get('Effect', 'N/A')
                action = stmt.get('Action', [])
                principal = stmt.get('Principal', {})
                
                print(f"    规则 {idx}:")
                print(f"      - Effect: {effect}")
                print(f"      - Action: {action}")
                print(f"      - Principal: {principal}")
                
                # 检查是否允许公开访问
                if effect == 'Allow' and principal == {'AWS': ['*']}:
                    if 's3:GetObject' in action:
                        print(f"      [WARNING] 允许公开读取!")
                    if 's3:PutObject' in action:
                        print(f"      [WARNING] 允许公开写入!")
            
            return True
            
        except Exception as e:
            # 如果没有策略，说明是私有bucket
            if "NoSuchBucketPolicy" in str(e):
                print(f"  [INFO] 当前策略: PRIVATE (无策略)")
                print(f"  [OK] 完全私有，需要签名URL访问")
                return True
            else:
                print(f"  [X] 获取策略失败: {e}")
                return False
                
    except S3Error as e:
        print(f"  [X] S3错误: {e}")
        return False


def set_secure_policy(client: Minio, bucket_name: str):
    """
    设置安全的自定义策略
    
    生产安全策略：
    1. 只允许经过身份验证的用户访问
    2. 文件访问需要签名URL
    3. 不允许匿名访问
    """
    print(f"\n配置安全策略 for bucket: {bucket_name}")
    print("-" * 60)
    
    # 生产安全的策略：不允许任何公开访问
    # 所有访问都必须通过签名URL
    policy = {
        "Version": "2012-10-17",
        "Statement": []
    }
    
    try:
        # 设置空策略 = 完全私有
        client.set_bucket_policy(bucket_name, json.dumps(policy))
        print(f"  [OK] 已设置为完全私有策略")
        print(f"  [INFO] 所有访问需要签名URL")
        return True
    except Exception as e:
        print(f"  [X] 设置策略失败: {e}")
        return False


def verify_presigned_url(client: Minio, bucket_name: str):
    """验证签名URL功能"""
    print(f"\n验证签名URL功能 for bucket: {bucket_name}")
    print("-" * 60)
    
    try:
        # 测试生成签名URL
        test_key = "test/test.txt"
        url = client.presigned_get_object(
            bucket_name,
            test_key,
            expires=datetime.timedelta(seconds=600)
        )
        
        print(f"  [OK] 签名URL生成成功")
        print(f"  URL示例: {url[:80]}...")
        print(f"  有效期: 10分钟")
        return True
        
    except Exception as e:
        print(f"  [X] 签名URL生成失败: {e}")
        return False


def main():
    print("=" * 60)
    print("MinIO Bucket策略检查工具")
    print("=" * 60)
    
    # 创建MinIO客户端
    endpoint = settings.MINIO_ENDPOINT
    if endpoint.startswith("http://"):
        endpoint = endpoint.replace("http://", "")
    elif endpoint.startswith("https://"):
        endpoint = endpoint.replace("https://", "")
    
    client = Minio(
        endpoint,
        access_key=settings.MINIO_ACCESS_KEY,
        secret_key=settings.MINIO_SECRET_KEY,
        secure=settings.MINIO_SECURE,
        region="cn-north-1"
    )
    
    # 要检查的bucket列表
    buckets = [
        settings.MINIO_BUCKET_NAME or "binli",
        settings.MINIO_BUCKET_REPORT or "jianchabaogao",
        "avatars",
        "usageguides"
    ]
    
    print(f"\nMinIO服务器: {endpoint}")
    print(f"待检查的bucket: {', '.join(buckets)}")
    
    # 检查所有bucket
    results = {}
    for bucket in buckets:
        results[bucket] = check_bucket_policy(client, bucket)
    
    # 总结
    print("\n" + "=" * 60)
    print("检查结果总结")
    print("=" * 60)
    
    all_ok = all(results.values())
    
    for bucket, ok in results.items():
        status = "[OK]" if ok else "[X]"
        print(f"{status} {bucket}")
    
    if all_ok:
        print("\n[OK] 所有bucket检查通过!")
        print("\n下一步:")
        print("1. 如果bucket是PRIVATE或空策略, 访问需要签名URL")
        print("2. 如果bucket是CUSTOM, 确保策略不允许公开访问")
        print("3. 运行后端服务测试签名URL功能")
    else:
        print("\n[X] 部分bucket存在问题!")
        print("\n建议:")
        print("1. 检查bucket是否存在")
        print("2. 检查MinIO连接配置")
        print("3. 检查访问密钥权限")
    
    # 询问是否配置安全策略
    print("\n" + "=" * 60)
    response = input("是否要配置安全策略？(y/n): ").strip().lower()
    
    if response == 'y':
        print("\n选择操作:")
        print("1. 设置为完全私有（推荐）")
        print("2. 保持当前CUSTOM策略")
        print("3. 退出")
        
        choice = input("请选择 (1/2/3): ").strip()
        
        if choice == '1':
            for bucket in buckets:
                if results.get(bucket, False):
                    set_secure_policy(client, bucket)
            
            print("\n[OK] 安全策略配置完成!")
            print("所有bucket已设置为完全私有，访问需要签名URL。")
            
        elif choice == '2':
            print("\n[OK] 保持当前CUSTOM策略")
            print("请确保当前策略不允许公开访问。")
        else:
            print("\n已退出")


if __name__ == "__main__":
    import datetime
    main()
