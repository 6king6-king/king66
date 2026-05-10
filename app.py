import streamlit as st
import pandas as pd
import json
import os
import time
import numpy as np
from datetime import datetime
import random
from typing import Dict, List, Any
from PIL import Image  
import pytesseract   

if os.name == 'nt':  # Windows
    pytesseract.pytesseract.tesseract_cmd = r'E:\test\xc\tesseract.exe'
# ================= 文件路径配置 =================
DATA_PATHS = {
    "users": "users.json",
    "wrong_records": "wrong_records.json",
    "practice_stats": "practice_stats.json",
    "risk_rules": "data/risk_rules.json",
    "practice_data": "data/practice_data.json",
    "compliance_rules": "data/compliance_rules.json",
    "forbidden_words": "data/forbidden_words.json",
    "violation_cases": "data/violation_cases.json",
    "icon_groups": "data/icon_groups.json"
}

# 默认数据（仅用于初始化文件，不占用主代码空间）
DEFAULT_USERS = {"student": "123456", "teacher": "admin", "admin": "admin123"}
DEFAULT_COMPLIANCE_RULES = {
    "充电宝(3C)": {
        "欧盟": ["CE认证", "RoHS环保指令", "UN38.3运输鉴定", "电池指令", "包装需有垃圾桶标"],
        "美国": ["FCC认证", "CPSIA铅含量", "加州65提案", "必须贴警告标", "UL测试报告"],
        "东南亚": ["PSE认证(日本)", "双语标签(英+当地语)", "MSDS化学品安全书"]
    },
    "口红(美妆)": {
        "欧盟": ["CPNP备案", "全成分标注(INCI)", "防腐剂限量", "重金属检测报告", "责任人地址"],
        "美国": ["FDA化妆品注册(VoA)", "英文标签", "莫诺索夫法案合规", "禁用色素添加剂"],
        "东南亚": ["东盟化妆品指令", "生产卫生许可证", "禁止宣称医疗功效"]
    },
    "纯棉T恤(服装)": {
        "欧盟": ["纺织品标签法规(EU 1007/2011)", "REACH法规(偶氮染料)", "洗涤护理符号", "原产地标"],
        "美国": ["CPSIA儿童产品证书(CPC)", "纤维成分标注(FTC)", "易燃性标准(16 CFR 1610)", "追踪标"],
        "东南亚": ["无侵权图案(迪士尼/IP)", "棉含量百分比标", "耐用吊牌"]
    },
    "蓝牙耳机": {
        "欧盟": ["CE认证", "RED指令", "RoHS", "WEEE回收标志"],
        "美国": ["FCC ID", "蓝牙资格认证(BQB)"],
        "东南亚": ["SRRC认证(中国)", "IMDA认证(新加坡)"]
    },
    "童装": {
        "欧盟": ["REACH法规", "EN 14682安全标准", "小部件拉力测试"],
        "美国": ["CPSIA儿童产品证书(CPC)", "易燃性标准16 CFR 1615/1616", "追踪标签"],
        "东南亚": ["无偶氮染料", "甲醛含量限值"]
    }
}
DEFAULT_FORBIDDEN_WORDS = [
    "最有效", "第一", "绝对", "100%", "永不", "特效", "100%有效", "最", "顶级",
    "独一无二", "完全", "彻底", "神奇", "万能", "最佳", "最新", "最先进", "首选",
    "销量冠军", "市场唯一", "专利", "专家推荐", "国家级", "世界级", "最高级",
    "最大", "唯一", "完全", "彻底", "神奇", "最佳", "最新", "最先进", "第一"
]
DEFAULT_VIOLATION_CASES = [
    {"商品": "充电宝", "市场": "欧盟", "违规点": "无UN38.3认证", "后果": "海关扣押/退运", "风险等级": "高"},
    {"商品": "美白精华", "市场": "美国", "违规点": "文案含'治疗色斑'", "后果": "被认定为药物下架", "风险等级": "中"},
    {"商品": "印有米老鼠T恤", "市场": "全球", "违规点": "未获迪士尼授权", "后果": "店铺封禁(TRO)", "风险等级": "极高"},
    {"商品": "蓝牙耳机", "市场": "亚马逊", "违规点": "标题含'Best Seller'", "后果": "链接变狗/降权", "风险等级": "低"}
]
DEFAULT_ICON_GROUPS = {
    "安全类": ["🔒", "🛡️", "🔑", "✅", "⚠️", "⚡"],
    "教育类": ["🎓", "📋", "📊", "🔍", "📝", "🧠"],
    "商务类": ["💼", "🌍", "📦", "🎯", "💡", "📌"],
    "通知类": ["🔔", "⭐", "✅", "⚠️", "⚡", "🎯"]
}

