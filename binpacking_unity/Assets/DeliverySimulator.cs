using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Networking;
using TMPro;

public class DeliverySimulator : MonoBehaviour
{
    [Header("시뮬레이션 속도 및 시간 설정")]
    public float realSpeed = 8.33f;       // 현실 트럭 속도 (초속 8.33m = 시속 약 30km)
    public float drivingTimeScale = 10f;  // 주행 시 배속 (10배속)
    
    // 가상 세계의 1분이 현실의 몇 초만에 틱(Tick) 될지 결정 (0.05면 10분 오르는데 0.5초 소요)
    public float virtualMinuteToRealSeconds = 0.05f; 

    public float timeAmplifier;

    [Header("시뮬레이션 오브젝트 설정")]
    public Transform truck;           
    public LineRenderer pathLine;
    public GameObject waypointPrefab;  
    private List<GameObject> spawnedPins = new List<GameObject>();

    [Header("UI 및 3D 화물 설정")]
    public TextMeshProUGUI liveTimerText;
    public GameObject boxPrefab;       
    public Transform cargoAnchor;      
    
    private List<GameObject> activeBoxes = new List<GameObject>(); 

    [System.Serializable]
    public class BoxData {
        public string destination;
        public string color_hex;
        public float size_x;
        public float size_y;
        public float size_z;
    }

    [System.Serializable]
    public class Coordinate {
        public float x; public float z;
        public bool is_landmark; 
        public string landmark_name;
        public float wait_time_minutes; 
    }

    [System.Serializable]
    public class WaypointData { public string name; public float x; public float z; }

    [System.Serializable]
    public class ScenarioData {
        public string title;
        public List<WaypointData> waypoints;
        public List<Coordinate> path;
        public List<BoxData> boxes; 
    }

    [System.Serializable]
    public class RouteResponse { public List<ScenarioData> scenarios; }

    void Start()
    {
        StartCoroutine(RequestRouteFromPython());
    }

    IEnumerator RequestRouteFromPython()
    {
        string url = "http://localhost:8000/get_route";
        using (UnityWebRequest webRequest = UnityWebRequest.Get(url))
        {
            yield return webRequest.SendWebRequest();

            if (webRequest.result == UnityWebRequest.Result.Success)
            {
                RouteResponse data = JsonUtility.FromJson<RouteResponse>(webRequest.downloadHandler.text);
                StartCoroutine(PlayAllScenarios(data.scenarios));
            }
            else
            {
                Debug.LogError("에러: " + webRequest.error);
            }
        }
    }

