using UnityEngine;

public class PosterImageAnomaly : AnomalyBase
{
    [Header("포스터 Quad의 Renderer")]
    [SerializeField] private Renderer targetRenderer;

    [Header("이상현상 포스터 텍스처")]
    [SerializeField] private Texture anomalyTexture;

    private Material runtimeMaterial;
    private Texture originalTexture;

    private void Awake()
    {
        if (targetRenderer == null)
        {
            Debug.LogError($"{name}: targetRenderer가 비어있음");
            return;
        }

        // 런타임 전용 머티리얼 인스턴스
        runtimeMaterial = targetRenderer.material;

        // URP면 _BaseMap, Built-in이면 mainTexture
        if (runtimeMaterial.HasProperty("_BaseMap"))
            originalTexture = runtimeMaterial.GetTexture("_BaseMap");
        else
            originalTexture = runtimeMaterial.mainTexture;
    }

    public override void Activate()
    {
        if (runtimeMaterial == null || anomalyTexture == null) return;

        if (runtimeMaterial.HasProperty("_BaseMap"))
            runtimeMaterial.SetTexture("_BaseMap", anomalyTexture);
        else
            runtimeMaterial.mainTexture = anomalyTexture;
    }

    public override void ResetAnomaly()
    {
        if (runtimeMaterial == null) return;

        if (runtimeMaterial.HasProperty("_BaseMap"))
            runtimeMaterial.SetTexture("_BaseMap", originalTexture);
        else
            runtimeMaterial.mainTexture = originalTexture;
    }
}