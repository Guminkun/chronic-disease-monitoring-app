# MinIO CUSTOM策略部署指南

## 当前环境状态

您的MinIO bucket已存在，权限设置为 **CUSTOM（自定义策略）**。

## CUSTOM策略说明

### 什么是CUSTOM策略？

CUSTOM策略表示bucket使用了自定义的访问控制策略，这是生产环境最灵活的方式。常见的CUSTOM策略配置：

1. **完全私有** - 最安全，所有访问都需要签名URL
2. **条件公开** - 允许特定条件下公开访问（如特定前缀）
3. **混合模式** - 部分公开，部分私有

### 生产安全要求

**关键原则：所有用户上传的医疗文件必须私有访问**

✅ **正确配置**:
- 用户上传的检查报告、病历、头像 - 必须私有
- 访问需要后端生成签名URL
- 验证用户权限后才返回URL

❌ **错误配置**:
- 允许匿名用户访问所有文件
- 允许公开下载 (`s3:GetObject` for `Principal: *`)
- 文件URL永久有效

## 步骤1: 检查当前策略

运行策略检查工具：

```bash
cd backend
python check_minio_policy.py
```

该工具会显示：
- 每个bucket的当前策略
- 是否允许公开访问
- 策略详情

## 步骤2: 配置安全策略（如需要）

### 方式1: 使用检查工具配置

运行 `check_minio_policy.py`，选择"设置为完全私有"。

### 方式2: 使用MinIO控制台

1. 访问 MinIO 控制台: http://192.168.88.205:9000
2. 登录: admin / Psbc@1234
3. 进入 Buckets → 选择bucket → Access
4. 点击 "Edit Policy"
5. 删除所有允许 `Principal: *` 的规则
6. 保存

### 方式3: 使用mc命令行

```bash
# 设置为完全私有（推荐）
mc anonymous set none myminio/binli
mc anonymous set none myminio/jianchabaogao
mc anonymous set none myminio/avatars
mc anonymous set none myminio/usageguides
```

## 步骤3: 验证配置

### 检查清单

- [ ] 运行 `check_minio_policy.py`，确认所有bucket不允许公开访问
- [ ] 测试上传文件，确认存储路径格式正确
- [ ] 测试获取签名URL，确认10分钟后过期
- [ ] 测试访问其他用户文件，确认返回403

### 测试命令

```bash
# 测试签名URL生成
python -c "
from app.services.minio_service import minio_service
url = minio_service.get_presigned_url('test/test.txt')
print('签名URL生成成功:', url[:50] + '...')
"
```

## 步骤4: 运行数据库迁移

```bash
cd backend
python migrate_minio_fields.py
```

## 步骤5: 安装依赖

```bash
pip install Pillow
```

## 步骤6: 重启服务

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 常见CUSTOM策略示例

### 示例1: 完全私有（推荐）

```json
{
  "Version": "2012-10-17",
  "Statement": []
}
```

**效果**: 所有访问都需要签名URL

### 示例2: 允许特定前缀公开

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {"AWS": ["*"]},
      "Action": ["s3:GetObject"],
      "Resource": ["arn:aws:s3:::bucket-name/public/*"]
    }
  ]
}
```

**效果**: 只有 `public/` 前缀下的文件可以公开访问

### 示例3: 只读公开（不推荐用于医疗文件）

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {"AWS": ["*"]},
      "Action": ["s3:GetObject"],
      "Resource": ["arn:aws:s3:::bucket-name/*"]
    }
  ]
}
```

**⚠️ 警告**: 允许所有文件公开读取，不适合医疗文件！

## 安全检查脚本

创建 `verify_security.py`:

```python
"""安全验证脚本"""
from app.services.minio_service import minio_service
from app.config import settings

def verify_security():
    """验证MinIO安全配置"""
    print("验证MinIO安全配置...")
    
    # 检查1: 验证签名URL有效期
    test_key = "test/test.txt"
    try:
        url = minio_service.get_presigned_url(test_key)
        # URL应该包含签名参数
        if 'X-Amz-Signature' in url or 'signature' in url.lower():
            print("✅ 签名URL生成成功")
        else:
            print("❌ URL未包含签名，可能配置错误")
    except Exception as e:
        print(f"❌ 签名URL生成失败: {e}")
    
    # 检查2: 验证路径隔离
    from uuid import uuid4
    test_user_id = str(uuid4())
    test_member_id = str(uuid4())
    test_key = minio_service._generate_file_key(
        test_user_id,
        test_member_id,
        'reports',
        'jpg'
    )
    
    if test_key.startswith(f"user_{test_user_id}/member_{test_member_id}"):
        print("✅ 文件路径隔离正确")
    else:
        print("❌ 文件路径隔离失败")
    
    print("\n安全验证完成!")

if __name__ == "__main__":
    verify_security()
```

运行验证:
```bash
python verify_security.py
```

## 故障排查

### 问题1: 文件无法访问

**症状**: 前端显示图片加载失败

**排查步骤**:
1. 检查后端日志是否有错误
2. 检查签名URL是否正确生成
3. 检查用户是否有权限访问该文件
4. 运行 `verify_security.py` 验证配置

### 问题2: 旧URL无法访问

**症状**: 旧的上传文件URL失效

**原因**: 旧URL格式是永久有效的公开URL，现在改为私有

**解决方案**: 
- 新上传的文件会自动使用签名URL
- 旧数据可以保留，系统会自动判断URL格式

### 问题3: 上传失败

**症状**: 上传时报错"Access Denied"

**排查步骤**:
1. 检查MinIO访问密钥权限
2. 检查bucket是否存在
3. 检查网络连接

## 兼容性说明

系统会自动处理新旧两种数据格式：

```python
# 自动兼容逻辑
if image_url.startswith('http'):
    # 旧格式：永久有效的公开URL
    # 直接返回（如果bucket仍是公开的）
    return image_url
else:
    # 新格式：文件key
    # 生成临时签名URL
    return minio_service.get_presigned_url(image_url)
```

## 下一步

1. ✅ 运行 `check_minio_policy.py` 检查策略
2. ✅ 根据需要调整策略
3. ✅ 运行数据库迁移
4. ✅ 测试上传和访问功能
5. ⏳ 更新前端代码（参考 `MinIO安全升级改动总结.md`）

---

**文档版本**: v2.1  
**更新日期**: 2026-04-16  
**适用场景**: MinIO CUSTOM策略环境
