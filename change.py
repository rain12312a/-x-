import re
import os
import tkinter as tk
from tkinter import ttk, messagebox

# ============================================================
# 配置
# ============================================================
MAX_LEVEL = 30
MAX_SKILL_LEVEL = 20

GROW_TEMPLATES = {
    "default":      {"hp":120,"mp":80, "shenfa":1,"bili":1,"gengu":1,"fuyuan":1,"dingli":1,"quanzhang":1,"jianfa":1,"daofa":1,"qimen":1,"wuxing":0},
    "主角":          {"hp":120,"mp":80, "shenfa":2,"bili":2,"gengu":2,"fuyuan":2,"dingli":2,"quanzhang":2,"jianfa":2,"daofa":2,"qimen":2,"wuxing":0},
    "无门派主角":    {"hp":120,"mp":80, "shenfa":3,"bili":3,"gengu":3,"fuyuan":3,"dingli":3,"quanzhang":2,"jianfa":2,"daofa":2,"qimen":2,"wuxing":2},
    "肉盾":          {"hp":200,"mp":40, "shenfa":1,"bili":2,"gengu":2,"fuyuan":0,"dingli":3,"quanzhang":2,"jianfa":0,"daofa":0,"qimen":0,"wuxing":0},
    "剑侠":          {"hp":120,"mp":60, "shenfa":2,"bili":1,"gengu":1,"fuyuan":1,"dingli":3,"quanzhang":0,"jianfa":4,"daofa":0,"qimen":0,"wuxing":0},
    "刀客":          {"hp":120,"mp":60, "shenfa":3,"bili":2,"gengu":1,"fuyuan":1,"dingli":1,"quanzhang":0,"jianfa":0,"daofa":4,"qimen":0,"wuxing":0},
    "宗师":          {"hp":120,"mp":80, "shenfa":2,"bili":2,"gengu":3,"fuyuan":3,"dingli":3,"quanzhang":2,"jianfa":2,"daofa":2,"qimen":2,"wuxing":0},
    "大侠":          {"hp":200,"mp":50, "shenfa":2,"bili":2,"gengu":3,"fuyuan":1,"dingli":2,"quanzhang":3,"jianfa":0,"daofa":0,"qimen":0,"wuxing":0},
    "剑掌双修":      {"hp":150,"mp":80, "shenfa":1,"bili":2,"gengu":2,"fuyuan":1,"dingli":2,"quanzhang":3,"jianfa":3,"daofa":0,"qimen":0,"wuxing":0},
    "小龙女":        {"hp":120,"mp":80, "shenfa":4,"bili":2,"gengu":2,"fuyuan":2,"dingli":2,"quanzhang":2,"jianfa":3,"daofa":0,"qimen":3,"wuxing":5},
    "段誉":          {"hp":120,"mp":120,"shenfa":3,"bili":2,"gengu":3,"fuyuan":5,"dingli":1,"quanzhang":3,"jianfa":0,"daofa":0,"qimen":0,"wuxing":0},
    "女子":          {"hp":100,"mp":80, "shenfa":2,"bili":1,"gengu":1,"fuyuan":2,"dingli":1,"quanzhang":1,"jianfa":1,"daofa":1,"qimen":1,"wuxing":0},
    "奇门":          {"hp":120,"mp":80, "shenfa":3,"bili":1,"gengu":1,"fuyuan":1,"dingli":1,"quanzhang":0,"jianfa":0,"daofa":0,"qimen":4,"wuxing":0},
    "韦小宝":        {"hp":80, "mp":50, "shenfa":1,"bili":0,"gengu":1,"fuyuan":5,"dingli":1,"quanzhang":1,"jianfa":1,"daofa":1,"qimen":1,"wuxing":0},
    "内家":          {"hp":140,"mp":100,"shenfa":1,"bili":1,"gengu":2,"fuyuan":1,"dingli":1,"quanzhang":1,"jianfa":1,"daofa":1,"qimen":1,"wuxing":0},
    "内功大师":      {"hp":180,"mp":150,"shenfa":1,"bili":1,"gengu":4,"fuyuan":2,"dingli":3,"quanzhang":1,"jianfa":1,"daofa":1,"qimen":1,"wuxing":0},
    "医生":          {"hp":120,"mp":80, "shenfa":1,"bili":1,"gengu":4,"fuyuan":4,"dingli":2,"quanzhang":0,"jianfa":0,"daofa":0,"qimen":0,"wuxing":0},
    "毒医":          {"hp":100,"mp":80, "shenfa":1,"bili":1,"gengu":3,"fuyuan":3,"dingli":2,"quanzhang":1,"jianfa":0,"daofa":0,"qimen":1,"wuxing":1},
    "刀剑双杀":      {"hp":120,"mp":60, "shenfa":3,"bili":1,"gengu":1,"fuyuan":1,"dingli":2,"quanzhang":0,"jianfa":3,"daofa":3,"qimen":0,"wuxing":0},
    "乔峰":          {"hp":200,"mp":50, "shenfa":0,"bili":2,"gengu":0,"fuyuan":0,"dingli":0,"quanzhang":0,"jianfa":0,"daofa":0,"qimen":0,"wuxing":0},
}

