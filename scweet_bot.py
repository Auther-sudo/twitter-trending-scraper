import asyncio
import random
from playwright.async_api import async_playwright
import pandas as pd
import os

# ===================== 配置 =====================
KEYWORDS_FILE = r"D:\编程工具或实用程序\scweet_bot\keywords.txt"
OUTPUT_FILE = r"D:\编程工具或实用程序\scweet_bot\推文结果.xlsx"  # 改为xlsx格式
MAX_TWEETS = 15  # 单关键词最大抓取数
SCROLL_STEP = 5  # 每次滚动加载的推文数（可调整）
PROXY = None
MAX_SCROLL_RETRY = 3  # 无新数据时最大滚动重试次数
# =================================================

# 加载关键词
def load_keywords():
    try:
        with open(KEYWORDS_FILE, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"加载关键词失败：{e}")
        return []

# 账号分类
def classify_account(name, bio):
    text = f"{name} {bio}".lower()
    gov = ["gov", "government", "ministry", "official", "政府"]
    media = ["news", "media", "tv", "journal", "新闻"]
    ngo = ["ngo", "non-profit", "charity", "公益"]
    if any(k in text for k in gov): return "政府机构"
    if any(k in text for k in media): return "媒体"
    if any(k in text for k in ngo): return "NGO"
    return "个人"

# 抓取程序（优化版，去掉去重）
async def crawl_twitter(keyword):
    results = []
    async with async_playwright() as p:
        try:
            # 启动浏览器（防风控）
            browser = await p.chromium.launch(
                headless=False,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--start-maximized",
                    "--no-sandbox",
                    "--disable-dev-shm-usage"
                ]
            )

            page = await browser.new_page(
                ignore_https_errors=True,
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"
            )

            # 隐藏自动化痕迹
            await page.evaluate("""() => {
                delete navigator.__proto__.webdriver;
                Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            }""")

            page.set_default_timeout(60000)

            # 打开 X
            print("\n打开 X 主页...")
            await page.goto("https://x.com/home", wait_until="domcontentloaded")
            await asyncio.sleep(2)

            # ==================== 手动登录 ====================
            print("\n" + "="*60)
            print("👉 请你登录 X")
            print("👉 登录成功后，回到这里按回车")
            print("="*60)
            input("按回车继续...")

            # ==================== 搜索 ====================
            print(f"\n正在搜索：{keyword}")
            await asyncio.sleep(2)
            await page.goto(f"https://x.com/search?q={keyword}&f=live", wait_until="domcontentloaded")
            await asyncio.sleep(10)

            # ==================== 滚动加载更多推文 ====================
            print("开始滚动加载推文...")
            parsed_count = 0  # 已解析推文计数器
            no_new_data_count = 0  # 无新数据计数器
            
            while parsed_count < MAX_TWEETS and no_new_data_count < MAX_SCROLL_RETRY:
                # 记录当前已解析的推文数量
                current_count = parsed_count
                
                # 抓取当前页面所有推文并解析
                tweets = await page.query_selector_all("article")
                for tweet in tweets:
                    if parsed_count >= MAX_TWEETS:
                        break
                    try:
                        # 随机间隔1-2秒，避免风控
                        await asyncio.sleep(random.uniform(1, 2))
                        
                        username_elem = await tweet.query_selector("div[data-testid='User-Name']")
                        username = await username_elem.inner_text() if username_elem else "未知"
                        
                        bio_elem = await tweet.query_selector("div[data-testid='UserDescription']")
                        bio = await bio_elem.inner_text() if bio_elem else ""
                        
                        content_elem = await tweet.query_selector("div[data-testid='tweetText']")
                        content = await content_elem.inner_text() if content_elem else ""
                        
                        results.append([keyword, username, classify_account(username, bio), content])
                        parsed_count += 1
                        print(f"✅ 第{parsed_count}条：{username[:25]}")
                    except Exception as e:
                        print(f"⚠️ 解析第{parsed_count+1}条推文失败：{e}")
                        continue

                # 检查是否有新数据
                if parsed_count == current_count:
                    no_new_data_count += 1
                    print(f"⚠️ 无新推文，重试次数：{no_new_data_count}/{MAX_SCROLL_RETRY}")
                else:
                    no_new_data_count = 0  # 重置重试计数器

                # 滚动页面加载更多（未达目标且未重试上限）
                if parsed_count < MAX_TWEETS and no_new_data_count < MAX_SCROLL_RETRY:
                    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    await asyncio.sleep(random.uniform(5, 10))  # 滚动后等待加载
                else:
                    break

        except Exception as e:
            print(f"❌ 抓取异常：{str(e)}")
        finally:
            await browser.close()

    return results

# 主程序
async def main():
    print("🚀 X 推文抓取（优化版）")
    keywords = load_keywords()
    if not keywords:
        print("❌ 未找到关键词")
        return

    all_data = []
    for kw in keywords:
        print(f"\n========== 关键词：{kw} ==========")
        data = await crawl_twitter(kw)
        all_data += data

    if all_data:
        # 保存为Excel文件（xlsx格式，不去重）
        df = pd.DataFrame(all_data, columns=["关键词", "账号名", "账号类型", "推文内容"])
        df.to_excel(OUTPUT_FILE, index=False, engine="openpyxl")
        print(f"\n🎉 抓取完成！共 {len(df)} 条数据")
        print(f"📁 文件已保存至：{OUTPUT_FILE}")
    else:
        print("\n❌ 未抓取到数据")

if __name__ == "__main__":
    # 安装依赖（首次运行需执行）：pip install playwright pandas openpyxl
    # 初始化playwright：playwright install chromium
    asyncio.run(main())