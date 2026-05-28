# test_fmp_standalone.py (M7-ALPHA FMP 2026 官方标准查询参数版·孤立探测沙盒)
import requests
import json

# 🌟 🌟 🌟 【关键填写点】：把你在 FMP 官网拿到的 API Key 贴到这里！
FMP_API_KEY = "kPMexoadiYqpbbYOmrzXzcDP7lmeHfVt" 

def test_fmp_nvda_pipeline(api_key: str):
    print("🚀 [FMP-SANDBOX] 正在对英伟达（NVDA）启动 2026 官方全新控制台参数点火测试...")
    symbol = "NVDA"
    
    # -----------------------------------------------------------------
    # 📊 探测流 1：打捞英伟达『公司简况与基本面明细』(Profile)
    # -----------------------------------------------------------------
    # 依据官方最新标准文档：代码必须通过 ?symbol=NVDA 传参，路径保持纯净
    profile_url = f"https://financialmodelingprep.com/stable/profile?symbol={symbol}&apikey={api_key}"
    print(f"\n📡 [1/2] 正在请求 FMP 官方新版稳定公司简况通道...")
    
    try:
        response_prof = requests.get(profile_url, timeout=10)
        if response_prof.status_code == 200:
            data_prof = response_prof.json()
            if data_prof and len(data_prof) > 0:
                print("A 🟢 [SUCCESS] 2026新版公司简况因子提取闭环！核心资产透视：")
                prof_core = data_prof[0]
                print(f"   🏢 公司全称: {prof_core.get('companyName')}")
                print(f"   🔌 所属行业: {prof_core.get('industry')} | 板块: {prof_core.get('sector')}")
                print(f"   💰 当前市值: ${prof_core.get('mcap'):,}")
                print(f"   📝 简介缩影(前100字): {prof_core.get('description', '')[:100]}...")
            else:
                print("⚠️ 网关正常响应，但拉回的数据为空，请检查 Key 的免费额度。")
        else:
            print(f"❌ 公司简介网关拒绝，状态码: {response_prof.status_code}，回复: {response_prof.text}")
    except Exception as e:
        print(f"❌ 公司简介触发网络故障: {e}")

    # -----------------------------------------------------------------
    # 📑 探测流 2：打捞英伟达『最新季度利润表财务底座』(Income Statement)
    # -----------------------------------------------------------------
    # 同样严格对齐 2026 查询参数规范：?symbol=NVDA&period=quarter
    income_url = f"https://financialmodelingprep.com/stable/income-statement?symbol={symbol}&period=quarter&limit=3&apikey={api_key}"
    print(f"\n📡 [2/2] 正在请求 FMP 官方新版稳定季度利润表通道...")
    
    try:
        response_inc = requests.get(income_url, timeout=10)
        if response_inc.status_code == 200:
            data_inc = response_inc.json()
            if data_inc and len(data_inc) > 0:
                print(f"B 🟢 [SUCCESS] 2026新版季度利润表提取闭环！已成功打捞 {len(data_inc)} 个季度原厂账本。")
                print("💡 下方是经过格式化后的第一手 JSON 财务因子样例：")
                print(json.dumps(data_inc[0], indent=2, ensure_ascii=False))
            else:
                print("⚠️ 利润表网关响应，但未拉回有效报表。")
        else:
            print(f"❌ 利润表网关拒绝，状态码: {response_inc.status_code}，回复: {response_inc.text}")
    except Exception as e:
        print(f"❌ 利润表触发网络故障: {e}")

    print("\n🏁 [FMP-SANDBOX] 2026正宗官方协议回路测试跑完全程。")

if __name__ == "__main__":
    if FMP_API_KEY == "你的_FMP_API_KEY":
        print("❌ 错误：请先在代码第 6 行替换为你自己在 FMP 注册拿到的真实 API Key！")
    else:
        test_fmp_nvda_pipeline(FMP_API_KEY)