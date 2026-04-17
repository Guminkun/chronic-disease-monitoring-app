# 临时用药疗程天数Bug修复报告

## Bug描述

**问题：** 添加临时用药时，选择疗程天数（如5天），保存后疗程天数被强制设为1天，延期提示显示剩余0天。

**影响范围：** 所有临时用药的疗程天数设置

## Bug根源分析

### 前端问题

**文件：** `frontend-mobile/src/pages/medication/add.vue`

**问题代码：**
```typescript
const payload: medApi.MedicationPlan = {
  // ... 其他字段 ...
  duration_days: courseDays.value || undefined,  // ❌ 问题
}
```

**问题原因：**
- `courseDays` 只在手动输入疗程时更新
- 用户选择快速疗程（如5天）时，只更新了 `form.value.end_date`
- `courseDays.value` 仍然是 `null`
- 提交时 `duration_days` 是 `undefined`

### 后端问题

**文件：** `backend/app/routers/medications.py`

**问题代码：**
```python
if plan.is_temporary:
    db_plan.duration_days = 1  # ❌ 强制设为1天
    db_plan.end_date = plan.start_date  # ❌ 强制设为开始日期
    db_plan.frequency_type = "daily"
    db_plan.frequency_value = "1"
```

**问题原因：**
- 后端无条件覆盖了临时用药的 `duration_days` 和 `end_date`
- 忽略了前端传递的正确值
- 这是历史遗留代码，可能当时临时用药逻辑不完善

## 修复方案

### 前端修复

**修改文件：** `frontend-mobile/src/pages/medication/add.vue`

**修复代码：**
```typescript
const payload: medApi.MedicationPlan = {
  // ... 其他字段 ...
  duration_days: isTemporary.value 
    ? durationDays.value  // 临时用药：使用计算值
    : (courseDays.value || undefined),  // 长期用药：使用手动输入值
}
```

**说明：**
- 临时用药：使用 `durationDays`（根据 `start_date` 和 `end_date` 计算的天数）
- 长期用药：使用 `courseDays`（手动输入的疗程天数）

### 后端修复

**修改文件：** `backend/app/routers/medications.py`

**修复代码：**
```python
if plan.is_temporary:
    # 只在未设置时才使用默认值
    if not db_plan.duration_days or db_plan.duration_days < 1:
        db_plan.duration_days = 1
    if not db_plan.end_date:
        db_plan.end_date = plan.start_date
    if not db_plan.frequency_type:
        db_plan.frequency_type = "daily"
        db_plan.frequency_value = "1"
```

**说明：**
- 尊重前端传递的 `duration_days` 和 `end_date`
- 只在未设置时才使用默认值
- 保持向下兼容

## 修复前后对比

### 场景：用户添加临时用药，选择5天疗程

| 步骤 | 修复前 | 修复后 |
|------|--------|--------|
| 1. 选择快速疗程5天 | `end_date` = 开始日期+4天 | `end_date` = 开始日期+4天 |
| 2. 提交数据 | `duration_days` = undefined | `duration_days` = 5 ✅ |
| 3. 后端保存 | 强制 `duration_days` = 1 ❌ | 使用 `duration_days` = 5 ✅ |
| 4. 数据库存储 | `duration_days` = 1, `end_date` = 开始日期 ❌ | `duration_days` = 5, `end_date` = 开始日期+4天 ✅ |
| 5. 前端显示 | 剩余0天 ❌ | 剩余5天 ✅ |

## 测试验证

### 测试场景1：快速疗程选择

**步骤：**
1. 添加用药 → 选择"临时用药"
2. 选择快速疗程"5天"
3. 点击保存
4. 查看药品详情

**预期结果：**
- ✅ 疗程天数显示：5天
- ✅ 结束日期：开始日期+4天
- ✅ 剩余天数：5天

### 测试场景2：手动输入疗程

**步骤：**
1. 添加用药 → 选择"临时用药"
2. 手动输入开始日期和结束日期
3. 点击保存
4. 查看药品详情

**预期结果：**
- ✅ 疗程天数：根据日期自动计算
- ✅ 结束日期：用户选择的日期
- ✅ 剩余天数：正确计算

### 测试场景3：长期用药不受影响

**步骤：**
1. 添加用药 → 选择"长期用药"
2. 设置用药信息
3. 点击保存

**预期结果：**
- ✅ 疗程天数：可选填
- ✅ 功能正常，不受影响

## 相关文件

**前端：**
- `frontend-mobile/src/pages/medication/add.vue` - 添加用药页面

**后端：**
- `backend/app/routers/medications.py` - 用药API

**测试：**
- `backend/test_temporary_medication_fix.py` - 测试脚本

## 注意事项

1. **向下兼容**
   - 修复后的代码兼容旧版本前端
   - 如果前端未传递 `duration_days`，后端会使用默认值1

2. **数据一致性**
   - 现有的临时用药数据（疗程1天）不会自动修复
   - 需要用户手动延期或重新添加

3. **测试建议**
   - 测试所有疗程选项：1天、3天、5天、7天、14天、30天
   - 测试手动选择日期的情况
   - 测试编辑已有临时用药的情况

## 总结

**修复时间：** 2026-04-17

**修复内容：**
- ✅ 前端：临时用药提交正确的 `duration_days`
- ✅ 后端：不再强制覆盖临时用药的疗程天数

**影响范围：** 所有临时用药的添加和编辑功能

**测试状态：** 待前端测试验证
