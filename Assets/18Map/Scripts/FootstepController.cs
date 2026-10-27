
using UnityEngine;

public class FootstepController : MonoBehaviour
{
    [Header("플레이어")]
    [SerializeField] private Transform player;

    [Header("오디오")]
    [SerializeField] private AudioSource audioSource;
    [SerializeField] private AudioClip footstepClip;

    [Header("걷기 / 뛰기 발소리 간격")]
    [Range(0.2f, 2f)]
    [SerializeField] private float walkStepInterval = 0.75f;

    [Range(0.2f, 2f)]
    [SerializeField] private float runStepInterval = 0.35f;

    [Header("이동속도 기준")]
    [SerializeField] private float minSpeed = 0.1f;
    [SerializeField] private float runSpeedThreshold = 2.2f;

    [Header("디버그")]
    [SerializeField] private float currentSpeed;

    private Vector3 previousPosition;
    private float nextStepTime;

    private void Start()
    {
        if (player != null)
            previousPosition = player.position;
    }

    private void Update()
    {
        if (player == null ||
            audioSource == null ||
            footstepClip == null)
            return;

        if (Time.deltaTime <= 0f)
            return;

        // 1. 수평 이동 거리 계산
        Vector3 movement = player.position - previousPosition;
        previousPosition = player.position;

        movement.y = 0f;

        // 2. 순간이동 제외
        if (movement.magnitude > 1.5f)
        {
            ResetTracking();
            return;
        }

        // 3. 이동속도 계산 및 보정
        float speed = movement.magnitude / Time.deltaTime;

        currentSpeed = Mathf.Lerp(
            currentSpeed,
            speed,
            1f - Mathf.Exp(-12f * Time.deltaTime)
        );

        // 4. 정지 상태에서는 발소리 없음
        if (currentSpeed < minSpeed)
            return;

        // 5. 걷기 / 뛰기 판단
        bool isRunning = currentSpeed >= runSpeedThreshold;

        float interval = isRunning
            ? runStepInterval
            : walkStepInterval;

        // 6. 발소리 재생 간격 확인
        if (Time.time < nextStepTime)
            return;

        // 7. 발소리 재생
        audioSource.PlayOneShot(footstepClip);

        nextStepTime = Time.time + interval;
    }

    public void ResetTracking()
    {
        if (player == null)
            return;

        previousPosition = player.position;
        currentSpeed = 0f;
        nextStepTime = Time.time;
    }
}
