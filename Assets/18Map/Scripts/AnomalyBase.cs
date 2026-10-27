using UnityEngine;

public abstract class AnomalyBase : MonoBehaviour
{
    // 이상현상 발생
    public abstract void Activate();

    // 정상 상태 복원
    public abstract void ResetAnomaly();
}