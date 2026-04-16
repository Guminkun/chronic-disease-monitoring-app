"""
OCR Service — 基于 PaddleOCR 异步 Job API (v2)
流程：提交 Job → 轮询状态 → 下载 JSONL 结果 → 解析
"""
import asyncio
import base64
import datetime
import json
import re
from typing import Any, Dict, List, Optional

import httpx

from app.config import settings

try:
    from bs4 import BeautifulSoup  # type: ignore
    _HAS_BS4 = True
except Exception:
    BeautifulSoup = None  # type: ignore
    _HAS_BS4 = False

_OPTIONAL_PAYLOAD = {
    "markdownIgnoreLabels": [
        "header", "header_image", "footer", "footer_image",
        "number", "footnote", "aside_text"
    ],
    "useDocOrientationClassify": False,
    "useDocUnwarping": False,
    "useLayoutDetection": True,
    "useChartRecognition": False,
    "promptLabel": "ocr",
    "repetitionPenalty": 1,
    "temperature": 0,
    "topP": 1,
    "minPixels": 147384,
    "maxPixels": 2822400,
    "layoutNms": True,
}

_POLL_INTERVAL = 5   # 秒
_MAX_WAIT = 300      # 最长等待 5 分钟


def _auth_headers() -> Dict[str, str]:
    return {"Authorization": f"bearer {settings.PADDLE_OCR_TOKEN}"}


async def _submit_job(client: httpx.AsyncClient, file_content: bytes, filename: str) -> str:
    """提交文件，返回 jobId。支持本地文件（multipart）。"""
    job_url = settings.PADDLE_OCR_JOB_URL
    headers = _auth_headers()
    data = {
        "model": settings.PADDLE_OCR_MODEL,
        "optionalPayload": json.dumps(_OPTIONAL_PAYLOAD),
    }
    files = {"file": (filename, file_content)}
    resp = await client.post(job_url, headers=headers, data=data, files=files)
    if resp.status_code != 200:
        raise Exception(f"OCR Job 提交失败: {resp.status_code} - {resp.text}")
    job_id = resp.json()["data"]["jobId"]
    print(f"[OCR] Job 提交成功，jobId={job_id}")
    return job_id


async def _poll_job(client: httpx.AsyncClient, job_id: str) -> str:
    """轮询直到 done，返回 jsonl_url。"""
    job_url = settings.PADDLE_OCR_JOB_URL
    headers = _auth_headers()
    elapsed = 0
    while elapsed < _MAX_WAIT:
        await asyncio.sleep(_POLL_INTERVAL)
        elapsed += _POLL_INTERVAL
        resp = await client.get(f"{job_url}/{job_id}", headers=headers)
        if resp.status_code != 200:
            raise Exception(f"OCR 轮询失败: {resp.status_code} - {resp.text}")
        data = resp.json()["data"]
        state = data["state"]
        if state == "pending":
            print(f"[OCR] jobId={job_id} 状态: pending ({elapsed}s)")
        elif state == "running":
            prog = data.get("extractProgress", {})
            print(f"[OCR] jobId={job_id} 运行中: {prog.get('extractedPages', '?')}/{prog.get('totalPages', '?')} 页 ({elapsed}s)")
        elif state == "done":
            jsonl_url = data["resultUrl"]["jsonUrl"]
            print(f"[OCR] jobId={job_id} 完成，结果地址: {jsonl_url}")
            return jsonl_url
        elif state == "failed":
            raise Exception(f"OCR Job 失败: {data.get('errorMsg', '未知错误')}")
        else:
            print(f"[OCR] jobId={job_id} 未知状态: {state}")
    raise Exception(f"OCR Job 超时（>{_MAX_WAIT}s），jobId={job_id}")


async def _download_result(client: httpx.AsyncClient, jsonl_url: str) -> str:
    """下载 JSONL 结果，拼接所有页的 markdown 文本。"""
    resp = await client.get(jsonl_url)
    resp.raise_for_status()
    summary = ""
    for line in resp.text.strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        try:
            result = json.loads(line).get("result", {})
            for res in result.get("layoutParsingResults", []):
                md = res.get("markdown", {})
                if md.get("text"):
                    summary += md["text"] + "\n"
        except Exception:
            continue
    return summary


