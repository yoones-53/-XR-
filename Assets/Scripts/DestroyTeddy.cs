using UnityEngine;

public class DestroyTeddy : MonoBehaviour
{
    private void OnTriggerEnter(Collider other)
    {
        if (other.CompareTag("Teddy"))
        {
            Destroy(other.gameObject);
        }
    }
}