ATTR_MAP = {
    "hp": "maxhp", "mp": "maxmp",
    "shenfa": "shenfa", "bili": "bili", "gengu": "gengu",
    "fuyuan": "fuyuan", "dingli": "dingli",
    "quanzhang": "quanzhang", "jianfa": "jianfa",
    "daofa": "daofa", "qimen": "qimen", "wuxing": "wuxing",
}

# ============================================================
# 核心逻辑
# ============================================================
def get_save_path():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        'gamedata', 'saves', 'fastsave')

def scan_roles(content):
    """扫描存档中的所有角色"""
    roles = []
    for m in re.finditer(r'<Roles\s.*?</Roles>', content):
        r = m.group(0)
        key = re.search(r'key="([^"]*)"', r)
        gt = re.search(r'grow_template="([^"]*)"', r)
        lv = re.search(r'grow_template="[^"]*"\s+level="(\d+)"', r)
        if not lv:
            # 无 grow_template 但仍有 level
            lv = re.search(r'<Roles\s[^>]*?level="(\d+)"', r)
        name = re.search(r'name="([^"]*)"', r)

        roles.append({
            'key': key.group(1) if key else '?',
            'name': name.group(1) if name else '?',
            'level': int(lv.group(1)) if lv else 0,
            'template': gt.group(1) if gt else None,
            'known': gt is not None and gt.group(1) in GROW_TEMPLATES,
        })
    return roles

def process_save(content, max_lv):
    """处理存档：角色满级 + 武功满级"""
    def upgrade_role(match):
        role_str = match.group(0)
        lv_match = re.search(r'grow_template="([^"]*)"\s+level="(\d+)"', role_str)
        if not lv_match:
            return role_str
        gt_name = lv_match.group(1)
        current_level = int(lv_match.group(2))
        if current_level >= max_lv:
            return role_str
        level_diff = max_lv - current_level

        gt = GROW_TEMPLATES.get(gt_name, GROW_TEMPLATES["default"])
        for gt_attr, save_attr in ATTR_MAP.items():
            growth = gt.get(gt_attr, 0) * level_diff
            if growth != 0:
                def _repl(m, g=growth, sa=save_attr):
                    return f'{sa}="{int(m.group(1)) + g}"'
                role_str = re.sub(rf'{save_attr}="(\d+)"', _repl, role_str, count=1)

        lp_growth = level_diff * 2
        if lp_growth != 0:
            def _repl_lp(m, g=lp_growth):
                return f'leftpoint="{int(m.group(1)) + g}"'
            role_str = re.sub(r'leftpoint="(\d+)"', _repl_lp, role_str, count=1)

        role_str = re.sub(r' level="\d+"', f' level="{max_lv}"', role_str, count=1)
        return role_str

    content = re.sub(r'<Roles\s.*?</Roles>', upgrade_role, content)
    content = re.sub(
        r'(<(?:i|sk) equipped="\d+" )level="\d+"( exp="\d+" name="[^"]*"\s*/>)',
        r'\1level="' + str(MAX_SKILL_LEVEL) + r'"\2', content)
    return content

