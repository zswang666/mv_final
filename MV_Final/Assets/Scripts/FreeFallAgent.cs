using UnityEngine;
using Unity.MLAgents;
using Unity.MLAgents.Sensors;

[RequireComponent(typeof(Rigidbody))]
public class FreeFallAgent : Agent
{
    EnvironmentParameters m_ResetParams;

    private Rigidbody m_RigidBody;
    private float m_ThrustMultiplier;
    private float m_ActionMode;

    public override void Initialize()
    {
        Debug.Log("Initialize agent.");
        m_RigidBody = GetComponent<Rigidbody>();
        m_ResetParams = Academy.Instance.EnvironmentParameters;
    }

    public override void CollectObservations(VectorSensor sensor)
    {
        // Camera sensor specified with GUI
        // get speed
        sensor.AddObservation(m_RigidBody.velocity); // 3-dim
    }

    public override void OnActionReceived(float[] vectorAction)
    {
        /* Convert action to agent motion */
        var thrust = new Vector3(0.0f, m_ThrustMultiplier * vectorAction[0], 0.0f);

        if (m_ActionMode == 0.0f)
        {
            m_RigidBody.AddForce(thrust);
        }
        else
        {
            m_RigidBody.velocity = thrust;
        }
        

        var end_episode = m_ResetParams.GetWithDefault("end_episode", 0.0f);
        if (end_episode > 0.0f)
        {
            EndEpisode();
        }
    }

    public override void Heuristic(float[] actionsOut)
    {
        /* Convert keyboard input to action */
        // up and down thrust
        actionsOut[0] = Input.GetAxis("Vertical");
    }

    public override void OnEpisodeBegin()
    {
        // Set environment parameter (can be accessed via channel from python)
        var position = new Vector3();
        position.x = m_ResetParams.GetWithDefault("position.x", -120.9f);
        position.y = m_ResetParams.GetWithDefault("position.y", 27.4834f);
        position.z = m_ResetParams.GetWithDefault("position.z", 792.7f);
        transform.position = position;
        transform.rotation = Quaternion.Euler(0.0f, 0.0f, 0.0f);
        m_RigidBody.velocity = new Vector3();

        m_RigidBody.mass = m_ResetParams.GetWithDefault("mass", 1.0f);
        m_ThrustMultiplier = m_ResetParams.GetWithDefault("thrust_multiplier", 10.0f);
        m_ActionMode = m_ResetParams.GetWithDefault("action_mode", 0.0f);
    }
}