async def _run_ocr_job(file_content: bytes, filename: str) -> str:
    """完整流程：提交 → 轮询 → 下载，返回 markdown 文本。"""
    timeout = httpx.Timeout(timeout=30.0, connect=15.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        job_id = await _submit_job(client, file_content, filename)
        jsonl_url = await _poll_job(client, job_id)
        return await _download_result(client, jsonl_url)


# ── 公开接口 ──────────────────────────────────────────────

MEDICAL_FIELD_PATTERNS = {
    'hospital': (
        ['医院', '医疗机构', '就诊医院', '就诊机构'],
        r'[：:\s]*([^\n，。]+?)(?=科室|门诊|日期|$)'
    ),
    'patient_name': (
        ['姓名', '患者姓名', '病人姓名'],
        r'[：:\s]*([^\n，。性别年龄]+?)(?=性别|年龄|科室|$)'
    ),
    'age': (
        ['年龄', '患者年龄'],
        r'[：:\s]*(\d+岁?)'
    ),
    'gender': (
        ['性别', '患者性别'],
        r'[：:\s]*([男女])'
    ),
    'report_type': (
        ['诊断', '初步诊断', '门诊诊断', '临床诊断'],
        r'[：:\s]*([^\n#]+?)(?=#|处理|治疗|注意事项|$)'
    ),
    'report_date': (
        ['日期', '就诊日期', '报告日期', '检查日期', '时间'],
        r'[：:\s]*(\d{4}[-/年]\d{1,2}[-/月]\d{1,2}日?)'
    ),
    'chief_complaint': (
        ['主诉', '患者主诉'],
        r'[：:\s]*([^\n#]+?)(?=\s*(?:##)?\s*(?:现病史|既往史)|$)'
    ),
    'present_illness': (
        ['现病史', '病史', '患者病史'],
        r'[：:\s]*([^\n#]+?)(?=\s*(?:##)?\s*(?:既往史|个人史|家族史|查体|辅助检查)|$)'
    ),
    'past_history': (
        ['既往史', '既往病史', '过去史'],
        r'[：:\s]*([^\n#]+?)(?=\s*(?:##)?\s*(?:个人史|家族史|查体|辅助检查|诊断)|$)'
    ),
    'personal_history': (
        ['个人史', '个人病史'],
        r'[：:\s]*([^\n#]+?)(?=\s*(?:##)?\s*(?:家族史|查体|辅助检查|诊断)|$)'
    ),
    'family_history': (
        ['家族史', '家族病史'],
        r'[：:\s]*([^\n#]+?)(?=\s*(?:##)?\s*(?:查体|辅助检查|诊断|处理|治疗)|$)'
    ),
    'department': (
        ['科室'],
        r'[：:\s]*([^\n，。#]+?)(?=日期|登记号|病案号|$)'
    ),
}


def extract_medical_fields(summary: str) -> Dict[str, Any]:
    """
    从病历OCR文本中提取关键字段
    仅返回有实际数据的字段，空值字段不返回
    """
    if not summary:
        return {}
    
    text = re.sub(r'<[^>]+>', ' ', summary)
    text = re.sub(r'\s+', ' ', text).strip()
    
    result = {}
    
    hospital_match = re.search(r'^([^\n，。科室]+?(?:医院|医疗机构))', text)
    if hospital_match:
        hospital = hospital_match.group(1).strip()
        if hospital and '___' not in hospital:
            result['hospital'] = hospital
    
    for field_name, (keywords, pattern) in MEDICAL_FIELD_PATTERNS.items():
        if field_name == 'hospital':
            continue
            
        for keyword in keywords:
            full_pattern = re.escape(keyword) + pattern
            match = re.search(full_pattern, text, re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                value = re.sub(r'^[：:\s\-−\[\]【】]+', '', value)
                value = re.sub(r'[：:\s\-−\[\]【】]+$', '', value)
                
                stop_keywords = ['既往史', '个人史', '家族史', '检查', '诊断', '治疗', '医生签名', '日期', '页', '\n', '处理', '注意事项', '建议']
                for stop_kw in stop_keywords:
                    if stop_kw in value:
                        value = value.split(stop_kw)[0].strip()
                
                value = re.sub(r'\s*\[[-−]\]\s*', ' ', value).strip()
                value = re.sub(r'\s+', ' ', value)
                value = value.replace('[-]', '').replace('[−]', '').strip()
                
                value = re.sub(r'\s*##\s*', ' ', value).strip()
                
                if '___' in value and value.replace('___', '').replace('：', '').replace(':', '').replace(' ', '') == '':
                    continue
                
                if value and len(value) > 0 and value not in ['___', '——', '—', '无', '否认']:
                    result[field_name] = value
                    break
    
    if 'report_type' not in result:
        diagnosis_match = re.search(r'(?:诊断|初步诊断)[：:\s]*([^\n#]+?)(?=#|处理|治疗|注意事项|$)', text, re.IGNORECASE)
        if diagnosis_match:
            result['report_type'] = diagnosis_match.group(1).strip()
    
    return result


async def parse_report_file(file_content: bytes, filename: str) -> Dict[str, Any]:
    """解析报告文件，返回含 summary + metrics + basic_info 的字典。"""
    print(f"[OCR] 开始解析: {filename} ({len(file_content)} bytes)")
    summary = await _run_ocr_job(file_content, filename)
    today = datetime.date.today().strftime("%Y-%m-%d")
    
    basic_info = {}
    metrics = []
    
    if "<table" in summary.lower() and "</table>" in summary.lower():
        metrics, basic_info = extract_metrics_and_info_from_html(summary)
    else:
        metrics = extract_metrics_from_markdown(summary)
        basic_info = extract_basic_info_from_text(summary)
    
    findings = ""
    diagnosis = ""
    
    text = re.sub(r'<[^>]+>', ' ', summary)
    text = re.sub(r'\s+', ' ', text).strip()
    
    imaging_keywords = ['超声', 'CT', 'MRI', 'X线', '影像', '核磁']
    lab_keywords = ['参考区间', '参考范围', '单位', '结果', '项目', '检验']
    
    is_imaging = False
    imaging_keyword_count = sum(1 for kw in imaging_keywords if kw in text)
    lab_keyword_count = sum(1 for kw in lab_keywords if kw in text)
    
    if imaging_keyword_count >= 2 and lab_keyword_count < 2:
        is_imaging = True
    elif lab_keyword_count >= 2 and imaging_keyword_count < 2:
        is_imaging = False
    else:
        if metrics and len(metrics) > 0:
            is_imaging = False
        else:
            is_imaging = imaging_keyword_count > lab_keyword_count
    
    if is_imaging:
        findings, diagnosis = extract_imaging_findings_and_diagnosis(summary)
    
    return {
        "report_date": today,
        "hospital_name": basic_info.get("hospital_name", ""),
        "summary": summary or "OCR解析成功，但未提取到有效文本。",
        "metrics": [] if is_imaging else metrics,
        "basic_info": basic_info,
        "findings": findings,
        "diagnosis": diagnosis
    }


def extract_imaging_findings_and_diagnosis(summary: str) -> tuple[str, str]:
    """
    从影像报告中提取检查所见和诊断结果
    返回: (检查所见, 诊断结果)
    """
    if not summary:
        return "", ""
    
    text = re.sub(r'<[^>]+>', ' ', summary)
    text = re.sub(r'\s+', ' ', text).strip()
    
    findings = ""
    diagnosis = ""
    
    findings_patterns = [
        r'(?:检查|影像|超声)?[所见及]+[:：\s]*([^\n]+?)(?=诊断|结论|意见|印象|$)',
        r'影像[表现所见]+[:：\s]*([^\n]+?)(?=诊断|结论|意见|印象|$)',
    ]
    
    for pattern in findings_patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            findings = match.group(1).strip()
            findings = re.sub(r'^[：:\s]+', '', findings)
            findings = re.sub(r'[：:\s]+$', '', findings)
            
            sentences = re.split(r'[。！？]', findings)
            if len(sentences) > 0:
                findings = '。'.join(sentences[:5])
                if not findings.endswith('。'):
                    findings += '。'
            
            if len(findings) > 10:
                break
    
    diagnosis_patterns = [
        r'(?:诊断|结论|意见|印象)[:：\s]*([^\n。]+)',
    ]
    
    for pattern in diagnosis_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            diagnosis = match.group(1).strip()
            diagnosis = re.sub(r'^[：:\s]+', '', diagnosis)
            diagnosis = re.sub(r'[：:\s]+$', '', diagnosis)
            
            stop_words = ['检查', '检验', '记录', '医生', '时间', '日期']
            parts = re.split(r'[，,、\s]+', diagnosis)
            clean_parts = []
            for part in parts:
                part = part.strip()
                if part and not any(sw in part for sw in stop_words):
                    clean_parts.append(part)
                elif clean_parts:
                    break
            
            if clean_parts:
                diagnosis = ' '.join(clean_parts[:3])
            
            if len(diagnosis) > 2:
                break
    
    return findings, diagnosis


async def parse_report_text_only(file_content: bytes, filename: str) -> Dict[str, Any]:
    """仅提取纯文本（影像报告用）。"""
    print(f"[OCR] 纯文本解析: {filename}")
    summary = await _run_ocr_job(file_content, filename)
    today = datetime.date.today().strftime("%Y-%m-%d")
    text = extract_text_only(summary)
    return {
        "report_date": today,
        "text": text or "OCR解析成功，但未提取到有效文本。",
    }


# ── 结果处理工具函数 ──────────────────────────────────────

def extract_text_only(summary: str) -> str:
    if not summary:
        return ""
    txt = re.sub(r"<[^>]+>", " ", summary).replace("&nbsp;", " ")
    lines = [l.strip() for l in txt.splitlines()]
    cleaned = [
        l for l in lines
        if l and not ("|" in l and l.count("|") >= 2) and not (set(l) <= {"|", "-", " "})
    ]
    return "\n".join(cleaned)


# 预设字段配置：字段名 -> (关键词列表, 提取模式)
FIELD_PATTERNS = {
    'gender': (
        ['性别', '性别：', '性别:', '患者性别'],
        r'[：:\s]*([男女])'
    ),
    'age': (
        ['年龄', '年龄：', '年龄:', '患者年龄'],
        r'[：:\s]*(\d+)\s*岁?'
    ),
    'project_package': (
        ['项目套餐', '项目', '套餐', '检查项目', '检验项目'],
        r'[：:\s]*([^\s]+)'
    ),
    'department': (
        ['病区', '科室', '病区/科室', '病区科室', '所在科室', '就诊科室', '申请科室'],
        r'[：:\s]*([^\s]+)'
    ),
    'hospital_name': (
        ['医疗机构', '医院', '医疗机构名称', '送检单位', '检验单位'],
        r'[：:\s]*([^\s]+)'
    ),
    'sample_time': (
        ['采样时间', '采样日期', '采集时间', '采血时间', '标本采集时间'],
        r'[：:\s]*([^\s]+)'
    ),
    'report_date': (
        ['报告时间', '报告日期', '打印时间', '审核时间'],
        r'[：:\s]*([^\s]+)'
    ),
    'sample_type': (
        ['样本种类', '标本种类', '标本类型', '样本类型'],
        r'[：:\s]*([^\s]+)'
    ),
    'receive_time': (
        ['接收时间', '收到时间', '标本接收时间'],
        r'[：:\s]*([^\s]+)'
    ),
    'request_doctor': (
        ['申请医生', '申请医师', '开单医生', '送检医生'],
        r'[：:\s]*([^\s]+)'
    ),
    'test_doctor': (
        ['检验医生', '检验者', '检验医师', '操作者', '检测者'],
        r'[：:\s]*([^\s]+)'
    ),
    'audit_doctor': (
        ['审核医生', '审核者', '审核医师', '复核者'],
        r'[：:\s]*([^\s]+)'
    ),
    'diagnosis': (
        ['诊断', '临床诊断', '初步诊断', '主诉诊断'],
        r'[：:\s]*([^\s]+)'
    ),
    'medical_record_no': (
        ['病历号', '病历编号', '门诊号', '住院号', '患者编号', '编号', 'ID'],
        r'[：:\s]*([^\s]+)'
    ),
}


def fuzzy_match_field(field_name: str, text: str) -> tuple[bool, str]:
    """
    模糊匹配字段名称
    返回: (是否匹配, 匹配到的关键词)
    """
    if field_name not in FIELD_PATTERNS:
        return False, ""
    
    keywords, _ = FIELD_PATTERNS[field_name]
    text_lower = text.lower()
    
    for keyword in keywords:
        keyword_lower = keyword.lower()
        if keyword_lower in text_lower:
            return True, keyword
        
        if len(keyword) >= 2:
            for i in range(len(text) - len(keyword) + 1):
                substring = text[i:i+len(keyword)]
                if len(set(substring) & set(keyword)) >= len(keyword) * 0.6:
                    return True, keyword
    
    return False, ""


def extract_field_value(field_name: str, text: str, matched_keyword: str) -> str:
    """
    提取字段值
    """
    if field_name not in FIELD_PATTERNS:
        return ""
    
    _, pattern_template = FIELD_PATTERNS[field_name]
    
    patterns_to_try = [
        re.escape(matched_keyword) + pattern_template,
        re.escape(matched_keyword) + r'[：:\s]*([^\s\n，。；]+)',
        re.escape(matched_keyword) + r'[：:\s]*([^<>\n]+?)(?=\s{2}|\n|<|$)',
        matched_keyword + r'[：:\s]*([^\s\n，。；]+)',
    ]
    
    for pattern in patterns_to_try:
        try:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match and match.group(1):
                value = match.group(1).strip()
                value = re.sub(r'^[：:\s]+', '', value)
                value = re.sub(r'[：:\s]+$', '', value)
                value = re.sub(r'<[^>]+>', '', value)
                value = re.sub(r'\s+', ' ', value).strip()
                
                if field_name == 'age' and not value.endswith('岁'):
                    value = value + '岁'
                
                if field_name == 'diagnosis' and len(value) > 50:
                    value = value[:50] + '...'
                
                if value and len(value) < 100 and value != matched_keyword:
                    return value
        except:
            continue
    
    return ""


def extract_basic_info_from_text(text: str) -> Dict[str, Any]:
    basic_info: Dict[str, Any] = {}
    if not text:
        return basic_info
    
    text_clean = re.sub(r'\s+', ' ', text)
    
    for field_name in FIELD_PATTERNS.keys():
        matched, keyword = fuzzy_match_field(field_name, text_clean)
        if matched:
            value = extract_field_value(field_name, text_clean, keyword)
            if value:
                basic_info[field_name] = value
    
    if 'patient_name' not in basic_info:
        match = re.search(r'(?:姓名|被检者|患者姓名)[：:\s]+([^\s]+)', text)
        if match:
            basic_info['patient_name'] = match.group(1)
    
    return basic_info


def extract_metrics_and_info_from_html(html_text: str) -> tuple[List[Dict[str, Any]], Dict[str, Any]]:
    metrics: List[Dict[str, Any]] = []
    basic_info: Dict[str, Any] = {}
    
    if not html_text:
        return metrics, basic_info

    def _parse_row_group(cell_texts: List[str]) -> List[Dict[str, Any]]:
        result = []
        for i in range(0, len(cell_texts), 5):
            g = cell_texts[i:i + 5]
            if len(g) < 5:
                continue
            name, code, value_raw, unit, ref = g
            if not name and not code:
                continue
            vm = re.search(r'([+-]?\d+(?:\.\d+)?)\s*([↓↑<>]?)', value_raw or "")
            value = vm.group(1) if vm else (value_raw or "")
            sym = vm.group(2) if vm else ""
            result.append({"name": name, "code": code, "value": value,
                           "unit": unit, "range": ref, "abnormal": bool(sym), "abnormal_symbol": sym})
        return result

    if _HAS_BS4 and BeautifulSoup:
        try:
            soup = BeautifulSoup(html_text, "html.parser")
            table = soup.find("table")
            if not table:
                return metrics, basic_info
            rows = table.find_all("tr")
            start = 0
            
            if rows:
                first_row_cells = [c.get_text(strip=True) for c in rows[0].find_all("td")]
                first_row_text = " ".join(first_row_cells)
                
                if any(k in first_row_text for k in ["姓名", "性别", "年龄", "病历号", "诊断", "科室", "病区"]):
                    for cell_text in first_row_cells:
                        for field_name in FIELD_PATTERNS.keys():
                            if field_name in basic_info:
                                continue
                            matched, keyword = fuzzy_match_field(field_name, cell_text)
                            if matched:
                                value = extract_field_value(field_name, cell_text, keyword)
                                if value:
                                    basic_info[field_name] = value
                    
                    if "patient_name" not in basic_info:
                        for cell_text in first_row_cells:
                            if "姓名" in cell_text or "送检者" in cell_text:
                                parts = re.split(r'[：:\s]+', cell_text)
                                if len(parts) > 1:
                                    basic_info['patient_name'] = parts[-1]
                    
                    start = 2 if len(rows) > 1 else 1
            
            for r in rows[start:]:
                cells = [c.get_text(strip=True) for c in r.find_all("td")]
                if any(cells):
                    metrics.extend(_parse_row_group(cells))
            
            return metrics, basic_info
        except Exception as e:
            print(f"Error parsing HTML: {e}")
            pass

    def strip_tags(s: str) -> str:
        return re.sub(r"<[^>]+>", "", s).strip()

    lines = [strip_tags(line) for line in html_text.split("\n") if strip_tags(line)]
    for line in lines:
        if "|" in line and line.count("|") >= 4:
            cols = [c.strip() for c in line.split("|")]
            metrics.extend(_parse_row_group(cols))
    
    return metrics, basic_info


def extract_metrics_from_markdown(text: str) -> List[Dict[str, Any]]:
    metrics: List[Dict[str, Any]] = []
    if not text:
        return metrics
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    i = 0
    while i < len(lines):
        line = lines[i]
        if "|" in line:
            header = [c.strip() for c in line.strip("|").split("|")]
            if i + 1 < len(lines) and set(lines[i + 1]) <= {"|", "-", " "}:
                j = i + 2
                name_idx = value_idx = unit_idx = range_idx = -1
                for idx, h in enumerate(header):
                    h2 = h.replace(" ", "")
                    if any(k in h2 for k in ["名称", "项目", "指标"]):
                        name_idx = idx
                    elif any(k in h2 for k in ["结果", "数值", "值", "Result", "Value"]):
                        value_idx = idx
                    elif any(k in h2 for k in ["单位", "Unit"]):
                        unit_idx = idx
                    elif any(k in h2 for k in ["参考", "范围", "Range"]):
                        range_idx = idx

                def safe_get(arr, idx2):
                    return arr[idx2].strip() if 0 <= idx2 < len(arr) else ""

                while j < len(lines) and "|" in lines[j]:
                    cols = [c.strip() for c in lines[j].strip("|").split("|")]
                    name = safe_get(cols, name_idx) if name_idx != -1 else safe_get(cols, 0)
                    value = safe_get(cols, value_idx) if value_idx != -1 else ""
                    unit = safe_get(cols, unit_idx) if unit_idx != -1 else ""
                    ref = safe_get(cols, range_idx) if range_idx != -1 else ""
                    if name:
                        metrics.append({"name": name, "code": "", "value": value,
                                        "unit": unit, "range": ref, "abnormal": False, "abnormal_symbol": ""})
                    j += 1
                i = j
                continue
        m = re.match(
            r"^([^:：\|\s]+)\s*[:：]\s*([+-]?\d+(?:\.\d+)?)\s*([^\s\(\)]+)?"
            r"\s*(?:\(([^)]+)\)|（([^）]+)）)?", line
        )
        if m:
            metrics.append({
                "name": m.group(1) or "",
                "code": "",
                "value": m.group(2) or "",
                "unit": m.group(3) or "",
                "range": m.group(4) or m.group(5) or "",
                "abnormal": False,
                "abnormal_symbol": "",
            })
        i += 1
    return metrics


def extract_metrics_from_html(html_text: str) -> List[Dict[str, Any]]:
    metrics, _ = extract_metrics_and_info_from_html(html_text)
    return metrics

