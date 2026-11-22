import random
import requests
import csv
import time

# --- 기존 위치 데이터 세팅 ---
LON_MIN, LON_MAX = 126.826377, 127.025452
LAT_MIN, LAT_MAX = 35.149440, 35.262273

REAL_LOCATIONS = {
    # 0. 물류 허브 (출발지 고정)
    "광주북HUB (월출동)": [126.853300, 35.215500],

    # 1. 전남대학교 캠퍼스 내부 주요 거점
    "전남대 공과대학 1호관": [126.904800, 35.176400],
    "전남대 대학본부": [126.907200, 35.175200],
    "전남대 중앙도서관": [126.906100, 35.175800],
    "전남대 BTL 기숙사 (9관)": [126.909500, 35.180200],
    "전남대 제1학생회관": [126.904500, 35.174500],
    "전남대 인문대학": [126.903200, 35.175500],
    "전남대 경영대학": [126.901500, 35.173800],
    "전남대 농업생명과학대학": [126.910500, 35.177200],
    "전남대 사회과학대학": [126.902200, 35.177000],
    "전남대 자연과학대학 1호관": [126.905500, 35.177800],
    "전남대 예술대학": [126.908500, 35.173500],
    "전남대 체육관": [126.911200, 35.179000],
    "전남대 정문 안내소": [126.909200, 35.171500],
    "전남대 후문 광장": [126.907000, 35.178800],
    "전남대 상대 뒤편": [126.901000, 35.178200],

    # 2. 행정복지센터 (동주민센터) 및 공공기관
    "북구청 (용봉동)": [126.911500, 35.174200],
    "용봉동 행정복지센터": [126.891200, 35.188500],
    "일곡동 행정복지센터": [126.894300, 35.205200],
    "양산동 행정복지센터": [126.868500, 35.208500],
    "운암1동 행정복지센터": [126.875000, 35.175000],
    "운암2동 행정복지센터": [126.882000, 35.178000],
    "운암3동 행정복지센터": [126.871000, 35.183000],
    "문흥1동 행정복지센터": [126.920500, 35.185500],
    "문흥2동 행정복지센터": [126.927000, 35.192000],
    "오치1동 행정복지센터": [126.905000, 35.195000],
    "오치2동 행정복지센터": [126.913000, 35.198000],
    "삼각동 행정복지센터": [126.895000, 35.200000],
    "매곡동 행정복지센터": [126.885000, 35.195000],
    "건국동 행정복지센터": [126.865000, 35.215000],
    "동림동 행정복지센터": [126.860000, 35.180000],
    "신안동 행정복지센터": [126.900000, 35.165000],
    "중흥1동 행정복지센터": [126.915000, 35.165000],
    "중흥2동 행정복지센터": [126.921000, 35.169000],
    "중흥3동 행정복지센터": [126.918000, 35.172000],
    "중앙동 행정복지센터": [126.910000, 35.158000],
    "임동 행정복지센터": [126.890000, 35.160000],
    "두암1동 행정복지센터": [126.930000, 35.170000],
    "두암2동 행정복지센터": [126.938000, 35.175000],
    "두암3동 행정복지센터": [126.945000, 35.172000],
    "문화동 행정복지센터": [126.935000, 35.180000],
    "석곡동 행정복지센터": [126.950000, 35.190000],
    "신용동 행정복지센터": [126.862000, 35.198000],
    "광주 우편집중국": [126.876000, 35.193000],
    "광주북부경찰서": [126.901000, 35.198000],

    # 3. 주요 아파트 단지 (배송 밀집 지역)
    "용봉동 현대아파트": [126.891200, 35.188500],
    "용봉동 한화꿈에그린": [126.897000, 35.184000],
    "용봉동 쌍용예가": [126.893500, 35.191000],
    "일곡동 삼호아파트": [126.899500, 35.204500],
    "일곡동 청솔아파트": [126.892000, 35.207000],
    "일곡동 현대아파트": [126.896500, 35.202000],
    "양산동 호반리젠시빌": [126.866000, 35.211000],
    "양산동 자이아파트": [126.872000, 35.205000],
    "운암동 벽산블루밍 1단지": [126.878000, 35.173000],
    "운암동 벽산블루밍 3단지": [126.873000, 35.179000],
    "운암동 서희스타힐스": [126.868000, 35.176000],
    "운암동 아이파크": [126.884000, 35.172000],
    "문흥동 현대아파트": [126.923000, 35.188000],
    "문흥동 라인동산아파트": [126.929000, 35.190000],
    "문흥동 상록아파트": [126.919000, 35.183000],
    "오치동 우성아파트": [126.908000, 35.192000],
    "오치동 금호아파트": [126.915000, 35.196000],
    "매곡동 대한그린아파트": [126.889000, 35.197000],
    "매곡동 현대아파트": [126.882000, 35.193000],
    "동림동 삼익아파트": [126.858000, 35.178000],
    "동림동 푸른마을 주공": [126.855000, 35.183000],
    "두암동 주공아파트 3단지": [126.941000, 35.169000],
    "두암동 무등파크맨션": [126.932000, 35.174000],
    "신용동 제일풍경채": [126.859000, 35.201000],
    "연제동 현대힐스테이트": [126.864000, 35.219000],

    # 4. 교육 시설 (초·중·고등학교 및 도서관)
    "경신여고": [126.886500, 35.174200],
    "문정여고": [126.918000, 35.189500],
    "광주예술고": [126.881000, 35.190000],
    "숭일고": [126.892000, 35.213000],
    "살레시오고": [126.898000, 35.218000],
    "고려고": [126.907000, 35.201000],
    "국제고": [126.922000, 35.203000],
    "광주공고": [126.929000, 35.181000],
    "금호고": [126.872000, 35.186000],
    "운암중": [126.876000, 35.181000],
    "용봉중": [126.896000, 35.186000],
    "일곡중": [126.894000, 35.208000],
    "양산중": [126.871000, 35.212000],
    "일곡도서관": [126.898000, 35.210000],
    "운암도서관": [126.880000, 35.183000],

    # 5. 교통, 문화, 상업 및 랜드마크 시설
    "광주역": [126.914200, 35.165400],
    "말바우시장": [126.925000, 35.170000],
    "광주비엔날레 전시관": [126.888000, 35.182000],
    "광주기아챔피언스필드": [126.889000, 35.168000],
    "본촌일반산업단지": [126.870000, 35.210000],
    "광주디자인진흥원": [126.850000, 35.220000],
    "우치공원 패밀리랜드": [126.895000, 35.225000],
    "국립광주박물관": [126.885000, 35.190000],
    "광주문화예술회관": [126.885500, 35.171000],
    "홈플러스 동광주점": [126.931000, 35.181000],
    "이마트동광주점": [126.919000, 35.166000],
    "오치동 북부소방서": [126.912000, 35.191000],
    "광주교육대학교": [126.931000, 35.161000],
    "동강대학교": [126.924000, 35.167000],
    "서방시장": [126.922000, 35.163000]
}

