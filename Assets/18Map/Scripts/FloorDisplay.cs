using UnityEngine;
using TMPro;

public class FloorDisplay : MonoBehaviour
{
    [Header("참조")]
    [SerializeField] private GameManager gameManager;
    [SerializeField] private TMP_Text floorText;

    private int previousFloor = -1;

    private void Start()
    {
        UpdateFloor();
    }

    private void Update()
    {
        if (gameManager == null || floorText == null)
            return;

        // 층수가 변경되었을 때만 갱신
        if (previousFloor != gameManager.CurrentFloor)
        {
            UpdateFloor();
        }
    }

    private void UpdateFloor()
    {
        if (gameManager == null || floorText == null)
            return;

        previousFloor = gameManager.CurrentFloor;

        floorText.text = previousFloor + "F";
    }
}
