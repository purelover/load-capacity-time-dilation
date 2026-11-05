#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Regenerate the one-page plain-language posters (A4 portrait, 150 dpi):
  poster-zh.png  — Chinese
  poster-en.png  — English

Layout (v6): hero formula zone on top, two-column "derivation vs. verification"
zone in the middle, bottom takeaway zone, navy footer.

Run:  python3 make_poster.py
Requires matplotlib >= 3.6 (glyph fallback + inline mathtext).
"""
import os
import re

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import (Circle, Ellipse, FancyArrowPatch,
                                FancyBboxPatch, Polygon, Rectangle)

NAVY   = '#1F2A44'
RED    = '#C0392B'
GRAY   = '#404040'
LIGHT  = '#F5F7FA'
BLUE   = '#2B5B8A'
GOLD   = '#A66A00'
GOLDBG = '#FBF3E3'
GREEN  = '#2E7D32'
ORANGE = '#E8933A'
WHITE  = 'white'

ASP = 8.27 / 11.69          # y-length per x-length of a physically square box
DPI = 150
OUT_DIR = os.path.dirname(os.path.abspath(__file__))

# ----------------------------------------------------------------------
# language packs
# ----------------------------------------------------------------------
LANG = {
    'zh': dict(
        fonts=['Noto Sans CJK SC', 'Noto Sans CJK JP', 'AR PL UMing CN',
               'Droid Sans Fallback', 'DejaVu Sans'],
        title='时间为什么会变慢？',
        subtitle='灵感来自一个念头：「如果世界是一台模拟器，它会怎么省钱？」',
        band='论文大白话版 · Kai Wu',
        hero_t='时间变慢 = 这台计算机在「降频」：',
        hero_big=r'$\mathbf{\lambda^2 = 1 - S_{\mathrm{load}}/S_{\mathrm{max}}}$',
        hero_word='时钟快慢 = √( 1 − 实际计算负载 ÷ 全息屏幕容量 )',
        hero_sat='信息塞满（占用率 100% · 黑洞视界）→ **时间彻底停住**',
        hero_note='★ 常数消消乐：量子常数 ℏ、光速 c、引力常数 G 相除时全部抵消！只剩纯几何比值 $r_s/R$',
        colhdr_l='怎么来的 · 推导逻辑',
        colhdr_r='有多准 · 物理验证与突破',
        cards_l=[
            ('① 模拟器的省钱策略', 'chip',
             '不丢帧（怕穿模被看穿）＋用满预算（降频 = 慢动作）'),
            ('② 反直觉修正：看总量，不看脚下', 'sat',
             'GPS 卫星周围空荡荡，时钟反而更快——系统算的是整片区域的「大资产」（地球势阱），不看脚下'),
            ('③ 三条规则「凭空」长出公式', 'rules',
             '悬崖边运行（限流曲线）·信号速度恒定（网络延迟）·参考系跟着内容转 → 自然长出**平方根曲线**'),
        ],
        cards_r=[
            ('④ 攻克旋转黑洞', 'bh',
             '旋转不是额外负担，只是「齿轮效应」：θ 依赖全被**洛伦兹因子 γ**吸收，视界上全向均匀饱和**100%**'),
            ('⑤ 预测带电黑洞（最硬核）', 'bolt',
             '加「电荷记账」：扣减球外电场能 Q²/2R（麦克斯韦唯一确定）→ 先推导、后查答案——10 万个随机黑洞，误差**$4\\times10^{-16}$**；连视界位置都是规则自己算出来的'),
            ('⑥ 账本完美平账', 'check',
             '黑洞每抹掉 1 单位信息，付出的能量恰好卡在理论最低值——**兰道尔极限**'),
        ],
        quote1='结果定位：精确重述 + 可检验的启发式模型——不是证明',
        quote2='一句话总结：「如果宇宙是一台**不丢帧 + 用满预算**的模拟器，其时间膨胀曲线必然长这样——而广义相对论恰好如此。」',
        footer='论文与验证代码公开：github.com/purelover/load-capacity-time-dilation',
        # sizes
        s_title=30, s_sub=12.5, s_band=9.5,
        s_hero_t=14.5, s_hero_big=30, s_hero_word=13.5, s_hero_sat=12, s_hero_note=11,
        s_colhdr=15, s_card_t=12.2, s_card_b=9.8, card_line_h=0.022,
        s_quote1=12.5, s_quote2=13, s_footer=10,
        # geometry
        cards_top=0.550, cards_bottom=0.183,
    ),
    'en': dict(
        fonts=['DejaVu Sans'],
        title='Why Does Time Slow Down?',
        subtitle='Inspired by a thought: “If the world were a simulation, how would it save computing power?”',
        band='The paper in plain language · Kai Wu',
        hero_t='Time slowing down = the computer “throttling” its clock:',
        hero_big=r'$\mathbf{\lambda^2 = 1 - S_{\mathrm{load}}/S_{\mathrm{max}}}$',
        hero_word='clock rate = √( 1 − compute load ÷ screen capacity )',
        hero_sat='Packed full (100% load · the black-hole horizon) → **time stops**',
        hero_note='★ The constants cancel: ℏ, c, G all divide out — only the geometric ratio $r_s/R$ remains',
        colhdr_l='How the curve is derived',
        colhdr_r='How accurate · the physics checks',
        cards_l=[
            ('① The simulator’s cost-saving trick', 'chip',
             'Never drop frames (clipping would give it away) + spend the full budget (throttling = slow motion)'),
            ('② The counterintuitive fix: count the whole', 'sat',
             'GPS satellites sit in near-vacuum, yet their clocks run faster — the system prices the whole region’s “big asset” (Earth’s potential well), not the ground'),
            ('③ Three rules grow the formula', 'rules',
             'edge-of-stability running (the load curve) · fixed signal speed (network latency) · frames co-rotate with content → the **square-root curve** grows on its own'),
        ],
        cards_r=[
            ('④ Conquering rotating black holes', 'bh',
             'Spin adds no load — just a “gear effect”: all θ-dependence is absorbed into the **Lorentz factor γ**; the horizon saturates uniformly at **100%**'),
            ('⑤ Predicting charged black holes — hardest', 'bolt',
             'Add “charge accounting”: deduct the field energy outside, Q²/2R; derive first, check after — 100,000 black holes, max error **$4\\times10^{-16}$**; even the horizon’s location is computed by the rules'),
            ('⑥ The books balance perfectly', 'check',
             'Erasing information at a black hole costs exactly the theoretical minimum — the **Landauer limit**'),
        ],
        quote1='Where this lands: an exact rewriting + a testable heuristic model — not a proof',
        quote2='One-line takeaway: “If the universe is a **no-dropped-frames, full-budget** simulator, its time-dilation curve must look like this — and general relativity’s does.”',
        footer='Paper and verification code: github.com/purelover/load-capacity-time-dilation',
        # sizes
        s_title=30, s_sub=11, s_band=9.5,
        s_hero_t=13.5, s_hero_big=30, s_hero_word=13, s_hero_sat=11.5, s_hero_note=10.5,
        s_colhdr=13, s_card_t=10.8, s_card_b=8.6, card_line_h=0.0188,
        s_quote1=10.5, s_quote2=11.8, s_footer=10,
        # geometry
        cards_top=0.550, cards_bottom=0.183,
    ),
}

# ----------------------------------------------------------------------
# text engine: tokenize, bold spans, wrap, draw with inline **red bold**
# ----------------------------------------------------------------------
TOK_RE = re.compile(
    r'\$[^$]*\$'
    r'|[A-Za-z0-9²³⁰¹⁴⁵⁶⁷⁸⁹⁻⁺×÷·%Θθλγℏ=+_/\\\-.…,;:!?\'"“”‘’()\[\]&|#@~<>]+'
    r'|[\u4e00-\u9fff]'
    r'|[^\s]'
    r'|\s+')


def parse_rich(s):
    """Return list of tokens [(start, end, text, bold)] with ** markup resolved."""
    parts = s.split('**')
    spans, pos = [], 0
    for i, p in enumerate(parts):
        if i % 2 == 1:
            spans.append((pos, pos + len(p)))
        pos += len(p)
    toks = []
    for m in re.finditer(TOK_RE, s):
        txt = m.group()
        if txt.strip('*') == '':          # markup stars are not rendered
            continue
        st, en = m.span()
        bold = any(a <= st and en <= b for a, b in spans)
        toks.append([st, en, txt, bold])
    return toks


class Renderer(object):
    """Draws rich text with per-token color/weight; measures real extents."""

    def __init__(self, fig, ax):
        self.fig = fig
        self.ax = ax
        self.renderer = fig.canvas.get_renderer()
        self.px_per_x = fig.get_size_inches()[0] * fig.dpi
        self.checks = []

    def _w_px(self, s, size, weight):
        t = self.ax.text(0, 0, s, fontsize=size, fontweight=weight, color='k')
        bb = t.get_window_extent(self.renderer)
        t.remove()
        return bb.width

    def wrap(self, s, size, weight, maxw_x):
        toks = parse_rich(s)
        px_max = maxw_x * self.px_per_x
        lines, cur = [], []
        for tk in toks:
            if tk[2].isspace() and not cur:
                continue                       # drop leading spaces
            if tk[2].isspace():
                cur.append(tk)
                continue
            test = cur + [tk]
            w = sum(self._w_px(t[2], size, 'bold' if t[3] else weight)
                    for t in test)
            if cur and w > px_max:
                while cur and cur[-1][2].isspace():
                    cur.pop()
                if cur:
                    lines.append(cur)
                cur = [tk]
            else:
                cur.append(tk)
        while cur and cur[-1][2].isspace():
            cur.pop()
        if cur:
            lines.append(cur)
        return lines

    def draw_tokens(self, x, y, line, size, color, bold_color, weight, ha='left',
                    va='center', container=None):
        """Draw one wrapped line of pre-parsed tokens (bold spans preserved)."""
        total = 0.0
        for tk in line:
            wpx = self._w_px(tk[2], size, 'bold' if tk[3] else weight)
            total += wpx / self.px_per_x
        x0 = x - total / 2.0 if ha == 'center' else x
        xcur = x0
        for tk in line:
            c = bold_color if tk[3] else color
            w = 'bold' if tk[3] else weight
            a = self.ax.text(xcur, y, tk[2], fontsize=size, color=c, fontweight=w,
                             ha='left', va=va)
            xcur += self._w_px(tk[2], size, w) / self.px_per_x
            if container is not None:
                self.checks.append((a, container))

    def draw_rich(self, x, y, s, size, color=GRAY, bold_color=RED, weight='normal',
                  ha='left', va='center', maxw=None, line_h=0.024, container=None):
        """Draw (possibly wrapped) rich text; returns the number of lines used
        and the y where the block ended (useful for va='top' stacking)."""
        if maxw is not None:
            lines = self.wrap(s, size, weight, maxw)
        else:
            lines = [parse_rich(s)]
        if va == 'top':
            ycur = y
            step = -line_h
        else:
            ycur = y - (len(lines) - 1) * line_h / 2.0
            step = +line_h
        for line in lines:
            self.draw_tokens(x, ycur, line, size, color, bold_color, weight,
                             ha=ha, va=va, container=container)
            ycur += step
        return len(lines), ycur - step

    def draw_plain(self, x, y, s, size, color=GRAY, weight='normal', ha='left',
                   va='center', container=None):
        a = self.ax.text(x, y, s, fontsize=size, color=color, fontweight=weight,
                         ha=ha, va=va)
        if container is not None:
            self.checks.append((a, container))
        return a

    def report_overflows(self, tol=0.005):
        bad = []
        for a, (x0, y0, x1, y1) in self.checks:
            try:
                bb = a.get_window_extent(self.renderer)
                inv = self.ax.transAxes.inverted()
                (ax0, ay0), (ax1, ay1) = inv.transform([(bb.x0, bb.y0),
                                                        (bb.x1, bb.y1)])
                if ax0 < x0 - tol or ax1 > x1 + tol or ay0 < y0 - tol or ay1 > y1 + tol:
                    bad.append((a.get_text()[:40], (ax0, ay0, ax1, ay1), (x0, y0, x1, y1)))
            except Exception:
                pass
        return bad


# ----------------------------------------------------------------------
# icons (drawn in axes-fraction coordinates, aspect-corrected)
# ----------------------------------------------------------------------
def icon(ax, kind, x, y, sx):
    h = sx * ASP
    if kind == 'chip':
        ax.add_patch(FancyBboxPatch((x - sx / 2, y - h / 2), sx, h,
                                    boxstyle='round,pad=0,rounding_size=0.0025',
                                    fc=BLUE, ec='none', transform=ax.transAxes))
        ax.add_patch(Rectangle((x - 0.30 * sx, y - 0.30 * h), 0.60 * sx, 0.60 * h,
                               fc='#DCE6F2', ec='none', transform=ax.transAxes))
        for k in (-1, 0, 1):
            py = y + (k * 0.19 - 0.055) * h
            ax.add_patch(Rectangle((x - 0.62 * sx, py), 0.09 * sx, 0.11 * h,
                                   fc='#7E93B0', ec='none', transform=ax.transAxes))
            ax.add_patch(Rectangle((x + 0.53 * sx, py), 0.09 * sx, 0.11 * h,
                                   fc='#7E93B0', ec='none', transform=ax.transAxes))
    elif kind == 'sat':
        ax.add_patch(Rectangle((x - 0.42 * sx, y - 0.42 * h), 0.20 * sx, 0.84 * h,
                               fc=BLUE, ec='none', transform=ax.transAxes))
        ax.add_patch(Rectangle((x + 0.22 * sx, y - 0.42 * h), 0.20 * sx, 0.84 * h,
                               fc=BLUE, ec='none', transform=ax.transAxes))
        ax.add_patch(Rectangle((x - 0.15 * sx, y - 0.26 * h), 0.30 * sx, 0.52 * h,
                               fc='#C9D6E8', ec=BLUE, lw=0.8, transform=ax.transAxes))
        ax.plot([x, x], [y + 0.26 * h, y + 0.34 * h], color=BLUE, lw=0.8,
                transform=ax.transAxes)
        ax.add_patch(Circle((x, y + 0.41 * h), 0.085 * sx, fc='none', ec=BLUE,
                            lw=0.8, transform=ax.transAxes))
    elif kind == 'bh':
        ax.add_patch(Ellipse((x, y), 1.45 * sx, 0.56 * h, angle=18,
                             fc=ORANGE, ec='none', alpha=0.9, zorder=1,
                             transform=ax.transAxes))
        ax.add_patch(Circle((x, y), 0.33 * sx, fc='black', ec='none', zorder=2,
                            transform=ax.transAxes))
        ax.add_patch(FancyArrowPatch((x - 0.62 * sx, y - 0.34 * h),
                                     (x - 0.60 * sx, y + 0.34 * h),
                                     connectionstyle='arc3,rad=-0.42',
                                     arrowstyle='-|>', mutation_scale=9,
                                     lw=1.3, color=RED, zorder=3,
                                     transform=ax.transAxes))
    elif kind == 'rules':
        for k in (-1, 0, 1):
            py = y + k * 0.20 * h
            ax.add_patch(FancyBboxPatch((x - 0.31 * sx, py - 0.055 * h),
                                        0.62 * sx, 0.11 * h,
                                        boxstyle='round,pad=0,rounding_size=0.0015',
                                        fc=BLUE, ec='none', transform=ax.transAxes))
    elif kind == 'bolt':
        pts = [(x - 0.10 * sx, y + 0.36 * h), (x + 0.12 * sx, y + 0.10 * h),
               (x + 0.02 * sx, y + 0.10 * h), (x + 0.12 * sx, y - 0.36 * h),
               (x - 0.12 * sx, y - 0.02 * h), (x - 0.02 * sx, y - 0.02 * h)]
        ax.add_patch(Polygon(pts, closed=True, fc=GOLD, ec='none',
                             transform=ax.transAxes))
    elif kind == 'check':
        ax.add_patch(Circle((x, y), 0.30 * sx, fc='none', ec=GREEN, lw=1.4,
                            transform=ax.transAxes))
        ax.plot([x - 0.15 * sx, x - 0.04 * sx, x + 0.18 * sx],
                [y + 0.02 * h, y - 0.10 * h, y + 0.12 * h],
                color=GREEN, lw=1.6, transform=ax.transAxes)


# ----------------------------------------------------------------------
# poster builder
# ----------------------------------------------------------------------
def build(lang):
    L = LANG[lang]
    plt.rcParams['font.sans-serif'] = L['fonts']
    plt.rcParams['axes.unicode_minus'] = False

    fig = plt.figure(figsize=(8.27, 11.69), dpi=DPI)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis('off')
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    R = Renderer(fig, ax)

    def box(x0, y0, w, h, fc=LIGHT, ec='none', lw=0):
        ax.add_patch(FancyBboxPatch((x0, y0), w, h,
                                    boxstyle='round,pad=0,rounding_size=0.010',
                                    fc=fc, ec=ec, lw=lw, transform=ax.transAxes))

    # --- top band, title, subtitle -----------------------------------
    ax.add_patch(Rectangle((0, 0.962), 1, 0.038, color=NAVY, transform=ax.transAxes))
    R.draw_plain(0.96, 0.981, L['band'], L['s_band'], color='#C9D4E8',
                 ha='right', container=(0.0, 0.962, 1.0, 1.0))
    R.draw_plain(0.5, 0.915, L['title'], L['s_title'], color=NAVY, weight='bold',
                 ha='center', container=(0.05, 0.89, 0.95, 0.945))
    R.draw_plain(0.5, 0.869, L['subtitle'], L['s_sub'], color=GRAY, ha='center',
                 container=(0.05, 0.855, 0.95, 0.885))

    # --- hero formula zone -------------------------------------------
    hx0, hy0, hw, hh = 0.048, 0.632, 0.904, 0.216
    box(hx0, hy0, hw, hh, fc=GOLDBG)
    ax.add_patch(Rectangle((hx0, hy0), 0.014, hh, color=GOLD, transform=ax.transAxes))
    hero_rect = (hx0, hy0, hx0 + hw, hy0 + hh)
    R.draw_plain(0.5, hy0 + 0.190, L['hero_t'], L['s_hero_t'], color=NAVY,
                 weight='bold', ha='center', container=hero_rect)
    R.draw_plain(0.5, hy0 + 0.138, L['hero_big'], L['s_hero_big'], color=RED,
                 ha='center', container=hero_rect)
    R.draw_plain(0.5, hy0 + 0.092, L['hero_word'], L['s_hero_word'], color=NAVY,
                 weight='bold', ha='center', container=hero_rect)
    R.draw_rich(0.5, hy0 + 0.056, L['hero_sat'], L['s_hero_sat'], color=NAVY,
                bold_color=RED, weight='bold', ha='center',
                container=(hx0 + 0.02, hy0, hx0 + hw - 0.02, hy0 + 0.075))
    R.draw_rich(0.5, hy0 + 0.022, L['hero_note'], L['s_hero_note'], color=GOLD,
                bold_color=GOLD, weight='bold', ha='center',
                container=(hx0 + 0.02, hy0, hx0 + hw - 0.02, hy0 + 0.042))

    # --- two-column zone ---------------------------------------------
    col_l = (0.040, 0.465 - 0.040)      # x0, w
    col_r = (0.495, 0.960 - 0.495)
    hdr_y = 0.578
    cards_top = L['cards_top']
    cards_bottom = L['cards_bottom']

    def column(x0, w, header, items, hdr_icon):
        # header
        icon(ax, hdr_icon, x0 + 0.022, hdr_y, 0.026)
        R.draw_plain(x0 + 0.046, hdr_y, header, L['s_colhdr'], color=NAVY,
                     weight='bold', container=(x0, hdr_y - 0.02, x0 + w, hdr_y + 0.022))
        ax.plot([x0 + 0.046, x0 + w - 0.02], [hdr_y - 0.024, hdr_y - 0.024],
                color=NAVY, lw=0.9, alpha=0.45, transform=ax.transAxes)
        # cards
        pad_t, t_lh, gap_tb, pad_b = 0.015, 0.024, 0.011, 0.013
        body_w = w - 0.056 - 0.024
        y = cards_top
        rects = []
        for (title, icon_kind, body) in items:
            tlines = R.wrap(title, L['s_card_t'], 'bold', body_w)
            blines = R.wrap(body, L['s_card_b'], 'normal', body_w)
            h = pad_t + len(tlines) * t_lh + gap_tb + len(blines) * L['card_line_h'] + pad_b
            rects.append((x0, y, w, h, tlines, blines, title, icon_kind, body))
            y -= h + 0.007
        return rects

    rects_l = column(*col_l, L['colhdr_l'], L['cards_l'], 'chip')
    rects_r = column(*col_r, L['colhdr_r'], L['cards_r'], 'bh')

    def draw_column(rects):
        for (x0, y0, w, h, tlines, blines, title, icon_kind, body) in rects:
            box(x0, y0, w, h, fc=LIGHT)
            ax.add_patch(Rectangle((x0, y0), 0.008, h, color=BLUE,
                                   transform=ax.transAxes))
            icon(ax, icon_kind, x0 + 0.030, y0 + h - 0.026, 0.026)
            # title lines (bold navy)
            yt = y0 + h - 0.015
            for line in tlines:
                R.draw_plain(x0 + 0.056, yt, ''.join(t[2] for t in line),
                             L['s_card_t'], color=NAVY, weight='bold',
                             container=(x0 + 0.052, y0, x0 + w - 0.02, y0 + h))
                yt -= 0.024
            # body lines (rich, gray + red bold)
            yb = y0 + h - 0.015 - len(tlines) * 0.024 - 0.011
            for line in blines:
                R.draw_rich(x0 + 0.056, yb, ''.join(t[2] for t in line),
                            L['s_card_b'], color=GRAY, bold_color=RED,
                            ha='left', va='center',
                            container=(x0 + 0.052, y0, x0 + w - 0.02, y0 + h))
                yb -= L['card_line_h']
        # arrows between cards
        cx = rects[0][0] + rects[0][2] / 2
        for i in range(len(rects) - 1):
            y_lo = rects[i][1] - 0.001
            y_hi = rects[i + 1][1] + rects[i + 1][3] + 0.001
            ax.add_patch(FancyArrowPatch((cx, y_lo), (cx, y_hi),
                                         arrowstyle='-|>', mutation_scale=10,
                                         lw=1.4, color=BLUE,
                                         transform=ax.transAxes))

    draw_column(rects_l)
    draw_column(rects_r)
    geom_warnings = []
    for name, rects in (('left', rects_l), ('right', rects_r)):
        bottom = rects[-1][1]
        if bottom < cards_bottom:
            geom_warnings.append(
                f'{name} column bottom {bottom:.3f} < zone bottom {cards_bottom}')
    # connector between the two header rows
    ax.add_patch(FancyArrowPatch((0.452, hdr_y), (0.489, hdr_y),
                                 arrowstyle='-|>', mutation_scale=10,
                                 lw=1.4, color=BLUE, transform=ax.transAxes))

    # --- bottom takeaway zone ----------------------------------------
    qx0, qy0, qw, qh = 0.048, 0.052, 0.904, 0.118
    box(qx0, qy0, qw, qh, fc=LIGHT)
    ax.add_patch(Rectangle((qx0, qy0), 0.014, qh, color=NAVY, transform=ax.transAxes))
    q_rect = (qx0, qy0, qx0 + qw, qy0 + qh)
    R.draw_rich(0.5, qy0 + 0.089, L['quote1'], L['s_quote1'], color=NAVY,
                bold_color=NAVY, weight='bold', ha='center',
                container=(qx0 + 0.03, qy0 + 0.055, qx0 + qw - 0.03, qy0 + qh - 0.008))
    R.draw_rich(0.5, qy0 + 0.054, L['quote2'], L['s_quote2'], color=NAVY,
                bold_color=RED, weight='bold', ha='center',
                maxw=qw - 0.09, line_h=0.026,
                container=(qx0 + 0.03, qy0, qx0 + qw - 0.03, qy0 + 0.088))

    # --- footer --------------------------------------------------------
    ax.add_patch(Rectangle((0, 0.0), 1, 0.046, color=NAVY, transform=ax.transAxes))
    R.draw_plain(0.5, 0.023, L['footer'], L['s_footer'], color=WHITE, ha='center',
                 container=(0.02, 0.0, 0.98, 0.046))

    out = os.path.join(OUT_DIR, f'poster-{lang}.png')
    fig.savefig(out, dpi=DPI, facecolor='white')
    plt.close(fig)
    return out, R.report_overflows(), geom_warnings


def main():
    for lang in ('zh', 'en'):
        out, overflows, geoms = build(lang)
        print(f'[{lang}] saved {out}')
        if overflows:
            print(f'[{lang}] OVERFLOW WARNINGS: {len(overflows)}')
            for text, bbox, rect in overflows:
                print('   text=%r bbox=(%.3f,%.3f,%.3f,%.3f) rect=%s'
                      % (text, *bbox, tuple(round(v, 3) for v in rect)))
        else:
            print(f'[{lang}] all text fits inside its container')
        for g in geoms:
            print(f'[{lang}] GEOMETRY WARNING: {g}')


if __name__ == '__main__':
    main()
