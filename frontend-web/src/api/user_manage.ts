import request from '../utils/request'

export function getPatients(params: any) {
  // 目前还没有专门的 patients 列表接口 (除了 doctor 的)，这里我们复用 doctor 的或者新建一个 admin 的
  // 假设后端有 /patients/ 接口支持分页查询
  return request({
    url: '/patients/',
    method: 'get',
    params
  })
}

// 暂时没有 admin 的患者管理接口，我们可能需要修改后端 patients.py，增加一个 query 接口
// 现在只能用 /patients/me 或者 /doctors/patients
// 让我们假设我们已经在后端加了 admin 获取患者列表的接口，或者我们现在去加一个
// 检查一下 backend/app/routers/patients.py
