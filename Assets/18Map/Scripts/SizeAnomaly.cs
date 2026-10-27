
using UnityEngine;

public class SizeAnomaly : AnomalyBase
{
    [Header("크기를 변경할 오브젝트")]
    [SerializeField] private Transform[] targets;

    [Header("크기 배율")]
    [SerializeField] private float multiplier = 2f;

    private Vector3[] originalScales;

    private void Awake()
    {
        originalScales = new Vector3[targets.Length];

        // 모든 오브젝트의 원래 크기 저장
        for (int i = 0; i < targets.Length; i++)
        {
            if (targets[i] == null) continue;

            originalScales[i] = targets[i].localScale;
        }
    }

    public override void Activate()
    {
        // 모든 오브젝트 크기 변경
        for (int i = 0; i < targets.Length; i++)
        {
            if (targets[i] == null) continue;

            targets[i].localScale =
                originalScales[i] * multiplier;
        }
    }

    public override void ResetAnomaly()
    {
        // 모든 오브젝트 원래 크기로 복원
        for (int i = 0; i < targets.Length; i++)
        {
            if (targets[i] == null) continue;

            targets[i].localScale = originalScales[i];
        }
    }
}
