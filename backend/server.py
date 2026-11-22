import random
from fastapi import FastAPI
import requests
import copy

app = FastAPI()

LON_MIN, LON_MAX = 126.826377, 127.025452
X_MIN_LON, X_MAX_LON = 196.9, -201.8
LAT_MIN, LAT_MAX = 35.149440, 35.262273
Z_MIN_LAT, Z_MAX_LAT = 155.2, -151.3

def gps_to_unity(lon, lat):
    x = X_MIN_LON + (lon - LON_MIN) * (X_MAX_LON - X_MIN_LON) / (LON_MAX - LON_MIN)
    z = Z_MIN_LAT + (lat - LAT_MIN) * (Z_MAX_LAT - Z_MIN_LAT) / (LAT_MAX - LAT_MIN)
    return x + 3.0, z

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

DISTINCT_COLORS = [
    "#FF3333", "#33FF33", "#3333FF", "#FFFF33", "#FF33FF", 
    "#33FFFF", "#FF9933", "#9933FF", "#3399FF", "#99FF33", "#FF3399"
]

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

def get_packing_penalties(names, seed_val):
    num_stops = len(names) - 1
    shuffled_cargo = list(range(1, num_stops + 1))
    
    # ⭐️ 수정된 부분: 서버 전체의 랜덤 시드를 고정하지 않고, 독립적인 지역 랜덤 객체를 사용합니다.
    local_random = random.Random(seed_val)
    local_random.shuffle(shuffled_cargo)
    
    penalties = [0] * len(names)
    for i in range(1, num_stops + 1):
        target_index = shuffled_cargo.index(i)
        blocking_boxes = len(shuffled_cargo) - 1 - target_index
        penalties[i] = 1 + (blocking_boxes * 3) 
        shuffled_cargo.remove(i)
    return penalties

def get_osrm_route(coords):
    coord_strings = [f"{c[0]},{c[1]}" for c in coords]
    url = f"http://router.project-osrm.org/route/v1/driving/{';'.join(coord_strings)}?overview=full&geometries=geojson"
    resp = requests.get(url).json()
    if resp.get("code") == "Ok":
        return resp['routes'][0]['geometry']['coordinates']
    return []

def generate_cargo_data(sampled_names):
    boxes = []
    for idx, dest in enumerate(sampled_names):
        color = DISTINCT_COLORS[idx % len(DISTINCT_COLORS)]
        num_boxes = random.randint(1, 3) 
        for _ in range(num_boxes):
            boxes.append({
                "destination": dest,
                "color_hex": color,
                "size_x": round(random.uniform(0.4, 0.8), 2),
                "size_y": round(random.uniform(0.4, 0.8), 2),
                "size_z": round(random.uniform(0.4, 0.8), 2)
            })
    return boxes

@app.get("/get_route")
def get_route():
    hub_name = "광주북HUB (월출동)"
    hub_coords = REAL_LOCATIONS[hub_name]
    other_locations = {k: v for k, v in REAL_LOCATIONS.items() if k != hub_name}
    
    # ⭐️ 배달 목적지를 10곳으로 고정하여 항상 일정한 퀄리티의 시연을 보장합니다.
    sample_size = 10 
    sampled_names = random.sample(list(other_locations.keys()), sample_size)
    
    raw_names = [hub_name] + sampled_names
    raw_coords = [hub_coords] + [other_locations[n] for n in sampled_names]
    
    table_url = f"http://router.project-osrm.org/table/v1/driving/{';'.join([f'{c[0]},{c[1]}' for c in raw_coords])}?annotations=duration"
    table_resp = requests.get(table_url).json()
    duration_matrix = table_resp["durations"]
    
    tsp_indices = solve_tsp(duration_matrix, start_index=0)
    tsp_names = [raw_names[i] for i in tsp_indices]
    tsp_coords = [raw_coords[i] for i in tsp_indices]
    
    raw_penalties = get_packing_penalties(raw_names, seed_val=100)
    tsp_penalties = get_packing_penalties(tsp_names, seed_val=200)
    lifo_penalties = [0] + [1] * (len(raw_names) - 1) 
    
    raw_osrm_coords = get_osrm_route(raw_coords)
    tsp_osrm_coords = get_osrm_route(tsp_coords)
    
    base_cargo_boxes = generate_cargo_data(sampled_names)

    def build_scenario_data(title, names, coords, osrm_coords, penalties, is_lifo):
        waypoints = [{"name": n, "x": gps_to_unity(c[0], c[1])[0], "z": gps_to_unity(c[0], c[1])[1]} for n, c in zip(names, coords)]
        
        landmark_indices = {}
        for idx, (t_lon, t_lat) in enumerate(coords):
            best_i, min_dist = 0, float('inf')
            for i, c in enumerate(osrm_coords):
                dist = (c[0] - t_lon)**2 + (c[1] - t_lat)**2
                if dist < min_dist:
                    min_dist = dist
                    best_i = i
            landmark_indices[best_i] = {"name": names[idx], "penalty": penalties[idx]}
            
        path = []
        for i, c in enumerate(osrm_coords):
            ux, uz = gps_to_unity(c[0], c[1])
            is_lm = i in landmark_indices
            path.append({
                "x": ux, "z": uz,
                "is_landmark": is_lm,
                "landmark_name": landmark_indices[i]["name"] if is_lm else "",
                "wait_time_minutes": landmark_indices[i]["penalty"] if is_lm else 0
            })

        scenario_boxes = copy.deepcopy(base_cargo_boxes)
        if is_lifo:
            scenario_boxes.sort(key=lambda b: names.index(b["destination"]), reverse=True)
        else:
            random.shuffle(scenario_boxes)

        return {
            "title": title, 
            "waypoints": waypoints, 
            "path": path,
            "boxes": scenario_boxes 
        }

    scenarios = [
        build_scenario_data("1차 시나리오 (TSP X + LIFO X)", raw_names, raw_coords, raw_osrm_coords, raw_penalties, is_lifo=False),
        build_scenario_data("2차 시나리오 (TSP X + LIFO O)", raw_names, raw_coords, raw_osrm_coords, lifo_penalties, is_lifo=True),
        build_scenario_data("3차 시나리오 (TSP O + LIFO X)", tsp_names, tsp_coords, tsp_osrm_coords, tsp_penalties, is_lifo=False),
        build_scenario_data("4차 시나리오 (TSP O + LIFO O) 최적화", tsp_names, tsp_coords, tsp_osrm_coords, lifo_penalties, is_lifo=True)
    ]
    
    return {"scenarios": scenarios}