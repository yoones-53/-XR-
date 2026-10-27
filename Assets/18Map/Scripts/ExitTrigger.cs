using UnityEngine;

public class ExitTrigger : MonoBehaviour
{
    [SerializeField] private GameManager gameManager;
    [SerializeField] private ExitType exitType;

    private void OnTriggerEnter(Collider other)
    {
        if (!other.CompareTag("Player")) return;

        gameManager.SelectExit(exitType);
    }
}