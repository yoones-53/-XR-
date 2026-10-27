using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Play_sound : MonoBehaviour {

    private AudioSource sounds;
	// Use this for initialization
	void Start () {
        sounds = GetComponent<AudioSource>();
	}
	
	// Update is called once per frame
	void Update () {
		
	}

    private void OnTriggerEnter(Collider other)
    {
        sounds.Play();
    }
}