def solve_tsp(matrix, start_index=0):
    num_nodes = len(matrix)
    visited = [False] * num_nodes
    path = [start_index]
    visited[start_index] = True
    current_node = start_index
    for _ in range(num_nodes - 1):
        next_node = None
        min_duration = float('inf')
        for j in range(num_nodes):
            if not visited[j] and matrix[current_node][j] < min_duration:
                min_duration = matrix[current_node][j]
                next_node = j
        path.append(next_node)
        visited[next_node] = True
        current_node = next_node
    return path

def get_packing_penalties(num_stops, seed_val):
    shuffled_cargo = list(range(1, num_stops + 1))
    local_random = random.Random(seed_val)
    local_random.shuffle(shuffled_cargo)
    
    total_penalty = 0
    for i in range(1, num_stops + 1):
        target_index = shuffled_cargo.index(i)
        blocking_boxes = len(shuffled_cargo) - 1 - target_index
        total_penalty += 1 + (blocking_boxes * 3)  # 1+3n 공식 적용
        shuffled_cargo.remove(i)
    return total_penalty

def calculate_drive_time(matrix, path_indices):
    total_seconds = 0
    for i in range(len(path_indices) - 1):
        total_seconds += matrix[path_indices[i]][path_indices[i+1]]
    return total_seconds / 60.0  # 초를 분 단위로 변환

