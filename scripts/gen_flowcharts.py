#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成两张业务流程图 SVG（零依赖）：
  1) docs/flowchart-current.svg  无 AI 现状业务流程图（泳道 + 痛点标注）
  2) docs/flowchart-ai.svg       增加 AI 后系统流程图（含人工兜底/降级分支）
运行：python scripts/gen_flowcharts.py
"""
import os
import html

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "docs")

# ---- 样式 ----
INK = "#1f2933"
MUTED = "#6b7280"
LINE = "#cbd5e1"
BG = "#ffffff"
# 角色泳道配色
ROLE_COLORS = {
    "学生":        "#e0f2fe",
    "助教":        "#dcfce7",
    "课程运营员":   "#fef9c3",
    "讲师/数据专员": "#ede9fe",
    "系统/平台":    "#f1f5f9",
    "AI 引擎":     "#ddd6fe",
}
KIND = {
    "start":  ("#16a34a", "#f0fdf4"),
    "end":    ("#dc2626", "#fef2f2"),
    "process":("#2563eb", "#eff6ff"),
    "ai":     ("#7c3aed", "#f5f3ff"),
    "decision":("#d97706", "#fffbeb"),
    "note":   ("#dc2626", "#fef2f2"),
}

def esc(s): return html.escape(str(s))

def wrap(text, n):
    """按字符数折行（适配中文）。"""
    lines, cur = [], ""
    for ch in str(text):
        cur += ch
        if len(cur) >= n:
            lines.append(cur); cur = ""
    if cur: lines.append(cur)
    return lines

def text_block(lines, x, y, fs=13, color=INK, anchor="start", weight="normal"):
    out = []
    lh = fs * 1.35
    for i, ln in enumerate(lines):
        out.append(f'<text x="{x}" y="{y + i*lh}" font-size="{fs}" fill="{color}" '
                   f'text-anchor="{anchor}" font-weight="{weight}" '
                   f'font-family="PingFang SC, Microsoft YaHei, sans-serif">{esc(ln)}</text>')
    return "\n".join(out)

def role_band(role, x, y, w, h):
    color = ROLE_COLORS.get(role, "#f1f5f9")
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{color}" '
            f'stroke="{LINE}" stroke-width="1"/>')

def node(x, y, w, h, kind, title, body_lines, role=None):
    stroke, fill = KIND.get(kind, KIND["process"])
    parts = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="9" '
             f'fill="{fill}" stroke="{stroke}" stroke-width="1.6"/>']
    # 标题
    parts.append(text_block([title], x+12, y+20, fs=13, color=stroke, weight="700"))
    if body_lines:
        parts.append(text_block(body_lines, x+12, y+38, fs=12, color=INK))
    return "\n".join(parts)

def arrow(x1, y1, x2, y2, label=None, dash=False):
    d = 'stroke-dasharray="5 4" ' if dash else ''
    a = (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{MUTED}" '
         f'stroke-width="1.6" {d}marker-end="url(#arr)"/>')
    if label:
        a += text_block([label], (x1+x2)/2+6, (y1+y2)/2, fs=11, color=MUTED)
    return a

def build(title, steps, side_notes, width=1000):
    lane_w = 120
    note_w = 250
    box_w = width - lane_w - note_w - 40
    top = 64
    box_h = 58
    gap = 26
    n = len(steps)
    height = top + n*(box_h+gap) + 40
    box_x = lane_w + 20
    parts = []
    parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
                 f'font-family="PingFang SC, Microsoft YaHei, sans-serif">')
    parts.append(f'<rect x="0" y="0" width="{width}" height="{height}" fill="{BG}"/>')
    # 标题
    parts.append(f'<rect x="0" y="0" width="{width}" height="48" fill="#1e3a8a"/>')
    parts.append(text_block([title], 18, 30, fs=18, color="#ffffff", weight="700"))
    # 箭头定义
    parts.append('<defs><marker id="arr" markerWidth="10" markerHeight="10" refX="8" refY="3" '
                 'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8,3 L0,6 Z" fill="#6b7280"/></marker></defs>')
    ys = []
    for i, s in enumerate(steps):
        y = top + i*(box_h+gap)
        ys.append(y)
        # 泳道
        parts.append(role_band(s["role"], 0, y, lane_w, box_h))
        parts.append(text_block(wrap(s["role"], 5), 10, y+box_h/2-6, fs=12,
                               color=INK, weight="700"))
        # 节点
        body = wrap(s.get("body", ""), 26) if s.get("body") else []
        parts.append(node(box_x, y, box_w, box_h, s["kind"], s["title"], body, s["role"]))
    # 顺序箭头
    cx = box_x + box_w/2
    for i in range(n-1):
        parts.append(arrow(cx, ys[i]+box_h, cx, ys[i+1]))
    # 侧边痛点
    for nt in side_notes:
        idx = nt["at"]
        y = ys[idx] + box_h/2
        nx = box_x + box_w + 16
        ny = y - 22
        color = "#dc2626"
        parts.append(f'<rect x="{nx}" y="{ny}" width="{note_w}" height="44" rx="7" '
                     f'fill="#fef2f2" stroke="#fecaca" stroke-width="1.2"/>')
        parts.append(text_block([nt["t"]], nx+10, ny+18, fs=11.5, color=color, weight="700"))
        if nt.get("d"):
            parts.append(text_block(wrap(nt["d"], 16), nx+10, ny+34, fs=10.5, color=MUTED))
        parts.append(arrow(box_x+box_w, y, nx, y, dash=True))
    parts.append('</svg>')
    return "\n".join(parts)

def build_ai(title, steps, branches, degraded):
    """带分支与降级说明的竖直流程图（AI）。"""
    width = 1000
    box_w = 640
    box_x = 200
    top = 64
    box_h = 56
    gap = 24
    n = len(steps)
    height = top + n*(box_h+gap) + 220
    parts = []
    parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
                 f'font-family="PingFang SC, Microsoft YaHei, sans-serif">')
    parts.append(f'<rect x="0" y="0" width="{width}" height="{height}" fill="{BG}"/>')
    parts.append(f'<rect x="0" y="0" width="{width}" height="48" fill="#1e3a8a"/>')
    parts.append(text_block([title], 18, 30, fs=18, color="#ffffff", weight="700"))
    parts.append('<defs><marker id="arr" markerWidth="10" markerHeight="10" refX="8" refY="3" '
                 'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8,3 L0,6 Z" fill="#6b7280"/></marker>'
                 '<marker id="arrR" markerWidth="10" markerHeight="10" refX="8" refY="3" '
                 'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8,3 L0,6 Z" fill="#dc2626"/></marker></defs>')
    ys = []
    for i, s in enumerate(steps):
        y = top + i*(box_h+gap); ys.append(y)
        body = wrap(s.get("body", ""), 30) if s.get("body") else []
        parts.append(node(box_x, y, box_w, box_h, s["kind"], s["title"], body))
    cx = box_x + box_w/2
    for i in range(n-1):
        parts.append(arrow(cx, ys[i]+box_h, cx, ys[i+1]))
    # 分支（转人工/暂停）
    for b in branches:
        idx = b["at"]; y = ys[idx]+box_h/2
        bx = box_x + box_w + 30
        by = y - 30
        parts.append(f'<rect x="{bx}" y="{by}" width="250" height="60" rx="8" '
                     f'fill="#fef2f2" stroke="#fca5a5" stroke-width="1.4"/>')
        parts.append(text_block([b["t"]], bx+10, by+18, fs=12, color="#dc2626", weight="700"))
        parts.append(text_block(wrap(b["d"], 16), bx+10, by+36, fs=10.5, color=MUTED))
        parts.append(arrow(box_x+box_w, y, bx, y, dash=True))
    # 降级说明框
    dy = ys[-1] + box_h + 40
    parts.append(f'<rect x="{box_x}" y="{dy}" width="{box_w}" height="70" rx="8" '
                 f'fill="#fffbeb" stroke="#fcd34d" stroke-width="1.4"/>')
    parts.append(text_block([degraded["t"]], box_x+12, dy+22, fs=13, color="#b45309", weight="700"))
    parts.append(text_block(wrap(degraded["d"], 52), box_x+12, dy+42, fs=11.5, color=MUTED))
    parts.append('</svg>')
    return "\n".join(parts)


# ================= 图 1：无 AI 现状 =================
current_steps = [
    {"role":"学生","kind":"start","title":"学生在群聊/作业评论中提问",
     "body":"求助入口分散，无统一受理渠道"},
    {"role":"助教","kind":"process","title":"手动巡查群聊 + 作业评论",
     "body":"人工翻找，高峰期仅能用现有终端"},
    {"role":"助教","kind":"process","title":"识别支持需求（靠经验）",
     "body":"无连续求助合并口径，常把续问当新问题"},
    {"role":"助教","kind":"process","title":"分类与转交",
     "body":"约 900 条/周 × 6 分钟/条"},
    {"role":"课程运营员","kind":"process","title":"交接给运营/下一责任人",
     "body":"现状常只写“已转交”，缺随单说明"},
    {"role":"助教","kind":"process","title":"助教联系学生",
     "body":"首次响应约 26 小时"},
    {"role":"讲师/数据专员","kind":"process","title":"辅导安排",
     "body":"跨岗冲突、重复求助率 35%"},
    {"role":"课程运营员","kind":"process","title":"反馈",
     "body":"通知发送量 ≠ 实际完成量"},
    {"role":"讲师/数据专员","kind":"end","title":"复盘（退回需保留原因）",
     "body":"建议无法溯源，难定位瓶颈"},
]
current_notes = [
    {"at":1,"t":"⚠ 入口分散","d":"群聊/作业评论/LMS 各一处"},
    {"at":2,"t":"⚠ 漏接连续求助","d":"f10：连续求助常被漏掉"},
    {"at":4,"t":"⚠ 交接无随单说明","d":"f14：说明留便签不随单"},
    {"at":4,"t":"⚠ 无接手确认","d":"f23：发消息≠完成"},
    {"at":6,"t":"⚠ 重复求助 35%","d":"f00：目标 15%"},
]

# ================= 图 2：增加 AI 后 =================
ai_steps = [
    {"role":"系统/平台","kind":"start","title":"多源采集：群聊 / 作业评论 / LMS / 直播",
     "body":"统一事件流，带业务编号 + 时间戳 + 版本"},
    {"role":"AI 引擎","kind":"ai","title":"AI 识别 + 合并连续求助",
     "body":"按学生把连续求助合并为一张工单（REQ-1/2）"},
    {"role":"AI 引擎","kind":"ai","title":"数据质量校验",
     "body":"校验主编号/事件时间/版本；歧义进人工修复队列（REQ-3）"},
    {"role":"AI 引擎","kind":"ai","title":"生成支持建议",
     "body":"显示原记录 + 待确认字段；不自动定性/评分（硬边界）"},
    {"role":"助教","kind":"decision","title":"助教人工复核",
     "body":"确认 / 转人工 / 暂停（f15、f44）"},
    {"role":"助教","kind":"process","title":"人工确认后联系学生",
     "body":"硬线：系统不直接触达（f42）"},
    {"role":"课程运营员","kind":"process","title":"辅导安排 + 接手确认",
     "body":"随单说明：编号/版本/状态/未解决/接手人（f23）"},
    {"role":"讲师/数据专员","kind":"process","title":"反馈闭环",
     "body":"误判例子收集，按问题解决率口径（f51/f55）"},
    {"role":"讲师/数据专员","kind":"end","title":"审计链 + 复盘",
     "body":"编号/版本/事实/建议/人工改动/签核人（f45）"},
]
ai_branches = [
    {"at":4,"t":"转人工 / 暂停","d":"标注触发原因 + 接手人 + 确认时间（f44）"},
]
ai_degraded = {"t":"降级与兜底（f35）",
    "d":"接口中断时使用带时间戳的只读快照，显示“暂未更新”；重连后按业务编号去重补齐，不重复派单，现有人工流程继续运行。"}

if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    p1 = os.path.join(OUT_DIR, "flowchart-current.svg")
    p2 = os.path.join(OUT_DIR, "flowchart-ai.svg")
    with open(p1, "w", encoding="utf-8") as f:
        f.write(build("无 AI 现状业务流程图 · 北辰在线学院学习支持协作", current_steps, current_notes))
    with open(p2, "w", encoding="utf-8") as f:
        f.write(build_ai("增加 AI 后系统流程图 · 北辰在线学院学习支持协作", ai_steps, ai_branches, ai_degraded))
    print("written:", os.path.abspath(p1))
    print("written:", os.path.abspath(p2))
