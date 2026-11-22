import requests
import json

def get_real_road_route(start_coord, end_coord):
    # OSRM 무료 공개 서버 (Driving: 자동차 도로 기준)
    # 좌표는 반드시 [경도(Longitude), 위도(Latitude)] 순서로 입력해야 합니다.
    base_url = "http://router.project-osrm.org/route/v1/driving/"
    
    # URL 완성: 시작경도,시작위도;도착경도,도착위도
    coordinates = f"{start_coord[0]},{start_coord[1]};{end_coord[0]},{end_coord[1]}"
    
    # overview=full (전체 경로 요청), geometries=geojson (좌표 배열 형태로 받기)
    url = f"{base_url}{coordinates}?overview=full&geometries=geojson"

    print("OSRM 서버에 길찾기 요청 중...")
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        
        # 도로를 따라 꺾이는 수많은 '빵부스러기(Breadcrumbs)' 좌표들 추출
        route_geometry = data['routes'][0]['geometry']['coordinates']
        distance = data['routes'][0]['distance'] # 단위: 미터(m)
        duration = data['routes'][0]['duration'] # 단위: 초(s)
        
        print(f"✅ 길찾기 성공!")
        print(f"총 이동 거리: {distance} 미터")
        print(f"예상 소요 시간: {duration} 초")
        print(f"추출된 궤적(점)의 개수: {len(route_geometry)}개")
        print(f"첫 3개 좌표 샘플: {route_geometry[:3]}")
        
        return route_geometry
    else:
        print(f"❌ 에러 발생: {response.status_code}")
        return None

# 테스트 실행: 광주 월출동(출발) -> 전남대(도착) 임의의 위경도
start_lon_lat = [126.8533, 35.2155] # 월출동 부근
end_lon_lat = [126.9048, 35.1764]   # 전남대 부근

get_real_road_route(start_lon_lat, end_lon_lat)