def run_simulation(trials=30):
    hub_name = "광주북HUB (월출동)"
    other_locations = list(REAL_LOCATIONS.keys())
    other_locations.remove(hub_name)
    
    results = []
    
    print(f"🚀 총 {trials}회 시뮬레이션 데이터 추출을 시작합니다...")
    
    for i in range(1, trials + 1):
        # 1. 랜덤하게 10곳 추출
        sampled_names = random.sample(other_locations, 10)
        raw_coords = [REAL_LOCATIONS[hub_name]] + [REAL_LOCATIONS[n] for n in sampled_names]
        num_stops = len(sampled_names)
        
        # 2. OSRM API 호출로 소요 시간 매트릭스 확보 (API 차단 방지를 위해 0.2초 대기)
        table_url = f"http://router.project-osrm.org/table/v1/driving/{';'.join([f'{c[0]},{c[1]}' for c in raw_coords])}?annotations=duration"
        resp = requests.get(table_url).json()
        duration_matrix = resp["durations"]
        time.sleep(0.2) 
        
        # 3. 경로 계산 (순수 인덱스 리스트)
        raw_path = list(range(len(raw_coords)))
        tsp_path = solve_tsp(duration_matrix, start_index=0)
        
        # 4. 시간 계산 분리 (T_drive, T_penalty)
        # --- [주행 시간 T_drive] ---
        raw_drive_time = calculate_drive_time(duration_matrix, raw_path)
        tsp_drive_time = calculate_drive_time(duration_matrix, tsp_path)
        
        # --- [하역 페널티 시간 T_penalty] ---
        # 랜덤 난수 시드를 매 회차마다 다르게 주어 다양한 페널티 상황 연출
        raw_penalty_time = get_packing_penalties(num_stops, seed_val=(i * 10))
        tsp_penalty_time = get_packing_penalties(num_stops, seed_val=(i * 20))
        
        # LIFO 적용 시 방해 상자(n)가 0이므로 목적지당 딱 1분씩만 소요됨
        lifo_penalty_time = num_stops * 1.0  
        
        # 5. 각 시나리오별 총합 기록
        row = {
            "Trial": i,
            "S1_Drive": round(raw_drive_time, 1), "S1_Penalty": raw_penalty_time, "S1_Total": round(raw_drive_time + raw_penalty_time, 1),
            "S2_Drive": round(raw_drive_time, 1), "S2_Penalty": lifo_penalty_time, "S2_Total": round(raw_drive_time + lifo_penalty_time, 1),
            "S3_Drive": round(tsp_drive_time, 1), "S3_Penalty": tsp_penalty_time, "S3_Total": round(tsp_drive_time + tsp_penalty_time, 1),
            "S4_Drive": round(tsp_drive_time, 1), "S4_Penalty": lifo_penalty_time, "S4_Total": round(tsp_drive_time + lifo_penalty_time, 1)
        }
        results.append(row)
        print(f"[{i}/{trials}] 완료... (최적화 시간: {row['S4_Total']}분)")
        
    return results

def save_to_csv(data, filename="simulation_results.csv"):
    keys = data[0].keys()
    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
        dict_writer = csv.DictWriter(f, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)
    print(f"\n✅ 데이터 추출 완료! [{filename}] 파일이 생성되었습니다.")

if __name__ == "__main__":
    simulation_data = run_simulation(trials=30)
    save_to_csv(simulation_data)