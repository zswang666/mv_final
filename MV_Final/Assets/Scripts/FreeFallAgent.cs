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

    public GameObject m_DustStorm;
    private bool m_DustStormEnable;

    private bool m_WindZoneEnable;
    private Vector3 m_WindZoneForce;

    public GameObject m_Light;

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

        if (m_WindZoneEnable)
        {
            Debug.Log(m_WindZoneForce);
            m_RigidBody.AddForce(m_WindZoneForce);
        }

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
        transform.rotation = Quaternion.Euler(90.0f, 0.0f, 0.0f);
        m_RigidBody.velocity = new Vector3();

        m_RigidBody.mass = m_ResetParams.GetWithDefault("mass", 1.0f);
        m_ThrustMultiplier = m_ResetParams.GetWithDefault("thrust_multiplier", 10.0f);
        m_ActionMode = m_ResetParams.GetWithDefault("action_mode", 0.0f);

        // duststorm
        m_DustStormEnable = m_ResetParams.GetWithDefault("dust_storm.enable", 0.0f) > 0.0f;
        m_DustStorm.SetActive(m_DustStormEnable);
        m_DustStorm.transform.position = new Vector3(position.x, position.y - 16.4f, position.z);
        var main = m_DustStorm.GetComponent<ParticleSystem>().main;
        main.startSizeMultiplier = m_ResetParams.GetWithDefault("dust_storm.start_size_multiplier", 25.0f);

        // wind
        m_WindZoneEnable = m_ResetParams.GetWithDefault("wind_zone.enable", 0.0f) > 0.0f;
        m_WindZoneForce = new Vector3(m_ResetParams.GetWithDefault("wind_zone.force.x", 1.0f),
                                      m_ResetParams.GetWithDefault("wind_zone.force.y", 0.0f),
                                      m_ResetParams.GetWithDefault("wind_zone.force.z", 1.0f));

        // freeze rigid body
        if (m_ResetParams.GetWithDefault("rigid_body.freeze_position.x", 0.0f) > 0.0f)
        {
            m_RigidBody.constraints = m_RigidBody.constraints | RigidbodyConstraints.FreezePositionX;
        }
        if (m_ResetParams.GetWithDefault("rigid_body.freeze_position.y", 0.0f) > 0.0f)
        {
            m_RigidBody.constraints = m_RigidBody.constraints | RigidbodyConstraints.FreezePositionY;
        }
        if (m_ResetParams.GetWithDefault("rigid_body.freeze_position.z", 0.0f) > 0.0f)
        {
            m_RigidBody.constraints = m_RigidBody.constraints | RigidbodyConstraints.FreezePositionZ;
        }
        if (m_ResetParams.GetWithDefault("rigid_body.freeze_rotation.x", 1.0f) > 0.0f)
        {
            m_RigidBody.constraints = m_RigidBody.constraints | RigidbodyConstraints.FreezeRotationX;
        }
        if (m_ResetParams.GetWithDefault("rigid_body.freeze_rotation.y", 1.0f) > 0.0f)
        {
            m_RigidBody.constraints = m_RigidBody.constraints | RigidbodyConstraints.FreezeRotationY;
        }
        if (m_ResetParams.GetWithDefault("rigid_body.freeze_rotation.z", 1.0f) > 0.0f)
        {
            m_RigidBody.constraints = m_RigidBody.constraints | RigidbodyConstraints.FreezeRotationZ;
        }

        // cloud shadow
        m_Light.GetComponent<EntroPi.CloudShadows>().enabled = m_ResetParams.GetWithDefault("cloud_shadow.enable", 0.0f) > 0.0f;
        m_Light.GetComponent<EntroPi.CloudShadows>().SpeedMultiplier = m_ResetParams.GetWithDefault("cloud_shadow.speed_multiplier", 5.0f);
        m_Light.GetComponent<EntroPi.CloudShadows>().CoverageModifier = m_ResetParams.GetWithDefault("cloud_shadow.coverage_modifier", 0.0f);
    }
}
