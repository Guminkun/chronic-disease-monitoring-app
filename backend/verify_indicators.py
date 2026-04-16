"""验证数据导入结果"""
from app.database import engine
from sqlalchemy import text

conn = engine.connect()

# 统计总数
result = conn.execute(text('SELECT COUNT(*) FROM indicators'))
total = result.fetchone()[0]
print(f"总记录数: {total}")

# 统计分类数
result = conn.execute(text('SELECT COUNT(DISTINCT category) FROM indicators'))
categories = result.fetchone()[0]
print(f"分类数量: {categories}")

# 各分类数量统计
result = conn.execute(text("""
    SELECT category, COUNT(*) as cnt 
    FROM indicators 
    GROUP BY category 
    ORDER BY cnt DESC
"""))

print("\n各分类数据统计:")
for row in result:
    print(f"  {row[0]}: {row[1]}条")

# 查看几条示例数据
result = conn.execute(text("""
    SELECT name, abbreviation, unit, reference_text, clinical_significance 
    FROM indicators 
    LIMIT 5
"""))

print("\n示例数据:")
for row in result:
    print(f"  名称: {row[0]}")
    print(f"  缩写: {row[1]}")
    print(f"  单位: {row[2]}")
    print(f"  参考范围: {row[3]}")
    print(f"  临床意义: {row[4]}")
    print("  ---")

conn.close()
