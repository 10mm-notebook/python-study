import os
import requests
import datetime
import re

def fetch_job_postings(api_key):
    """금융감독원 API를 호출하여 오늘부터 7일 후까지의 채용 공고를 가져옵니다."""
    today = datetime.date.today()
    one_week_later = today + datetime.timedelta(days=7)
    
    start_date = today.strftime('%Y-%m-%d')
    end_date = one_week_later.strftime('%Y-%m-%d')
    
    url = (
        f"https://www.fss.or.kr/fss/kr/openApi/api/recruitInfo.jsp"
        f"?apiType=json&startDate={start_date}&endDate={end_date}&authKey={api_key}"
    )
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # HTTP 오류 발생 시 예외 발생
        data = response.json()
        
        if data.get("reponse", {}).get("resultCode") == "1":
            return data["reponse"].get("result", [])
        else:
            print(f"API Error: {data.get('reponse', {}).get('resultMsg', 'Unknown error')}")
            return []
            
    except requests.exceptions.RequestException as e:
        print(f"HTTP Request failed: {e}")
        return []
    except ValueError: # JSONDecodeError
        print(f"Failed to decode JSON from response: {response.text}")
        return []

def generate_markdown_table(jobs):
    """채용 공고 리스트를 마크다운 테이블 형식으로 변환합니다."""
    if not jobs:
        return "이번 주에 새로운 채용 공고가 없습니다."

    header = f"## 📅 주간 금융권 채용 공고 ({datetime.date.today().strftime('%Y-%m-%d')})

"
    table = "| 기관명 | 제목 | 마감일 | 링크 |
"
    table += "|---|---|---|---|
"
    
    for job in jobs:
        title = job.get('titl', 'N/A').replace('\n', ' ').strip()
        # URL이 없는 경우 원본 게시글 URL을 사용
        link = job.get('siteUrl') if job.get('siteUrl') else job.get('originUrl', '#')
        table += f"| {job.get('instNm', 'N/A')} | {title} | {job.get('recpEndDay', 'N/A')} | [바로가기]({link}) |
"
        
    return header + table

def update_readme(markdown_content):
    """README.md 파일의 특정 부분을 찾아 새로운 내용으로 교체합니다."""
    readme_path = 'Chapter_10/README.md'
    placeholder_start = "<!-- START_JOBS -->"
    placeholder_end = "<!-- END_JOBS -->"
    
    try:
        with open(readme_path, 'r', encoding='utf-8') as f:
            readme_content = f.read()

        # 정규 표현식을 사용하여 플레이스홀더 사이의 내용을 교체
        new_content = f"{placeholder_start}
{markdown_content}
{placeholder_end}"
        
        # 플레이스홀더가 있는지 확인하고 교체
        if placeholder_start in readme_content and placeholder_end in readme_content:
            pattern = re.compile(f"{placeholder_start}.*?{placeholder_end}", re.DOTALL)
            updated_readme = pattern.sub(new_content, readme_content)
        else:
            # 플레이스홀더가 없으면 파일 끝에 추가
            updated_readme = readme_content + "
" + new_content

        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(updated_readme)
        print("README.md updated successfully.")

    except FileNotFoundError:
        print(f"Error: {readme_path} not found. Creating a new one.")
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(f"<!-- START_JOBS -->
{markdown_content}
<!-- END_JOBS -->")


if __name__ == "__main__":
    api_key = os.getenv("FSS_API_KEY")
    
    if not api_key:
        raise ValueError("API 키가 환경 변수(FSS_API_KEY)에 설정되지 않았습니다.")
        
    job_postings = fetch_job_postings(api_key)
    markdown_table = generate_markdown_table(job_postings)
    update_readme(markdown_table)
