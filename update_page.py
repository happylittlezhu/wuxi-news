# -*- coding: utf-8 -*-
"""
无锡重点关注企业商业动态·每日参阅 —— 页面数据更新脚本
用法：python update_page.py [html_path] [json_path]
默认在同目录下读取 index.html 和 new_data.json

new_data.json 格式：
{
  "date": "YYYY-MM-DD",
  "today": [ {"title","event","relation","source","url"} ],   // 当日精选 8-12 条
  "records": [ {"time","name","field","industry","type","desc","city","source","url"} ]  // 简讯流全量记录
}
"""
import json, os, re, sys, io
from datetime import datetime

BASE = os.path.dirname(os.path.abspath(__file__))
HTML = sys.argv[1] if len(sys.argv) > 1 else os.path.join(BASE, 'index.html')
INPUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(BASE, 'new_data.json')
XLSX = os.path.join(os.path.dirname(os.path.abspath(HTML)), '无锡头部企业商业动态.xlsx')


def load_json(path):
    with io.open(path, 'r', encoding='utf-8-sig') as f:
        return json.load(f)


def parse_const_array(line):
    """从 'const XXX = [...];' 行中解析 JSON 数组"""
    m = re.match(r'^\s*const\s+\w+\s*=\s*(\[.*\])\s*;\s*$', line, re.S)
    if not m:
        raise ValueError('无法解析行: %s...' % line[:60])
    return json.loads(m.group(1))


def dedup_key(rec):
    return (rec.get('name', '') + '|' + rec.get('desc', '')[:40]).strip()


def time_key(t):
    """把各种时间格式解析为可比较的元组：YYYY-MM-DD / YYYY-MM / YYYY / YYYY上半年 / YYYY下半年"""
    t = (t or '').strip()
    m = re.match(r'^(\d{4})-(\d{1,2})-(\d{1,2})$', t)
    if m:
        return (int(m.group(1)), int(m.group(2)), int(m.group(3)))
    m = re.match(r'^(\d{4})-(\d{1,2})$', t)
    if m:
        return (int(m.group(1)), int(m.group(2)), 0)
    m = re.match(r'^(\d{4})上半年$', t)
    if m:
        return (int(m.group(1)), 1, 0)
    m = re.match(r'^(\d{4})下半年$', t)
    if m:
        return (int(m.group(1)), 7, 0)
    m = re.match(r'^(\d{4})$', t)
    if m:
        return (int(m.group(1)), 0, 0)
    return (0, 0, 0)


def sort_records_desc(records):
    """按时间由近及远排序（稳定排序，同日保持原相对顺序）"""
    return sorted(records, key=lambda r: time_key(r.get('time', '')), reverse=True)


def extract_time_from_text(text):
    """从正文中提取事件日期，返回 'YYYY-MM-DD' 或 'YYYY-MM'；提取不到返回 None"""
    if not text:
        return None
    m = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日', text)
    if m:
        return '%s-%02d-%02d' % (m.group(1), int(m.group(2)), int(m.group(3)))
    m = re.search(r'(\d{4})年(\d{1,2})月', text)
    if m:
        return '%s-%02d' % (m.group(1), int(m.group(2)))
    m = re.search(r'(\d{1,2})月(\d{1,2})日', text)
    if m:
        return '%s-%02d-%02d' % (datetime.now().year, int(m.group(1)), int(m.group(2)))
    return None


def sort_today_desc(today):
    """当日精选按事件时间由近及远排序。

    时间来源优先级：time 字段 > 从 title/event 正文提取的日期。
    完全无法确定时间的条目排在最后，保持原相对顺序（稳定排序）。
    """
    if not today:
        return today

    def eff_time(it):
        t = str(it.get('time', '')).strip()
        if t:
            return t
        text = ' '.join([str(it.get('title', '')), str(it.get('event', ''))])
        return extract_time_from_text(text) or ''

    def key(it):
        return time_key(eff_time(it))

    with_t = [it for it in today if key(it)[0] > 0]
    without_t = [it for it in today if key(it)[0] <= 0]
    with_t = sorted(with_t, key=key, reverse=True)
    return with_t + without_t


def main():
    new = load_json(INPUT)
    date = new['date']
    today = new.get('today', [])
    records = new.get('records', [])
    collect_time = date + ' 07:30'

    if not date or (not today and not records):
        print('WARN: 无有效数据（date=%s, today=%d条, records=%d条）' % (date, len(today), len(records)))

    with io.open(HTML, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    out, data_total, skipped = [], 0, 0
    for line in lines:
        if line.startswith('const DATA = '):
            data = parse_const_array(line)
            existing_keys = {dedup_key(r) for r in data}
            new_recs = []
            for r in records:
                rec = dict(r)
                rec.setdefault('time', date)
                rec['collect'] = collect_time
                if dedup_key(rec) in existing_keys:
                    skipped += 1
                    continue
                new_recs.append(rec)
            data = new_recs + data
            data = sort_records_desc(data)
            for idx, r in enumerate(data):
                r['seq'] = idx + 1
            data_total = len(data)
            out.append('const DATA = ' + json.dumps(data, ensure_ascii=False) + ';\n')
        elif line.startswith('const TODAY = '):
            out.append('const TODAY = ' + json.dumps(sort_today_desc(today), ensure_ascii=False) + ';\n')
        elif line.startswith('const TODAY_DATE = '):
            out.append('const TODAY_DATE = "%s";\n' % date)
        elif line.startswith('const TODAY_DATE_CN = '):
            out.append('const TODAY_DATE_CN = "%s";\n' % date)
        else:
            out.append(line)

    with io.open(HTML, 'w', encoding='utf-8') as f:
        f.writelines(out)

    print('OK: 页面已更新至 %s；当日精选 %d 条；新增记录 %d 条（去重跳过 %d 条）；DATA 总计 %d 条'
          % (date, len(today), len(records) - skipped, skipped, data_total))

    # 同步重新生成 Excel（openpyxl 可用时）
    try:
        from openpyxl import Workbook
        wb = Workbook()
        ws = wb.active
        ws.title = '商业动态'
        headers = ['序号', '采集日期', '动态日期', '企业名称', '业务领域', '所属产业', '动态类型', '动态内容', '涉及城市', '来源']
        ws.append(headers)
        for r in data:
            ws.append([r.get('seq', ''), r.get('collect', ''), r.get('time', ''), r.get('name', ''),
                       r.get('field', ''), r.get('industry', ''), r.get('type', ''),
                       r.get('desc', ''), r.get('city', ''), r.get('source', '')])
        wb.save(XLSX)
        print('OK: Excel 已同步更新（%d 条）' % data_total)
    except ImportError:
        print('NOTE: 未安装 openpyxl，跳过 Excel 更新')

    # 同步输出 data.json（供微信小程序 wx.request 拉取）
    try:
        json_out = {
            'date': date,
            'today': today,
            'data': data,
            'total': data_total
        }
        json_path = os.path.join(os.path.dirname(os.path.abspath(HTML)), 'data.json')
        with io.open(json_path, 'w', encoding='utf-8') as f:
            json.dump(json_out, f, ensure_ascii=False)
        print('OK: data.json 已同步更新（%d 条 + 当日精选 %d 条）' % (data_total, len(today)))
    except Exception as e:
        print('WARN: data.json 输出失败: %s' % e)


if __name__ == '__main__':
    main()
