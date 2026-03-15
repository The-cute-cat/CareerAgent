from typing import Dict, Optional

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup


def fetch_job_info(
        url: str,
        wait_timeout: int = 5,
        headless: bool = False
) -> Dict[str, Optional[str]]:
    """
    抓取智联招聘职位详情信息

    参数:
        url: 职位详情页URL
        wait_timeout: 等待元素加载的超时时间（秒）
        headless: 是否无头模式运行浏览器

    返回:
        dict: 包含职位信息的字典，键包括:
            - 职位名称
            - 岗位详情
    """
    result = {
        "岗位名称":None,
        "岗位详情":None,
    }
    # 1. 初始化浏览器（需要提前安装ChromeDriver）
    from selenium.webdriver.chrome.options import Options
    options = Options()
    if headless:
        options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    driver.get(url)

    # 2. 等待目标元素加载完成（关键）
    try:
        # 等待5秒，直到h1标签出现
        element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "summary-plane__title"))
        )
        # 3. 获取渲染后的完整HTML
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        # 4. 再定位元素
        gangwei = soup.find("h1", class_="summary-plane__title")
        info_ul = soup.find("ul", class_="summary-plane__info")
        skills_container = soup.find("div", class_="describtion__skills-content")
        skills_yaoqiu = soup.find("div", class_="describtion__detail-content")
        skills_str = ""
        gangwei_str = ""
        job_info = {}
        if info_ul:
            li_list = info_ul.find_all("li")
            # 逐个提取
            if li_list[1].get_text(strip=True) and li_list[2].get_text(strip=True):
                job_info["经验"] = li_list[1].get_text(strip=True)
                job_info["学位"] = li_list[2].get_text(strip=True)
                skills_str = skills_str + "职位描述：" + ";".join(job_info.values())+";"
        if skills_container:
            # 2. 找到所有技能标签
            skill_items = skills_container.find_all("span", class_="describtion__skills-item")
            # 3. 提取文本并拼接成字符串（用逗号分隔）
            skills_str = skills_str + "职位描述：" + ",".join([item.get_text(strip=True) for item in skill_items])+";"
        if gangwei:
            gangwei_str = gangwei.get_text(strip=True)
        if skills_yaoqiu:
            skills_str = skills_str + skills_yaoqiu.get_text(strip=True)
        if gangwei_str :
            result["岗位名称"] = gangwei_str
        if skills_str:
            result["岗位详情"] = skills_str
    finally:
        driver.quit()
        # print(f"{gangwei_str}\n{skills_str}")

    return result


if __name__ == "__main__":
    yy=fetch_job_info("https://www.zhaopin.com/jobdetail/CC000260640J40852151604.htm?refcode=4019&srccode=401901&preactionid=a7c1140f-c46c-45e5-b867-ab342d8bdc77")
    print(yy)