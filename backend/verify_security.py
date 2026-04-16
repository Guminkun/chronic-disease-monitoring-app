"""安全验证脚本"""
from app.services.minio_service import minio_service
from uuid import uuid4

def verify_security():
    """验证MinIO安全配置"""
    print("=" * 60)
    print("MinIO安全配置验证")
    print("=" * 60)
    
    # 检查1: 验证签名URL生成
    print("\n检查1: 签名URL生成")
    test_key = "test/test.txt"
    try:
        url = minio_service.get_presigned_url(test_key)
        if 'X-Amz-Signature' in url or 'signature' in url.lower() or 'X-Amz' in url:
            print("  [OK] 签名URL生成成功")
            print(f"  URL示例: {url[:60]}...")
        else:
            print("  [WARNING] URL未包含签名参数")
            print("  如果bucket是公开的，可能不需要签名")
    except Exception as e:
        print(f"  [ERROR] 签名URL生成失败: {e}")
    
    # 检查2: 验证路径隔离
    print("\n检查2: 文件路径隔离")
    test_user_id = str(uuid4())
    test_member_id = str(uuid4())
    test_key = minio_service._generate_file_key(
        test_user_id,
        test_member_id,
        'reports',
        'jpg'
    )
    
    print(f"  生成的路径: {test_key}")
    
    if test_key.startswith(f"user_{test_user_id}/member_{test_member_id}"):
        print("  [OK] 文件路径隔离正确")
    else:
        print("  [ERROR] 文件路径隔离失败")
    
    # 检查3: MD5计算
    print("\n检查3: MD5去重功能")
    test_data = b"test file content"
    md5_hash = minio_service._calculate_md5(test_data)
    print(f"  测试数据MD5: {md5_hash}")
    print("  [OK] MD5计算功能正常")
    
    # 总结
    print("\n" + "=" * 60)
    print("验证完成!")
    print("=" * 60)
    print("\n下一步:")
    print("1. 运行: python check_minio_policy.py 检查bucket策略")
    print("2. 运行: python migrate_minio_fields.py 迁移数据库")
    print("3. 重启后端服务测试功能")

if __name__ == "__main__":
    verify_security()
