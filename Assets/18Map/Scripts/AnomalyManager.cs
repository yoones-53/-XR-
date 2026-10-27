
using System.Collections.Generic;
using UnityEngine;

public class AnomalyManager : MonoBehaviour
{
    [Header("이상현상 목록")]
    [SerializeField]
    private List<AnomalyBase> anomalies = new();

    [Header("디버그 - 강제 이상현상")]
    [SerializeField] private bool forceSpecificAnomaly = false;
    [SerializeField] private AnomalyBase forcedAnomaly;

    // 최초 시작층 여부
    private bool isFirstFloor = true;

    // 이미 출현한 이상현상
    private HashSet<AnomalyBase> experienced = new();

    // 현재 층의 이상현상
    private AnomalyBase currentAnomaly;

    public bool HasAnomaly => currentAnomaly != null;

    public void GenerateFloor()
    {
        // 1. 이전 이상현상 초기화
        if (currentAnomaly != null)
        {
            currentAnomaly.ResetAnomaly();
            currentAnomaly = null;
        }

        // 2. 최초 5층 튜토리얼
        // 강제 테스트 모드에서는 건너뜀
        if (isFirstFloor)
        {
            isFirstFloor = false;

            if (!forceSpecificAnomaly)
            {
                Debug.Log("최초 5층: 튜토리얼 (정상층)");
                return;
            }
        }

        // 3. 강제 이상현상 모드
        if (forceSpecificAnomaly)
        {
            if (forcedAnomaly == null)
            {
                Debug.LogWarning(
                    "강제 이상현상이 지정되지 않았습니다.");
                return;
            }

            currentAnomaly = forcedAnomaly;
            currentAnomaly.Activate();

            Debug.Log("[강제 이상현상] " +
                currentAnomaly.GetType().Name);

            return;
        }

        // 4. 정상층 45% / 이상현상층 55%
        bool spawnAnomaly = Random.value < 0.55f;

        if (!spawnAnomaly)
        {
            Debug.Log("정상 층");
            return;
        }

        // 5. 아직 경험하지 않은 이상현상 목록
        List<AnomalyBase> available = GetAvailable();

        // 6. 모두 경험했으면 초기화
        if (available.Count == 0)
        {
            experienced.Clear();
            available = GetAvailable();
        }

        if (available.Count == 0)
        {
            Debug.LogWarning(
                "등록된 이상현상이 없습니다.");
            return;
        }

        // 7. 랜덤 선택
        int index = Random.Range(0, available.Count);

        currentAnomaly = available[index];

        // 8. 이상현상 활성화
        currentAnomaly.Activate();

        // 9. 경험 기록
        experienced.Add(currentAnomaly);

        Debug.Log("이상현상: " +
            currentAnomaly.GetType().Name);
    }

    private List<AnomalyBase> GetAvailable()
    {
        List<AnomalyBase> result = new();

        foreach (AnomalyBase anomaly in anomalies)
        {
            if (anomaly != null &&
                !experienced.Contains(anomaly) &&
                !result.Contains(anomaly))
            {
                result.Add(anomaly);
            }
        }

        return result;
    }

    // Inspector에서 수동 테스트 가능
    [ContextMenu("Test Generate Floor")]
    private void TestGenerateFloor()
    {
        GenerateFloor();
    }
}
