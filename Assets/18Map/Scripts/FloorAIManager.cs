
using UnityEngine;
using UnityStandardAssets.Characters.ThirdPerson;

public class FloorAIManager : MonoBehaviour
{
    [Header("AI Prefab")]
    [SerializeField] private GameObject aiPrefab;

    [Header("AI Start Point")]
    [SerializeField] private Transform startPoint;

    [Header("AI Destination")]
    [SerializeField] private Transform destination;

    private GameObject currentAI;

    private void Start()
    {
        ResetAI();
    }

    public void ResetAI()
    {
        // 기존 AI 삭제
        if (currentAI != null)
        {
            currentAI.SetActive(false);
            Destroy(currentAI);
        }

        // 시작 위치에 AI 생성
        currentAI = Instantiate(
            aiPrefab,
            startPoint.position,
            startPoint.rotation
        );

        // 기존 AICharacterControl 사용
        AICharacterControl aiControl =
            currentAI.GetComponent<AICharacterControl>();

        if (aiControl != null)
        {
            aiControl.SetTarget(destination);
        }
        else
        {
            Debug.LogError(
                "AI Prefab에 AICharacterControl이 없습니다."
            );
        }
    }
}
