using UnityEngine;
using Unity.MLAgents;
using Unity.MLAgents.Sensors;

public class FlyCameraAgent : Agent
{
    /*
        Reference: FlyCamera.cs
        wasd : basic movement
        shift : Makes camera accelerate
        space : Moves camera on X and Z axis only.  So camera doesn't gain any height
    */

    EnvironmentParameters m_ResetParams;

    private float camSens = 0.25f; // How sensitive it with mouse
    private float keySpeed = 10.0f; // regular speed

    Vector3 m_LastMouse = new Vector3(255, 255, 255); // kind of in the middle of the screen, rather than at the top (play)
    Vector3 m_DeltaMouse = new Vector3(0.0f, 0.0f, 0.0f);


    public override void Initialize()
    {
        Debug.Log("Initialize agent.");
        m_ResetParams = Academy.Instance.EnvironmentParameters;
    }

    public override void CollectObservations(VectorSensor sensor)
    {
        // Camera sensor specified with GUI
    }

    public override void OnActionReceived(float[] vectorAction)
    {
        /* Convert action to agent motion */
        // Rotation; 3-dim [2:] (the last dim should always be 0, not used); range Mouse movement in pixel
        var mRot = new Vector3(-vectorAction[3] * camSens, vectorAction[2] * camSens, 0);
        mRot = new Vector3(transform.eulerAngles.x + mRot.x,
                           transform.eulerAngles.y + mRot.y, 0);
        transform.eulerAngles = mRot;

        // Translation; 2-dim [:2]; range [-1, 1]
        var p = new Vector3();
        p[0] = keySpeed * Mathf.Clamp(vectorAction[0], -1f, 1f);
        p[2] = keySpeed * Mathf.Clamp(vectorAction[1], -1f, 1f);
        p = p * 0.1f;
        transform.Translate(p);
    }

    public override void Heuristic(float[] actionsOut)
    {
        /* Convert keyboard and mouse input to action */
        // Keyboard command (use continous action here just to make rotation with mouse easier)
        actionsOut[0] = Input.GetAxis("Horizontal");
        actionsOut[1] = Input.GetAxis("Vertical");

        m_DeltaMouse = Input.mousePosition - m_LastMouse;
        actionsOut[2] = m_DeltaMouse.x;
        actionsOut[3] = m_DeltaMouse.y;
        actionsOut[4] = m_DeltaMouse.z;
        m_LastMouse = Input.mousePosition;
    }

    public override void OnEpisodeBegin()
    {
        // Fixed starting pose
        transform.position = new Vector3(-120.9f, 10.0f, 792.7f);
        transform.rotation = Quaternion.Euler(0.0f, 0.0f, 0.0f);

        keySpeed = m_ResetParams.GetWithDefault("key_speed", 10.0f);
        camSens = m_ResetParams.GetWithDefault("cam_sens", 0.25f);
    }
}
