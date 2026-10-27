using UnityEngine;
using System.Collections;

public class csDestroyDelayed : MonoBehaviour {

	private AudioSource myAudio;

	void Start() {
		myAudio = GetComponent<AudioSource>();
	}

	void OnCollisionEnter(Collision collision)
	{
		myAudio.Play();

		Destroy(this.gameObject , myAudio.clip.length );
	}

}

/*
소리가 사라질때까지 없어져야 할 게임 오브젝트가 남아 있어 부자연스럽다.
*/