# ============================================================
# GUI
# ============================================================
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("金庸群侠传X · 一键满级")
        self.root.resizable(False, False)
        self.save_path = get_save_path()

        # -- 顶部：存档路径 --
        f1 = ttk.Frame(root, padding=5)
        f1.pack(fill=tk.X)
        ttk.Label(f1, text="存档:").pack(side=tk.LEFT)
        self.path_var = tk.StringVar(value=self.save_path)
        ttk.Entry(f1, textvariable=self.path_var, width=55).pack(side=tk.LEFT, padx=5)

        # -- 等级设置 --
        f2 = ttk.Frame(root, padding=5)
        f2.pack(fill=tk.X)
        ttk.Label(f2, text="目标等级:").pack(side=tk.LEFT)
        self.lv_var = tk.IntVar(value=MAX_LEVEL)
        ttk.Spinbox(f2, from_=1, to=99, textvariable=self.lv_var, width=5).pack(side=tk.LEFT, padx=5)
        ttk.Label(f2, text="武功等级:").pack(side=tk.LEFT)
        self.sk_var = tk.IntVar(value=MAX_SKILL_LEVEL)
        ttk.Spinbox(f2, from_=1, to=20, textvariable=self.sk_var, width=5).pack(side=tk.LEFT, padx=5)
        ttk.Button(f2, text="刷新", command=self.refresh).pack(side=tk.RIGHT, padx=3)

        # -- 角色列表 --
        f3 = ttk.Frame(root, padding=5)
        f3.pack(fill=tk.BOTH, expand=True)
        cols = ("角色", "模板", "当前等级", "目标等级")
        self.tree = ttk.Treeview(f3, columns=cols, show="headings", height=8)
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=100 if c != "角色" else 120)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        sb = ttk.Scrollbar(f3, orient=tk.VERTICAL, command=self.tree.yview)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=sb.set)

        # -- 一键满级按钮 --
        f4 = ttk.Frame(root, padding=5)
        f4.pack(fill=tk.X)
        self.btn = ttk.Button(f4, text="⚡ 一键满级", command=self.do_upgrade)
        self.btn.pack(fill=tk.X, ipady=5)

        # -- 状态栏 --
        self.status = tk.StringVar(value="就绪")
        ttk.Label(root, textvariable=self.status, relief=tk.SUNKEN, anchor=tk.W).pack(fill=tk.X)

        self.refresh()

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        if not os.path.exists(self.path_var.get()):
            self.status.set("存档文件不存在！")
            return
        with open(self.path_var.get(), 'r', encoding='utf-8') as f:
            content = f.read()
        roles = scan_roles(content)
        target = self.lv_var.get()
        for r in roles:
            t = r['template'] if r['template'] is not None else '—'
            if r['template'] and not r['known']:
                t += ' (default)'
            new_lv = min(target, max(r['level'], target)) if r['template'] is not None else r['level']
            self.tree.insert('', tk.END, values=(r['name'], t, r['level'], new_lv))
        self.status.set(f"共 {len(roles)} 个角色")

    def do_upgrade(self):
        path = self.path_var.get()
        if not os.path.exists(path):
            messagebox.showerror("错误", "存档文件不存在！")
            return

        target_lv = self.lv_var.get()
        sk_lv = self.sk_var.get()

        with open(path, 'r', encoding='utf-8') as f:
            original = f.read()

        content = process_save(original, target_lv)
        # 动态替换武功等级
        content = re.sub(
            r'(<(?:i|sk) equipped="\d+" )level="\d+"( exp="\d+" name="[^"]*"\s*/>)',
            r'\1level="' + str(sk_lv) + r'"\2', content)

        if content == original:
            self.status.set("无需修改（已满级或无 grow_template 角色）")
            return

        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)

        self.status.set("修改完成！")
        self.btn.configure(text="✅ 已满级")
        self.root.after(2000, lambda: self.btn.configure(text="⚡ 一键满级"))
        self.refresh()

root = tk.Tk()
App(root)
root.mainloop()