    IEnumerator PlayAllScenarios(List<ScenarioData> scenarios)
    {
        for (int i = 0; i < scenarios.Count; i++)
        {
            ScenarioData sc = scenarios[i];
            Debug.Log($"<color=#00FFFF><b>▶ [{sc.title}] 시작</b></color>");

            // 1. 핀 및 기존 상자 초기화
            foreach (GameObject pin in spawnedPins) Destroy(pin);
            spawnedPins.Clear();
            ClearCargoBoxes();

            // 2. 핀 및 경로 선 그리기
            foreach (WaypointData wp in sc.waypoints)
            {
                GameObject pin = Instantiate(waypointPrefab, new Vector3(wp.x, 0.3f, wp.z), Quaternion.identity);
                pin.name = wp.name;
                spawnedPins.Add(pin);
            }

            pathLine.positionCount = sc.path.Count;
            for (int j = 0; j < sc.path.Count; j++) 
                pathLine.SetPosition(j, new Vector3(sc.path[j].x, 0.5f, sc.path[j].z));

            // 3. 트럭 위치 초기화 및 화물(Box) 적재
            if (sc.path.Count > 0)
                truck.position = new Vector3(sc.path[0].x, truck.position.y, sc.path[0].z);
            
            LoadCargoBoxes(sc.boxes);

            float totalVirtualMinutes = 0f;

            // 4. 주행 시작 전 엔진 시간 배속(10배속) 켜기
            Time.timeScale = drivingTimeScale;

            for (int j = 0; j < sc.path.Count; j++)
            {
                Coordinate coord = sc.path[j];
                Vector3 targetPos = new Vector3(coord.x, truck.position.y, coord.z);
                truck.LookAt(targetPos);

                while (Vector3.Distance(truck.position, targetPos) > 0.05f)
                {
                    // realSpeed로 이동하지만 Time.timeScale이 켜져 있어 빠르게 주행
                    truck.position = Vector3.MoveTowards(truck.position, targetPos, realSpeed * Time.deltaTime);
                    
                    // Time.deltaTime을 60으로 나누어 가상 세계의 분(Minutes) 누적
                    totalVirtualMinutes += (Time.deltaTime / 60f) * timeAmplifier; 
                    UpdateUIText(sc.title, totalVirtualMinutes);
                    yield return null; 
                }

                // ⭐️ 목적지 도착 시 상자 하역 (Unload)
                if (coord.is_landmark && coord.landmark_name != "광주북HUB (월출동)")
                {
                    // 도착: 짐 내리는 모습을 확실히 보여주기 위해 배속을 1배로 풂
                    Time.timeScale = 1f;

                    UnloadBoxesAtDestination(coord.landmark_name); 

                    // ⭐️ 요청하신 서서히 증가하는 타이머 로직 복구
                    float penalty = coord.wait_time_minutes;
                    float waitTimer = 0f;
                    
                    while (waitTimer < penalty)
                    {
                        // virtualMinuteToRealSeconds 비율에 맞춰 타이머 숫자가 프레임마다 차르르륵 올라감
                        float timeAdd = (Time.deltaTime / virtualMinuteToRealSeconds); 
                        waitTimer += timeAdd;
                        totalVirtualMinutes += timeAdd;
                        
                        // 정확한 목표치를 넘지 않도록 보정
                        if (waitTimer > penalty) 
                        {
                            totalVirtualMinutes -= (waitTimer - penalty);
                            waitTimer = penalty;
                        }
                        
                        UpdateUIText(sc.title, totalVirtualMinutes);
                        yield return null;
                    }

                    // 타이머가 다 올라간 후 아주 약간의 여운(0.5초)을 주고 출발
                    yield return new WaitForSeconds(0.5f);

                    // 다시 주행을 위해 배속(10배속) 켜기
                    Time.timeScale = drivingTimeScale;
                }
            }

            Time.timeScale = 1f;

            Debug.Log($"<color=#00FF00><b>🏁 [{sc.title}] 종료. 총 시간: {Mathf.RoundToInt(totalVirtualMinutes)}분</b></color>");
            yield return new WaitForSeconds(3.0f);
        }
    }

    void LoadCargoBoxes(List<BoxData> boxes)
    {
        float currentX = 0f; float currentY = 0f; float currentZ = 0f;
        float rowMaxY = 0f; 
        float cargoWidth = 2.0f; 

        foreach (BoxData b in boxes)
        {
            if (boxPrefab == null || cargoAnchor == null) return;

            if (currentX + b.size_x > cargoWidth)
            {
                currentX = 0f;
                currentY += rowMaxY;
                rowMaxY = 0f;
                
                if (currentY > 1.5f) 
                {
                    currentY = 0f;
                    currentZ -= 1.0f; 
                }
            }

            GameObject boxObj = Instantiate(boxPrefab, cargoAnchor);
            boxObj.transform.localScale = new Vector3(b.size_x, b.size_y, b.size_z);
            boxObj.name = b.destination;

            float posX = currentX + (b.size_x / 2f);
            float posY = currentY + (b.size_y / 2f);
            float posZ = currentZ - (b.size_z / 2f);
            boxObj.transform.localPosition = new Vector3(posX, posY, posZ);

            Color parsedColor;
            if (ColorUtility.TryParseHtmlString(b.color_hex, out parsedColor))
            {
                boxObj.GetComponent<Renderer>().material.color = parsedColor;
            }

            activeBoxes.Add(boxObj);
            
            currentX += b.size_x;
            rowMaxY = Mathf.Max(rowMaxY, b.size_y);
        }
    }

    void UnloadBoxesAtDestination(string destinationName)
    {
        List<GameObject> toRemove = new List<GameObject>();
        foreach (GameObject box in activeBoxes)
        {
            if (box.name == destinationName) toRemove.Add(box);
        }

        foreach (GameObject box in toRemove)
        {
            activeBoxes.Remove(box);
            Destroy(box); 
        }
    }

    void ClearCargoBoxes()
    {
        foreach (GameObject box in activeBoxes) Destroy(box);
        activeBoxes.Clear();
    }

    void UpdateUIText(string title, float minutes)
    {
        if (liveTimerText != null)
        {
            liveTimerText.text = $"<color=yellow><b>{title}</b></color>\n" +
                                 $"누적 시간 : <color=white><b>{Mathf.RoundToInt(minutes)} 분</b></color>";
        }
    }
}