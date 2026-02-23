

import os
import requests
import datetime
import re
from dotenv import load_dotenv

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
        # 마감일이 없는 경우 '채용 시'로 표시
        end_day = job.get('recpEndDay', 'N/A')
        if not end_day or end_day == 'N/A':
            end_day = '채용 시'

        link = job.get('siteUrl') if job.get('siteUrl') else job.get('originUrl', '#')
        table += f"| {job.get('instNm', 'N/A')} | {title_text} | {end_day} | [바로가기]({link}) |\n"
        
    return table

def update_readme(markdown_content):
    """Chapter_10/README.md 파일의 내용을 새로운 채용 공고로 교체합니다."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    readme_path = os.path.join(script_dir, 'Chapter_10/README.md')
    placeholder_start = "<!-- START_JOBS -->"
    placeholder_end = "<!-- END_JOBS -->"

    try:
        with open(readme_path, 'r', encoding='utf-8') as f:
            full_content = f.read()

        now_utc = datetime.datetime.utcnow()
        now_kst = now_utc + datetime.timedelta(hours=9)
        header = f"## 📅 금융권 채용 공고 (최근 업데이트: {now_kst.strftime('%Y-%m-%d %H:%M:%S')})\n\n"
        jobs_section = f"{placeholder_start}\n{header}{markdown_content}\n{placeholder_end}"

        # 정규식을 사용하여 placeholder 사이의 내용만 교체
        pattern = re.compile(f"{re.escape(placeholder_start)}.*?{re.escape(placeholder_end)}", re.DOTALL)
        
        if pattern.search(full_content):
            final_content = pattern.sub(jobs_section, full_content)
        else:
            # 플레이스홀더가 없는 경우 파일 끝에 추가 (또는 다른 원하는 동작)
            final_content = full_content + "\n" + jobs_section

        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(final_content)
        
        print(f"Successfully wrote {len(final_content)} characters to {readme_path}")

    except FileNotFoundError:
        # 루트에 README.md가 없는 경우를 대비해 새로 생성
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(jobs_section)
        print(f"Created {readme_path} and wrote {len(jobs_section)} characters.")


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    load_dotenv(os.path.join(script_dir, ".env"))

    api_key = os.getenv("FSS_API_KEY")
    
    if not api_key:
        raise ValueError("API 키가 환경 변수(FSS_API_KEY)에 설정되지 않았습니다.")
    
    today = datetime.date.today()

    all_fetched_jobs = {} # Use a dictionary to store jobs by appformNo for deduplication

    # Fetch data for the past year in 30-day chunks
    # Start from 1 month in the future to cover current jobs and go back 1 year
    current_date_iterator = today + datetime.timedelta(days=30) 
    end_of_historical_period = today - datetime.timedelta(days=90) 

    while current_date_iterator > end_of_historical_period:
        interval_end_date = current_date_iterator
        interval_start_date = interval_end_date - datetime.timedelta(days=30)

        # Ensure start date doesn't go beyond the desired historical period
        if interval_start_date < end_of_historical_period:
            interval_start_date = end_of_historical_period

        print(f"Fetching jobs from {interval_start_date.strftime('%Y-%m-%d')} to {interval_end_date.strftime('%Y-%m-%d')}")
        jobs_in_interval = fetch_job_postings(
            api_key,
            interval_start_date.strftime('%Y-%m-%d'),
            interval_end_date.strftime('%Y-%m-%d')
        )

        for job in jobs_in_interval:
            appform_no = job.get('appformNo')
            if appform_no:
                all_fetched_jobs[appform_no] = job # Add or update job, effectively deduplicating

        current_date_iterator = interval_start_date - datetime.timedelta(days=1) # Move to the day before the start of the current interval

    all_jobs = list(all_fetched_jobs.values()) # Convert dictionary values back to a list

    current_jobs = []
    closed_jobs = []

    for job in all_jobs:
        end_day_str = job.get('recpEndDay')
        
        # '9999-12-31'은 관행적으로 '채용 시'를 의미하므로 표시를 정규화
        if end_day_str == '9999-12-31':
            end_day_str = '채용 시 마감'
            job['recpEndDay'] = end_day_str
        
        if end_day_str == '채용 시': # 마감일이 '채용 시'인 경우
            current_jobs.append(job)
        elif not end_day_str: # 마감일이 아예 없는 경우
            current_jobs.append(job)
        else:
            try:
                end_day = datetime.datetime.strptime(end_day_str, '%Y-%m-%d').date()
                if end_day >= today: # 마감일이 오늘이거나 미래인 경우
                    current_jobs.append(job)
                else: # 마감일이 과거인 경우
                    closed_jobs.append(job)
            except ValueError:
                # 날짜 형식이 '채용 시'도 아니고, 비어있지도 않으며, 잘못된 경우
                current_jobs.append(job) # 일단 진행 중인 공고로 분류

    # 마크다운 생성
    current_section = generate_markdown_section("🚀 진행 중인 공고", current_jobs)
    closed_section = generate_markdown_section("✅ 최근 마감된 공고 (90일 이내)", closed_jobs)
    
    final_markdown = current_section + "\n" + closed_section
    
    update_readme(final_markdown)