# ================= 配置加载器 =================
class ConfigLoader:
    @staticmethod
    def init_config_files():
        if not os.path.exists(DATA_PATHS["users"]):
            with open(DATA_PATHS["users"], "w", encoding="utf-8") as f:
                json.dump(DEFAULT_USERS, f, ensure_ascii=False, indent=2)
        if not os.path.exists(DATA_PATHS["wrong_records"]):
            with open(DATA_PATHS["wrong_records"], "w", encoding="utf-8") as f:
                json.dump({}, f)
        if not os.path.exists(DATA_PATHS["practice_stats"]):
            with open(DATA_PATHS["practice_stats"], "w", encoding="utf-8") as f:
                json.dump({}, f)
        os.makedirs(os.path.dirname(DATA_PATHS["compliance_rules"]), exist_ok=True)
        if not os.path.exists(DATA_PATHS["compliance_rules"]):
            with open(DATA_PATHS["compliance_rules"], "w", encoding="utf-8") as f:
                json.dump(DEFAULT_COMPLIANCE_RULES, f, ensure_ascii=False, indent=2)
        if not os.path.exists(DATA_PATHS["forbidden_words"]):
            with open(DATA_PATHS["forbidden_words"], "w", encoding="utf-8") as f:
                json.dump(DEFAULT_FORBIDDEN_WORDS, f, ensure_ascii=False, indent=2)
        if not os.path.exists(DATA_PATHS["violation_cases"]):
            with open(DATA_PATHS["violation_cases"], "w", encoding="utf-8") as f:
                json.dump(DEFAULT_VIOLATION_CASES, f, ensure_ascii=False, indent=2)
        if not os.path.exists(DATA_PATHS["icon_groups"]):
            with open(DATA_PATHS["icon_groups"], "w", encoding="utf-8") as f:
                json.dump(DEFAULT_ICON_GROUPS, f, ensure_ascii=False, indent=2)

    @staticmethod
    @st.cache_data
    def load_compliance_rules() -> Dict:
        with open(DATA_PATHS["compliance_rules"], "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    @st.cache_data
    def load_forbidden_words() -> List[str]:
        with open(DATA_PATHS["forbidden_words"], "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    @st.cache_data
    def load_violation_cases() -> List[Dict]:
        with open(DATA_PATHS["violation_cases"], "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    @st.cache_data
    def load_icon_groups() -> Dict:
        with open(DATA_PATHS["icon_groups"], "r", encoding="utf-8") as f:
            return json.load(f)

# ================= 数据持久化 =================
class DataPersistence:
    @staticmethod
    def load_json(file_path: str) -> Dict:
        if not os.path.exists(file_path):
            return {}
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def save_json(file_path: str, data: Dict):
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @classmethod
    def load_users(cls) -> Dict:
        return cls.load_json(DATA_PATHS["users"])

    @classmethod
    def save_users(cls, data: Dict):
        cls.save_json(DATA_PATHS["users"], data)

    @classmethod
    def load_wrong_records(cls) -> Dict:
        return cls.load_json(DATA_PATHS["wrong_records"])

    @classmethod
    def save_wrong_records(cls, data: Dict):
        cls.save_json(DATA_PATHS["wrong_records"], data)

    @classmethod
    def load_practice_stats(cls) -> Dict:
        return cls.load_json(DATA_PATHS["practice_stats"])

    @classmethod
    def save_practice_stats(cls, data: Dict):
        cls.save_json(DATA_PATHS["practice_stats"], data)

    @staticmethod
    def load_risk_rules() -> List[Dict]:
        if not os.path.exists(DATA_PATHS["risk_rules"]):
            st.error("风险规则文件不存在，请提供 data/risk_rules.json")
            return []
        with open(DATA_PATHS["risk_rules"], "r", encoding="utf-8") as f:
            return json.load(f).get("rules", [])

    @staticmethod
    def load_practice_sets() -> List[Dict]:
        if not os.path.exists(DATA_PATHS["practice_data"]):
            st.error("练习题文件不存在，请提供 data/practice_data.json")
            return []
        with open(DATA_PATHS["practice_data"], "r", encoding="utf-8") as f:
            return json.load(f).get("sets", [])

# ================= 页面配置与样式 =================
def setup_page_config():
    st.set_page_config(page_title="跨境电商合规实训平台", page_icon="🛡️", layout="wide", initial_sidebar_state="collapsed")

def inject_custom_css():
    """注入自定义CSS - 从外部文件读取"""
    try:
        with open("style.css", "r", encoding="utf-8") as f:
            css_style = f.read()
        st.markdown(f"<style>{css_style}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        # 如果文件不存在，使用备用样式
        st.markdown("""
        <style>
        .stApp { background: linear-gradient(135deg, #f5f7fa 0%, #e4edf5 100%); }
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        .stButton>button { border-radius: 8px; }
        </style>
        """, unsafe_allow_html=True)

# ================= 会话状态管理 =================
def init_session_state():
    defaults = {
        "logged_in": False, "username": "", "is_admin": False,
        "captcha_icons": [], "correct_captcha": "", "selected_captcha": "",
        "show_admin_panel": False, "current_admin_tab": "用户管理",
        "current_main_tab": "🏠 首页",  # 将默认改为"🏠 首页"
        "show_sidebar": True
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v
# ================= 验证码功能 =================
class CaptchaManager:
    @staticmethod
    def generate_captcha():
        groups = ConfigLoader.load_icon_groups()
        group_names = list(groups.keys())
        selected_group = random.choice(group_names)
        icons = groups[selected_group]
        captcha_icons = random.sample(icons, 3)
        correct = random.choice(captcha_icons)
        random.shuffle(captcha_icons)
        st.session_state.captcha_icons = captcha_icons
        st.session_state.correct_captcha = correct
        st.session_state.selected_captcha = ""

    @staticmethod
    def select_icon(icon: str):
        st.session_state.selected_captcha = icon

    @staticmethod
    def render():
        st.markdown("### 🔐 图标验证")
        st.markdown("请从下方选择与上方图标属于同一类的图标")
        if not st.session_state.captcha_icons:
            CaptchaManager.generate_captcha()
        st.markdown(f"<div style='text-align: center; font-size: 3em; margin-bottom: 15px;'>{st.session_state.correct_captcha}</div>", unsafe_allow_html=True)
        for i, icon in enumerate(st.session_state.captcha_icons):
            st.button(icon, key=f"captcha_{i}", on_click=CaptchaManager.select_icon, args=(icon,), use_container_width=True)
        if st.button("🔄 刷新验证码", use_container_width=True):
            CaptchaManager.generate_captcha()
            st.rerun()

# ================= 登录界面 =================
def render_login():
    st.markdown("<h1 style='text-align: center;'>🛡️ 跨境电商合规风控实训平台</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>AI知识图谱驱动 · 真实可上线版 · 全流程合规检测</p>", unsafe_allow_html=True)
    
    # 使用状态来切换登录/注册模式
    if "login_mode" not in st.session_state:
        st.session_state.login_mode = "login"  # login 或 register
    
    # 主表单区域
    with st.columns([1,2,1])[1]:
        # 判断显示登录还是注册表单
        if st.session_state.login_mode == "login":
            # ========== 登录表单 ==========
            users = DataPersistence.load_users()
            username = st.text_input("👤 用户名", key="login_user", placeholder="请输入用户名")
            pwd = st.text_input("🔒 密码", type="password", key="login_pwd", placeholder="请输入密码")
            # 按钮区域（登录按钮 + 切换注册）
            col1, col2 = st.columns([3, 1])
            with col1:
                if st.button("🔐 登录", type="primary", use_container_width=True):
                    if st.session_state.selected_captcha != st.session_state.correct_captcha:
                        st.error("❌ 图标验证错误")
                    elif username in users and users[username] == pwd:
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.session_state.is_admin = (username == "adminking")
                        st.success(f"🎉 欢迎 {username}")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ 账号或密码错误")
            with col2:
                if st.button("📝 注册", use_container_width=True):
                    st.session_state.login_mode = "register"
                    st.rerun()
        
        else:
            # ========== 注册表单 ==========
            st.markdown("""
            <div style="background-color: #e8f5e9; border-left: 4px solid #4caf50; padding: 12px; border-radius: 8px; margin-bottom: 20px;">
            <p style="margin: 0;">📝 填写下方信息，免费注册新账号</p>
            </div>
            """, unsafe_allow_html=True)
            
            new_username = st.text_input("👤 用户名", key="reg_user", placeholder="请输入用户名（3-20个字符）")
            new_password = st.text_input("🔒 密码", type="password", key="reg_pwd", placeholder="请输入密码（6-20个字符）")
            confirm_password = st.text_input("🔒 确认密码", type="password", key="reg_confirm", placeholder="请再次输入密码")
            
            col1, col2 = st.columns([3, 1])
            with col1:
                if st.button("✅ 注册", type="primary", use_container_width=True):
                    # 验证
                    if st.session_state.selected_captcha != st.session_state.correct_captcha:
                        st.error("❌ 图标验证错误")
                    elif not new_username or not new_password:
                        st.error("❌ 用户名和密码不能为空")
                    elif len(new_username) < 3 or len(new_username) > 20:
                        st.error("❌ 用户名长度应为3-20个字符")
                    elif len(new_password) < 6 or len(new_password) > 20:
                        st.error("❌ 密码长度应为6-20个字符")
                    elif new_password != confirm_password:
                        st.error("❌ 两次输入的密码不一致")
                    else:
                        users = DataPersistence.load_users()
                        if new_username in users:
                            st.error("❌ 用户名已存在，请选择其他用户名")
                        else:
                            users[new_username] = new_password
                            DataPersistence.save_users(users)
                            
                            stats = DataPersistence.load_practice_stats()
                            if new_username not in stats:
                                stats[new_username] = {"total": 0, "correct": 0}
                                DataPersistence.save_practice_stats(stats)
                            
                            st.success(f"✅ 注册成功！欢迎 {new_username}")
                            st.balloons()
                            time.sleep(1)
                            
                            st.session_state.logged_in = True
                            st.session_state.username = new_username
                            st.session_state.is_admin = False
                            st.rerun()
            with col2:
                if st.button("← 返回登录", use_container_width=True):
                    st.session_state.login_mode = "login"
                    st.rerun()
# ================= 顶部导航栏 =================
def render_top_navbar():
    c1, c2 = st.columns([3,1])
    with c1:
        st.markdown("<div class='nav-title'>🛡️ 跨境电商合规实训平台</div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div style='text-align: right;'>👤 欢迎, {st.session_state.username}</div>", unsafe_allow_html=True)
    st.markdown("---")
    
    cols = st.columns(9)  # 从8列改为9列（增加首页）
    main_tabs = ["🏠 首页", "知识库", "风险检测", "练习中心", "学习报告"]  # 添加首页
    for i, tab in enumerate(main_tabs):
        with cols[i]:
            active = (st.session_state.current_main_tab == tab and not st.session_state.show_admin_panel)
            if st.button(tab, key=f"main_{tab}", type="primary" if active else "secondary", use_container_width=True):
                st.session_state.current_main_tab = tab
                st.session_state.show_admin_panel = False
                st.rerun()
    
    if st.session_state.is_admin:
        admin_tabs = ["用户管理", "数据查看", "系统设置"]
        offset = len(main_tabs)
        for i, tab in enumerate(admin_tabs):
            with cols[offset + i]:
                active = (st.session_state.show_admin_panel and st.session_state.current_admin_tab == tab)
                if st.button(tab, key=f"admin_{tab}", type="primary" if active else "secondary", use_container_width=True):
                    st.session_state.current_admin_tab = tab
                    st.session_state.show_admin_panel = True
                    st.rerun()
    
    with cols[-1]:
        if st.button("🚪 退出登录", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()
    st.markdown("---")
# ================= 管理员面板 =================
def render_admin_panel():
    st.markdown("<h1>🔧 管理后台</h1>", unsafe_allow_html=True)
    tab = st.session_state.current_admin_tab
    if tab == "用户管理":
        render_user_management()
    elif tab == "数据查看":
        render_data_view()
    elif tab == "系统设置":
        render_system_settings()

def render_user_management():
    st.markdown("#### 👥 用户账户管理")
    users = DataPersistence.load_users()
    st.dataframe(pd.DataFrame(list(users.items()), columns=["用户名","密码"]), use_container_width=True)
    st.markdown("##### ➕ 添加用户")
    new_user = st.text_input("用户名", key="new_u")
    new_pwd = st.text_input("密码", type="password", key="new_p")
    if st.button("添加"):
        if new_user and new_pwd:
            users[new_user] = new_pwd
            DataPersistence.save_users(users)
            st.success(f"用户 {new_user} 已添加")
            st.rerun()
    st.markdown("##### ❌ 删除用户")
    del_user = st.selectbox("选择用户", list(users.keys()), key="del_u")
    if st.button("删除"):
        if del_user != "admin":
            del users[del_user]
            DataPersistence.save_users(users)
            wrong = DataPersistence.load_wrong_records()
            if del_user in wrong:
                del wrong[del_user]
                DataPersistence.save_wrong_records(wrong)
            stats = DataPersistence.load_practice_stats()
            if del_user in stats:
                del stats[del_user]
                DataPersistence.save_practice_stats(stats)
            st.success(f"用户 {del_user} 已删除")
            st.rerun()
        else:
            st.error("不能删除管理员")

def render_data_view():
    st.markdown("#### 📊 全局统计")
    users = DataPersistence.load_users()
    wrong = DataPersistence.load_wrong_records()
    stats = DataPersistence.load_practice_stats()
    total_users = len(users)
    total_wrong = sum(len(v) for v in wrong.values())
    total_practice = sum(s.get("total",0) for s in stats.values())
    total_correct = sum(s.get("correct",0) for s in stats.values())
    accuracy = (total_correct/total_practice*100) if total_practice>0 else 0
    c1,c2,c3 = st.columns(3)
    c1.metric("总用户数", total_users)
    c2.metric("总错题数", total_wrong)
    c3.metric("平台正确率", f"{accuracy:.1f}%")
    st.divider()
    st.markdown("##### 错题记录")
    if wrong:
        for u, rec in wrong.items():
            with st.expander(f"📁 {u} ({len(rec)}条)"):
                if rec:
                    st.dataframe(pd.DataFrame(rec), use_container_width=True)
    else:
        st.info("无错题记录")

def render_system_settings():
    st.markdown("#### ⚙️ 系统设置")
    if st.button("🔄 重置所有数据"):
        if st.checkbox("确认重置？不可逆"):
            DataPersistence.save_users(DEFAULT_USERS.copy())
            DataPersistence.save_wrong_records({})
            DataPersistence.save_practice_stats({})
            st.success("已重置")
            st.rerun()
    st.divider()
    st.markdown("##### 📥 数据导出")
    fmt = st.radio("格式", ["JSON","CSV"])
    if st.button("导出"):
        if fmt == "JSON":
            export = {
                "users": DataPersistence.load_users(),
                "wrong_records": DataPersistence.load_wrong_records(),
                "practice_stats": DataPersistence.load_practice_stats()
            }
            st.download_button("下载", data=json.dumps(export,ensure_ascii=False,indent=2), file_name="data.json", mime="application/json")
        else:
            wrong = DataPersistence.load_wrong_records()
            rows = []
            for u, rec in wrong.items():
                for r in rec:
                    r["用户名"] = u
                    rows.append(r)
            if rows:
                df = pd.DataFrame(rows)
                st.download_button("下载CSV", data=df.to_csv(index=False, encoding='utf-8-sig'), file_name="wrong_records.csv")
            else:
                st.warning("无数据")

# ================= 主界面功能 =================
def render_main_content():
    tab = st.session_state.current_main_tab
    if tab == "🏠 首页":
        render_home_page()  # 新增首页函数
    elif tab == "知识库":
        render_knowledge_base()
    elif tab == "风险检测":
        render_risk_detection()
    elif tab == "练习中心":
        render_practice_center()
    elif tab == "学习报告":
        render_learning_report()
        # ================= 首页 =================
# ================= 首页 =================
def render_home_page():
    """渲染首页 - 视频介绍 + 平台知识"""
    st.subheader("🏠 欢迎来到跨境电商合规实训平台")
    
    # 平台简介
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 30px; border-radius: 15px; color: white; margin-bottom: 25px;">
        <h2 style="color: white; margin: 0;">📚 平台简介</h2>
        <p style="margin-top: 15px; font-size: 16px;">
        本平台专为跨境电商从业者设计，提供合规知识学习、商品风险检测、实战练习等功能。
        帮助您快速掌握各国合规要求，规避跨境贸易风险。
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # 视频区域（全宽，放大显示）
    st.markdown("### 📹 跨境电商合规指南")
    st.markdown("💡 观看视频，快速了解跨境电商合规要点")
    
    # 使用全宽列显示视频
    video_col1, video_col2, video_col3 = st.columns([1, 3, 1])
    with video_col2:
        # 视频示例 - 可以替换为你自己的视频链接
        video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # 示例视频，请替换
        st.video(video_url)
        st.caption("📌 视频来源：跨境电商合规指南（点击观看完整版）")
    
    # 平台导航（放在视频下面）
    st.markdown("---")
    st.markdown("### 🎯 快速导航")
    st.markdown("点击下方按钮，快速进入功能模块")
    
    # 四个功能按钮（2x2布局）
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📚 知识库", use_container_width=True):
            st.session_state.current_main_tab = "知识库"
            st.rerun()
        st.caption("学习各国合规要求")
    
    with col2:
        if st.button("🔍 风险检测", use_container_width=True):
            st.session_state.current_main_tab = "风险检测"
            st.rerun()
        st.caption("检测商品合规风险")
    
    col3, col4 = st.columns(2)
    with col3:
        if st.button("📝 练习中心", use_container_width=True):
            st.session_state.current_main_tab = "练习中心"
            st.rerun()
        st.caption("实战答题巩固知识")
    
    with col4:
        if st.button("📊 学习报告", use_container_width=True):
            st.session_state.current_main_tab = "学习报告"
            st.rerun()
        st.caption("查看学习进度")
    
    # 合规知识介绍（三个卡片）
    st.markdown("---")
    st.markdown("### 📖 跨境电商合规知识速览")
    
    card_col1, card_col2, card_col3 = st.columns(3)
    
    with card_col1:
        with st.container():
            st.markdown("""
            <div style="background-color: #e3f2fd; padding: 20px; border-radius: 10px; margin: 10px 0;">
                <h3 style="color: #1976d2;">🇪🇺 欧盟</h3>
                <p>• CE认证<br>• RoHS指令<br>• REACH法规<br>• WEEE回收</p>
            </div>
            """, unsafe_allow_html=True)
    
    with card_col2:
        with st.container():
            st.markdown("""
            <div style="background-color: #fff3e0; padding: 20px; border-radius: 10px; margin: 10px 0;">
                <h3 style="color: #f57c00;">🇺🇸 美国</h3>
                <p>• FCC认证<br>• CPSIA法规<br>• FDA注册<br>• FTC广告法</p>
            </div>
            """, unsafe_allow_html=True)
    
    with card_col3:
        with st.container():
            st.markdown("""
            <div style="background-color: #e8f5e9; padding: 20px; border-radius: 10px; margin: 10px 0;">
                <h3 style="color: #388e3c;">🌏 东南亚</h3>
                <p>• PSE认证<br>• 东盟指令<br>• 清真认证<br>• 本地语言标签</p>
            </div>
            """, unsafe_allow_html=True)
    
    # 学习路径建议
    st.markdown("---")
    st.markdown("### 🎓 学习路径建议")
    
    steps = st.columns(4)
    with steps[0]:
        st.markdown("""
        <div style="text-align: center;">
            <h1>1️⃣</h1>
            <h4>学习知识</h4>
            <p>浏览知识库，了解各国合规要求</p>
        </div>
        """, unsafe_allow_html=True)
    with steps[1]:
        st.markdown("""
        <div style="text-align: center;">
            <h1>2️⃣</h1>
            <h4>风险检测</h4>
            <p>上传商品信息，检测合规风险</p>
        </div>
        """, unsafe_allow_html=True)
    with steps[2]:
        st.markdown("""
        <div style="text-align: center;">
            <h1>3️⃣</h1>
            <h4>实战练习</h4>
            <p>答题巩固知识，查漏补缺</p>
        </div>
        """, unsafe_allow_html=True)
    with steps[3]:
        st.markdown("""
        <div style="text-align: center;">
            <h1>4️⃣</h1>
            <h4>查看报告</h4>
            <p>了解学习进度，持续改进</p>
        </div>
        """, unsafe_allow_html=True)
    
    # 平台数据 - 仅管理员可见
    if st.session_state.is_admin:
        st.markdown("---")
        st.markdown("### 📊 平台数据统计（仅管理员可见）")
        
        stats = DataPersistence.load_practice_stats()
        users = DataPersistence.load_users()
        wrong = DataPersistence.load_wrong_records()
        
        total_users = len(users)
        total_practice = sum(s.get("total", 0) for s in stats.values())
        total_correct = sum(s.get("correct", 0) for s in stats.values())
        total_wrong_records = sum(len(v) for v in wrong.values())
        accuracy = (total_correct / total_practice * 100) if total_practice > 0 else 0
        
        col_a, col_b, col_c, col_d = st.columns(4)
        col_a.metric("👥 注册用户数", total_users)
        col_b.metric("📝 总练习次数", total_practice // 5 if total_practice >= 5 else 0)
        col_c.metric("📊 平均正确率", f"{accuracy:.1f}%")
        col_d.metric("❌ 总错题数", total_wrong_records)
        
        # 最近活跃用户（可选）
        with st.expander("📈 查看详细统计"):
            st.write("**用户练习统计：**")
            if stats:
                stats_df = pd.DataFrame([
                    {"用户名": u, "练习次数": s.get("total", 0)//5, "正确数": s.get("correct", 0)}
                    for u, s in stats.items()
                ])
                st.dataframe(stats_df, use_container_width=True)
            else:
                st.info("暂无练习数据")
def render_knowledge_base():
    st.subheader("📚 合规知识库")
    rules = ConfigLoader.load_compliance_rules()
    categories = list(rules.keys())
    col1, col2 = st.columns([1,2])
    with col1:
        with st.container():
            st.markdown("<div class='vertical-card'>", unsafe_allow_html=True)
            category = st.selectbox("商品类别", categories, key="kb_cat")
            market = st.selectbox("目标市场", ["欧盟","美国","东南亚"], key="kb_mkt")
            st.markdown("</div>", unsafe_allow_html=True)
        with st.container():
            st.markdown("<div class='vertical-card'>", unsafe_allow_html=True)
            st.markdown("### 📋 违规词库")
            forbidden = ConfigLoader.load_forbidden_words()
            st.code(" | ".join(forbidden[:15]))
            with st.expander("完整列表"):
                st.write(", ".join(forbidden))
            st.markdown("</div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='vertical-card'>", unsafe_allow_html=True)
        st.markdown(f"### 🎯 {category} - {market} 合规要求")
        for i, rule in enumerate(rules[category][market]):
            st.markdown(f"<div class='compliance-card'><strong>📋 规则{i+1}:</strong> {rule}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<div class='vertical-card'>", unsafe_allow_html=True)
        laws = {"欧盟":"REACH | CE | RoHS", "美国":"CPSIA | FDA | FTC", "东南亚":"东盟指令 | PSE"}
        st.info(f"📖 {laws[market]}")
        st.markdown("</div>", unsafe_allow_html=True)

def render_risk_detection():
    st.subheader("🔍 商品合规风险检测")
    
    risk_rules = DataPersistence.load_risk_rules()
    compliance_rules = ConfigLoader.load_compliance_rules()
    all_categories = sorted(set(compliance_rules.keys()) | {cat for rule in risk_rules for cat in rule.get("product_categories", [])})
    
    # 三个选项卡：手动输入 / 图片识别 / 拍照识别
    input_method = st.radio(
        "选择输入方式",
        ["✏️ 手动输入", "📸 图片识别", "📷 拍照识别"],
        horizontal=True,
        help="手动输入：直接填写商品信息；图片识别：上传图片；拍照识别：使用摄像头"
    )
    
    # ========== 1. 手动输入模式 ==========
    if input_method == "✏️ 手动输入":
        col1, col2 = st.columns(2)
        with col1:
            with st.container():
                st.markdown("<div class='vertical-card'>", unsafe_allow_html=True)
                product_type = st.selectbox("商品类型", all_categories, key="rd_prod")
                target_market = st.selectbox("目标市场", ["欧盟", "美国", "东南亚"], key="rd_mkt")
                product_name = st.text_input("商品名称", key="rd_name")
                brand = st.text_input("品牌信息", key="rd_brand")
                st.markdown("</div>", unsafe_allow_html=True)
        with col2:
            with st.container():
                st.markdown("<div class='vertical-card'>", unsafe_allow_html=True)
                ingredients = st.text_area("成分/材质", height=100, key="rd_ing")
                description = st.text_area("商品描述/标题", height=150, key="rd_desc")
                st.markdown("</div>", unsafe_allow_html=True)
        
        if st.button("🔍 开始检测", type="primary", key="btn_manual"):
            if not product_type or not target_market:
                st.error("请填写商品类型和目标市场")
                return
            detected = perform_risk_check(
                risk_rules, product_type, target_market,
                product_name, description, ingredients, brand
            )
            display_risk_results(detected)
    
    # ========== 2. 图片识别模式 ==========
    elif input_method == "📸 图片识别":
        st.markdown("### 📸 上传商品图片")
        st.markdown("支持上传商品包装、标签、说明书等图片，系统将自动识别文字并检测合规风险")
        
        uploaded_file = st.file_uploader(
            "选择图片", 
            type=['png', 'jpg', 'jpeg', 'bmp', 'webp'],
            key="img_upload",
            help="支持 JPG、PNG、BMP、WEBP 格式"
        )
        
        if uploaded_file:
            col1, col2 = st.columns([1, 1])
            with col1:
                st.image(uploaded_file, caption="上传的图片", use_container_width=True)
            with col2:
                with st.spinner("正在识别图片中的文字..."):
                    recognized_text = extract_text_from_image(uploaded_file)
                    if recognized_text:
                        st.success(f"✅ 识别到 {len(recognized_text)} 个字符")
                        st.text_area("识别结果预览", recognized_text[:500], height=120)
                    else:
                        st.warning("未识别到文字内容，请尝试更清晰的图片")
            
            st.markdown("### 📝 商品信息（可编辑）")
            col1, col2 = st.columns(2)
            with col1:
                product_type = st.selectbox("商品类型", all_categories, key="rd_prod_img")
                target_market = st.selectbox("目标市场", ["欧盟", "美国", "东南亚"], key="rd_mkt_img")
                product_name = st.text_input("商品名称", key="rd_name_img", placeholder="例如: 充电宝")
                brand = st.text_input("品牌信息", key="rd_brand_img", placeholder="例如: 小米")
            with col2:
                description = st.text_area(
                    "商品描述/标题", 
                    value=recognized_text if recognized_text else "",
                    height=150,
                    key="rd_desc_img",
                    placeholder="图片识别到的文字会自动填入这里，您可以手动修改"
                )
                ingredients = st.text_area("成分/材质", height=100, key="rd_ing_img", placeholder="如有成分信息请填写")
            
            if st.button("🔍 开始检测", type="primary", key="btn_img"):
                if not product_type or not target_market:
                    st.error("请填写商品类型和目标市场")
                    return
                detected = perform_risk_check(
                    risk_rules, product_type, target_market,
                    product_name, description, ingredients, brand
                )
                display_risk_results(detected)
        else:
            st.info("👆 请上传一张商品图片开始检测")
    
    # ========== 3. 拍照识别模式（新增，移动端适用） ==========
    else:
        st.markdown("### 📷 拍照识别")
        st.markdown("使用摄像头拍摄商品标签、包装或说明书")
        
        camera_image = st.camera_input(
            "📸 对准商品拍照",
            key="mobile_camera",
            help="点击拍照，确保文字清晰可见"
        )
        
        if camera_image:
            col1, col2 = st.columns([1, 1])
            with col1:
                st.image(camera_image, caption="拍摄的照片", use_container_width=True)
            with col2:
                with st.spinner("正在识别图片中的文字..."):
                    recognized_text = extract_text_from_image(camera_image)
                    if recognized_text:
                        st.success(f"✅ 识别到 {len(recognized_text)} 个字符")
                        st.text_area("识别结果预览", recognized_text[:500], height=120)
                    else:
                        st.warning("未识别到文字内容，请重新拍摄更清晰的图片")
            
            st.markdown("### 📝 商品信息（可编辑）")
            col1, col2 = st.columns(2)
            with col1:
                product_type = st.selectbox("商品类型", all_categories, key="cam_prod")
                target_market = st.selectbox("目标市场", ["欧盟", "美国", "东南亚"], key="cam_mkt")
                product_name = st.text_input("商品名称", key="cam_name", placeholder="例如: 充电宝")
                brand = st.text_input("品牌信息", key="cam_brand", placeholder="例如: 小米")
            with col2:
                description = st.text_area(
                    "商品描述/标题", 
                    value=recognized_text if recognized_text else "",
                    height=150,
                    key="cam_desc",
                    placeholder="图片识别到的文字会自动填入这里"
                )
                ingredients = st.text_area("成分/材质", height=100, key="cam_ing", placeholder="如有成分信息请填写")
            
            if st.button("🔍 开始检测", type="primary", key="btn_cam"):
                if not product_type or not target_market:
                    st.error("请填写商品类型和目标市场")
                    return
                detected = perform_risk_check(
                    risk_rules, product_type, target_market,
                    product_name, description, ingredients, brand
                )
                display_risk_results(detected)
        else:
            st.info("👆 点击上方相机按钮拍照")
            st.caption("💡 提示：拍照时请确保光线充足，文字清晰")

# ================= 辅助函数 =================
def perform_risk_check(risk_rules, product_type, target_market, 
                       product_name, description, ingredients, brand):
    """执行风险检测"""
    detected = []
    full_text = f"{product_name} {description} {ingredients}".lower()
    
    for rule in risk_rules:
        categories = rule.get("product_categories", [])
        if categories and product_type not in categories:
            continue
        markets = rule.get("markets", [])
        if markets and target_market not in markets:
            continue
        
        rtype = rule.get("type")
        level = rule.get("risk_level", "中")
        msg_tpl = rule.get("message", "")
        advice = rule.get("advice", "")
        
        if rtype == "forbidden_word":
            for kw in rule.get("keywords", []):
                if kw.lower() in full_text:
                    detected.append({
                        "level": level, 
                        "title": rule["name"], 
                        "message": msg_tpl.format(word=kw), 
                        "advice": advice,
                        "type": "违禁词"
                    })
                    break
        
        elif rtype == "missing_certification":
            required = rule.get("required_words", [])
            found = any(rw.lower() in full_text for rw in required)
            if not found:
                detected.append({
                    "level": level, 
                    "title": rule["name"], 
                    "message": msg_tpl, 
                    "advice": advice,
                    "type": "认证缺失"
                })
        
        elif rtype == "infringement":
            for kw in rule.get("keywords", []):
                if kw.lower() in product_name.lower() or kw.lower() in full_text:
                    detected.append({
                        "level": level, 
                        "title": rule["name"], 
                        "message": msg_tpl, 
                        "advice": advice,
                        "type": "侵权风险"
                    })
                    break
        
        elif rtype == "ingredient":
            if ingredients:
                for kw in rule.get("keywords", []):
                    if kw.lower() in ingredients.lower():
                        detected.append({
                            "level": level, 
                            "title": rule["name"], 
                            "message": msg_tpl.format(word=kw), 
                            "advice": advice,
                            "type": "成分违规"
                        })
                        break
        
        elif rtype == "packaging":
            required = rule.get("required_words", [])
            found = any(rw.lower() in full_text for rw in required)
            if not found:
                detected.append({
                    "level": level, 
                    "title": rule["name"], 
                    "message": msg_tpl, 
                    "advice": advice,
                    "type": "包装不合规"
                })
    
    order = {"极高": 0, "高": 1, "中": 2, "低": 3}
    detected.sort(key=lambda x: order.get(x["level"], 4))
    return detected

def display_risk_results(detected):
    """显示检测结果"""
    if not detected:
        st.success("✅ 未发现合规风险")
        st.balloons()
    else:
        st.warning(f"⚠️ 发现 {len(detected)} 个风险")
        for i, d in enumerate(detected, 1):
            with st.expander(f"【风险{i}】{d['title']} (等级:{d['level']} | 类型:{d['type']})"):
                st.markdown(f"**📌 结果：** {d['message']}")
                st.markdown(f"**💡 建议：** {d['advice']}")
                if d['level'] in ["极高", "高"]:
                    st.error("❗ 严重风险，优先处理")
                else:
                    st.info("建议及时整改")
        
        if st.button("📚 查看知识库"):
            st.session_state.current_main_tab = "知识库"
            st.session_state.show_admin_panel = False
            st.rerun()

def extract_text_from_image(uploaded_file):
    """从上传的图片中提取文字（使用 Tesseract）"""
    if uploaded_file is None:
        return ""
    
    try:
        # 打开图片
        image = Image.open(uploaded_file)
        
        # 图片预处理（提高识别率）
        # 转换为灰度图
        if image.mode != 'L':
            image = image.convert('L')
        
        # 使用 Tesseract 识别文字（中英文混合）
        text = pytesseract.image_to_string(image, lang='chi_sim+eng')
        
        # 清理文本
        text = text.strip()
        # 合并多余换行
        text = ' '.join(text.split())
        
        return text
    except Exception as e:
        st.error(f"图片识别失败: {str(e)}")
        return ""

# ================= 修复后的练习中心 =================
def render_practice_center():
    st.subheader("📝 练习中心")
    st.markdown("**实战题库**：系统会随机抽取一套练习题，每套5题，答错自动记录到学习报告。")

    practice_sets = DataPersistence.load_practice_sets()
    if not practice_sets:
        st.error("练习题文件缺失")
        return

    if "practice_questions" not in st.session_state:
        st.session_state.practice_questions = None
        st.session_state.practice_answers = []
        st.session_state.practice_idx = 0

    if st.button("🔄 随机抽取一套练习", type="secondary"):
        chosen = random.choice(practice_sets)
        st.session_state.practice_questions = chosen["questions"]
        st.session_state.practice_answers = [None] * len(chosen["questions"])
        st.session_state.practice_idx = 0
        st.rerun()

    qs = st.session_state.practice_questions
    if qs is None:
        st.info("点击「随机抽取一套练习」开始挑战")
        return

    idx = st.session_state.practice_idx
    if idx >= len(qs):
        total = len(qs)
        correct = 0
        wrong_list = []
        for i, q in enumerate(qs):
            ans = st.session_state.practice_answers[i]
            if ans == q["answer"]:
                correct += 1
            else:
                wrong_list.append({
                    "题目": q["question"],
                    "用户答案": ans,
                    "正确答案": q["answer"],
                    "解析": q["explanation"],
                    "时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
        username = st.session_state.username
        stats = DataPersistence.load_practice_stats()
        if username not in stats:
            stats[username] = {"total": 0, "correct": 0}
        stats[username]["total"] += total
        stats[username]["correct"] += correct
        DataPersistence.save_practice_stats(stats)

        wrong = DataPersistence.load_wrong_records()
        if username not in wrong:
            wrong[username] = []
        wrong[username].extend(wrong_list)
        DataPersistence.save_wrong_records(wrong)

        st.success(f"✅ 练习完成！正确率：{correct}/{total} ({correct/total*100:.1f}%)")
        if wrong_list:
            st.warning("📝 以下错题已记录到「学习报告」中：")
            for w in wrong_list:
                st.markdown(f"- **{w['题目']}** 你的答案：{w['用户答案']}，正确答案：{w['正确答案']}。{w['解析']}")
        else:
            st.balloons()

        st.session_state.practice_questions = None
        st.session_state.practice_answers = []
        st.session_state.practice_idx = 0
        if st.button("继续练习", type="primary"):
            st.rerun()
        return

    q = qs[idx]
    st.markdown(f"**第 {idx+1}/{len(qs)} 题**")
    st.markdown(f"### {q['question']}")

    # 获取已保存的答案
    saved_ans = st.session_state.practice_answers[idx]
    options = q["options"]
    if saved_ans is not None and saved_ans in options:
        default_index = options.index(saved_ans)
    else:
        default_index = 0   # 默认第一个选项
    ans = st.radio("请选择答案:", options, index=default_index, key=f"prac_{idx}")
    # 保存当前答案
    st.session_state.practice_answers[idx] = ans

    col1, col2 = st.columns(2)
    with col1:
        if st.button("上一题", disabled=(idx == 0), key=f"prev_{idx}"):
            st.session_state.practice_idx -= 1
            st.rerun()
    with col2:
        if st.button("下一题", key=f"next_{idx}"):
            st.session_state.practice_idx += 1
            st.rerun()

def render_learning_report():
    st.subheader("📊 学习报告")
    username = st.session_state.username
    wrong = DataPersistence.load_wrong_records().get(username, [])
    stats = DataPersistence.load_practice_stats().get(username, {"total":0,"correct":0})
    total = stats["total"]
    correct = stats["correct"]
    acc = (correct/total*100) if total>0 else 0
    c1,c2,c3 = st.columns(3)
    c1.metric("总练习次数", total//5)
    c2.metric("错题数", len(wrong))
    c3.metric("累计正确率", f"{acc:.1f}%")
    st.markdown("<div class='vertical-card'>", unsafe_allow_html=True)
    st.markdown("### 📝 我的错题")
    if wrong:
        st.dataframe(pd.DataFrame(wrong), use_container_width=True)
    else:
        st.info("🎉 暂无错题记录，继续保持！")
    st.markdown("</div>", unsafe_allow_html=True)

# ================= 主函数 =================
def main():
    setup_page_config()
    inject_custom_css()
    ConfigLoader.init_config_files()
    init_session_state()
    if not st.session_state.logged_in:
        render_login()
        st.stop()
    render_top_navbar()
    if st.session_state.is_admin and st.session_state.show_admin_panel:
        render_admin_panel()
    else:
        render_main_content()

if __name__ == "__main__":
    main()