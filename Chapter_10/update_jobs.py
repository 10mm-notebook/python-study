

import os
import requests
import datetime
import re

def fetch_job_postings(api_key, start_date, end_date):
    """금융감독원 API를 호출하여 지정된 기간의 채용 공고를 가져옵니다."""
    
    url = (
        f"https://www.fss.or.kr/fss/kr/openApi/api/recruitInfo.jsp"
        f"?apiType=json&startDate={start_date}&endDate={end_date}&authKey={api_key}"
    )
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        if data.get("reponse", {}).get("resultCode") == "1":
            return data["reponse"].get("result", [])
        else:
            if data.get("reponse", {}).get("resultMsg") != "자료가 없습니다.":
                 print(f"API Error: {data.get('reponse', {}).get('resultMsg', 'Unknown error')}")
            return []
            
    except requests.exceptions.RequestException as e:
        print(f"HTTP Request failed: {e}")
        return []
    except ValueError:
        print(f"Failed to decode JSON from response: {response.text}")
        return []

def generate_markdown_section(title, jobs):
    """채용 공고 리스트로 마크다운 섹션 하나를 생성합니다."""
    if not jobs:
        return f"### {title}\n\n- 해당 기간에 공고가 없습니다.\n"

    table = f"### {title}\n\n"
    table += "| 기관명 | 제목 | 마감일 | 링크 |\n"
    table += "|---|---|---|---|\n"
    
    for job in sorted(jobs, key=lambda x: x.get('recpEndDay', ''), reverse=True):
        title_text = job.get('titl', 'N/A').replace('\n', ' ').strip()
        link = job.get('siteUrl') if job.get('siteUrl') else job.get('originUrl', '#')
        table += f"| {job.get('instNm', 'N/A')} | {title_text} | {job.get('recpEndDay', 'N/A')} | [바로가기]({link}) |\n"
        
    return table

def update_readme(markdown_content):
    """README.md 파일의 내용을 새로운 채용 공고로 교체합니다."""
    readme_path = 'Chapter_10/README.md'
    placeholder_start = "<!-- START_JOBS -->"
    placeholder_end = "<!-- END_JOBS -->"

    try:
        with open(readme_path, 'r', encoding='utf-8') as f:
            full_content = f.read()

        if placeholder_start in full_content:
            intro_content = full_content.split(placeholder_start)[0]
        else:
            intro_content = full_content # 플레이스홀더가 없으면 전체를 소개글로 간주

        header = f"## 📅 금융권 채용 공고 (최근 업데이트: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')})\n\n"
        jobs_section = f"{placeholder_start}\n{header}{markdown_content}\n{placeholder_end}"

        final_content = intro_content + jobs_section

        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(final_content)
        
        print(f"Successfully wrote {len(final_content)} characters to {readme_path}")

    except FileNotFoundError:
        print(f"Error: {readme_path} not found. Cannot update.")


if __name__ == "__main__":
    api_key = os.getenv("FSS_API_KEY")
    
    if not api_key:
        raise ValueError("API 키가 환경 변수(FSS_API_KEY)에 설정되지 않았습니다.")
    
    today = datetime.date.today()
    
    start_current = today
    end_current = today + datetime.timedelta(days=30)
    current_jobs = fetch_job_postings(api_key, start_current.strftime('%Y-%m-%d'), end_current.strftime('%Y-%m-%d'))
    
    end_closed = today - datetime.timedelta(days=1)
    start_closed = end_closed - datetime.timedelta(days=30)
    closed_jobs = fetch_job_postings(api_key, start_closed.strftime('%Y-%m-%d'), end_closed.strftime('%Y-%m-%d'))

    current_section = generate_markdown_section("🚀 진행 중인 공고", current_jobs)
    closed_section = generate_markdown_section("✅ 최근 마감된 공고", closed_jobs)
    
    final_markdown = current_section + "\n" + closed_section
    
    update_readme(final_markdown)
