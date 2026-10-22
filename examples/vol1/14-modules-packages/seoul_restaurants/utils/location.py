# [1권 Chapter 14: 모듈과 패키지 · 14.4 패키지 기초 · manuscript/chapters/14-modules-packages.md:591]
# seoul_restaurants/utils/location.py
"""
위치 관련 유틸리티
"""
import math
from typing import Any, Dict, Tuple

# 서울 주요 지역 좌표 (위도, 경도)
SEOUL_DISTRICTS = {
    '강남구': (37.5172, 127.0473),
    '강동구': (37.5301, 127.1238),
    '강북구': (37.6396, 127.0257),
    '강서구': (37.5509, 126.8495),
    '관악구': (37.4781, 126.9515),
    '광진구': (37.5384, 127.0822),
    '구로구': (37.4954, 126.8874),
    '금천구': (37.4519, 126.9018),
    '노원구': (37.6544, 127.0565),
    '도봉구': (37.6686, 127.0471),
    '동대문구': (37.5814, 127.0098),
    '동작구': (37.5124, 126.9393),
    '마포구': (37.5663, 126.9019),
    '서대문구': (37.5791, 126.9368),
    '서초구': (37.4837, 127.0324),
    '성동구': (37.5636, 127.0365),
    '성북구': (37.6066, 127.0182),
    '송파구': (37.5145, 127.1059),
    '양천구': (37.5167, 126.8665),
    '영등포구': (37.5264, 126.8962),
    '용산구': (37.5384, 126.9654),
    '은평구': (37.6176, 126.9227),
    '종로구': (37.5735, 126.9788),
    '중구': (37.5640, 126.9975),
    '중랑구': (37.6061, 127.0925)
}

def get_district_info(district: str) -> Dict[str, Any]:
    """지역 정보 조회"""
    coords = SEOUL_DISTRICTS.get(district)
    if not coords:
        return {'error': f'알 수 없는 지역: {district}'}
    
    return {
        'name': district,
        'latitude': coords[0],
        'longitude': coords[1],
        'region': _get_region_name(district)
    }

def _get_region_name(district: str) -> str:
    """지역별 권역 이름"""
    gangbuk = ['종로구', '중구', '용산구', '성동구', '광진구', '동대문구', '중랑구', '성북구', '강북구', '도봉구', '노원구', '은평구', '서대문구', '마포구']
    gangnam = ['강남구', '서초구', '송파구', '강동구']
    
    if district in gangbuk:
        return '강북'
    elif district in gangnam:
        return '강남'
    else:
        return '기타'

class DistanceCalculator:
    """거리 계산기"""
    
    @staticmethod
    def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """두 지점 간 거리 계산 (km)"""
        R = 6371  # 지구 반지름 (km)
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_lat / 2) ** 2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    @classmethod
    def distance_between_districts(cls, district1: str, district2: str) -> float:
        """두 지역 간 거리"""
        coords1 = SEOUL_DISTRICTS.get(district1)
        coords2 = SEOUL_DISTRICTS.get(district2)
        
        if not coords1 or not coords2:
            raise ValueError(f"알 수 없는 지역: {district1} 또는 {district2}")
        
        return cls.haversine_distance(coords1[0], coords1[1], coords2[0], coords2[1])
