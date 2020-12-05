using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class LandinigZone : MonoBehaviour
{
    public RaycastHit hit;

    // Start is called before the first frame update
    void Start()
    {
    }

    // Update is called once per frame
    void Update()
    {
    }

    public void ResetPose()
    {
        if (Physics.Raycast(transform.position, Vector3.down, out hit))
        {
            transform.position = hit.point;
            //var relForward = transform.TransformDirection(Vector3.forward);
            //transform.rotation = Quaternion.LookRotation(relForward, hit.normal);
            //var upDir = Vector3.Cross(hit.point - Vector3.up, hit.point - Vector3.up).normalized;
            //transform.up = -upDir;// hit.normal;
        }
    }
}
