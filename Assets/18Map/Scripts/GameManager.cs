
using UnityEngine;

public enum ExitType
{
    Elevator,
    Stairs
}

public class GameManager : MonoBehaviour
{
    [Header("Managers")]
    [SerializeField] private FloorAIManager floorAIManager;
    [SerializeField] private AnomalyManager anomalyManager;

    [Header("Player")]
    [SerializeField] private Transform player;
    [SerializeField] private Transform startPoint;

    public int CurrentFloor { get; private set; } = 5;

    private bool isTransitioning;

    private void Start()
    {
        anomalyManager.GenerateFloor();

        // FloorAIManager의 Start()에서
        // 최초 AI가 생성되므로 여기서는 호출하지 않음
    }

    public void SelectExit(ExitType exit)
    {
        if (isTransitioning) return;

        isTransitioning = true;

        bool choseStairs = exit == ExitType.Stairs;

        bool correct =
            choseStairs == anomalyManager.HasAnomaly;

        if (!correct)
        {
            CurrentFloor = 5;
        }
        else if (CurrentFloor == 1)
        {
            Debug.Log("게임 클리어!");
            CurrentFloor = 5;
        }
        else
        {
            CurrentFloor--;
        }

        // 추후 화면 암전 연출 추가

        // 1. 플레이어 시작 지점 이동
        CharacterController cc =
            player.GetComponent<CharacterController>();

        if (cc != null) cc.enabled = false;

        player.SetPositionAndRotation(
            startPoint.position,
            startPoint.rotation
        );

        if (cc != null) cc.enabled = true;

        // 2. 이상현상 초기화 + 다음 층 추첨
        anomalyManager.GenerateFloor();

        // 3. AI 캐릭터 초기화 + 재생성
        floorAIManager.ResetAI();

        Debug.Log("현재 층: " + CurrentFloor);

        isTransitioning = false;
    }
}
