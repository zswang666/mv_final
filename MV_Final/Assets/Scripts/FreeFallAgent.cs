using UnityEngine;
using Unity.MLAgents;
using Unity.MLAgents.Sensors;

[RequireComponent(typeof(Rigidbody))]
public class FreeFallAgent : Agent
{
    EnvironmentParameters m_ResetParams;

    private Rigidbody m_RigidBody;
    private float m_ControlMultiplier;
    private float m_ActionMode;

    public GameObject m_DustStorm;
    private bool m_DustStormEnable;

    private bool m_WindZoneEnable;
    private Vector3 m_WindZoneForceLow;
    private Vector3 m_WindZoneForceHigh;

    public GameObject m_Light;
    private bool m_rotationalLightEnable;
    private float m_rotationalLightInterval;
    private float m_rotationalLightStep;
    private Vector2 m_rotationalLightBound;

    public GameObject m_LandingZone;
    private bool m_LandingZoneEnable;
    private Vector3 m_LandingZoneOffset;

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
        sensor.AddObservation(m_RigidBody.angularVelocity); // 3-dim
        if (m_LandingZoneEnable)
        {
            sensor.AddObservation(m_LandingZone.transform.position - transform.position);
        }
        else
        {
            sensor.AddObservation(Vector3.zero);
        }
    }

    public override void OnActionReceived(float[] vectorAction)
    {
        /* Convert action to agent motion */
        if (m_WindZoneEnable)
        {
            var windZoneForce = new Vector3(Random.Range(m_WindZoneForceLow[0], m_WindZoneForceHigh[0]),
                                            Random.Range(m_WindZoneForceLow[1], m_WindZoneForceHigh[1]),
                                            Random.Range(m_WindZoneForceLow[2], m_WindZoneForceHigh[2]));
            m_RigidBody.AddForce(windZoneForce);
        }

        if (m_ActionMode == 0.0f)
        {
            var thrust = new Vector3(m_ControlMultiplier * vectorAction[0], 
                                     m_ControlMultiplier * vectorAction[1],
                                     m_ControlMultiplier * vectorAction[2]);
            var torque = new Vector3(m_ControlMultiplier * vectorAction[3],
                                     m_ControlMultiplier * vectorAction[4],
                                     m_ControlMultiplier * vectorAction[5]);
            m_RigidBody.AddForce(thrust);
            m_RigidBody.AddTorque(torque);
        }
        else
        {
            var velocity = new Vector3(m_ControlMultiplier * vectorAction[0],
                                       m_ControlMultiplier * vectorAction[1],
                                       m_ControlMultiplier * vectorAction[2]);
            var angularVelocity = new Vector3(m_ControlMultiplier * vectorAction[3],
                                              m_ControlMultiplier * vectorAction[4],
                                              m_ControlMultiplier * vectorAction[5]);
            m_RigidBody.velocity = velocity;
            m_RigidBody.angularVelocity = angularVelocity;
        }

        // update rotational light
        if (m_rotationalLightEnable)
        {
            float new_light_rotation_x = m_Light.transform.rotation.eulerAngles.x + m_rotationalLightStep;
            if (new_light_rotation_x > m_rotationalLightBound.y)
            {
                new_light_rotation_x = m_rotationalLightBound.y;
                m_rotationalLightStep = -1.0f * m_rotationalLightStep;
            }
            else if (new_light_rotation_x < m_rotationalLightBound.x)
            {
                new_light_rotation_x = m_rotationalLightBound.x;
                m_rotationalLightStep = -1.0f * m_rotationalLightStep;
            }
            m_Light.transform.rotation = Quaternion.Euler(new_light_rotation_x, 
                                                          m_Light.transform.rotation.eulerAngles.y, 
                                                          m_Light.transform.rotation.eulerAngles.z);
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
        actionsOut[1] = Input.GetAxis("Vertical");
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
        m_ControlMultiplier = m_ResetParams.GetWithDefault("control_multiplier", 10.0f);
        m_ActionMode = m_ResetParams.GetWithDefault("action_mode", 0.0f);

        // duststorm
        m_DustStormEnable = m_ResetParams.GetWithDefault("dust_storm.enable", 0.0f) > 0.0f;
        m_DustStorm.SetActive(m_DustStormEnable);
        m_DustStorm.transform.position = new Vector3(position.x, position.y - 16.4f, position.z);
        var main = m_DustStorm.GetComponent<ParticleSystem>().main;
        main.startSizeMultiplier = m_ResetParams.GetWithDefault("dust_storm.start_size_multiplier", 25.0f);

        // wind
        m_WindZoneEnable = m_ResetParams.GetWithDefault("wind_zone.enable", 0.0f) > 0.0f;
        m_WindZoneForceLow = new Vector3(m_ResetParams.GetWithDefault("wind_zone.force_low.x", -1.0f),
                                         m_ResetParams.GetWithDefault("wind_zone.force_low.y", 0.0f),
                                         m_ResetParams.GetWithDefault("wind_zone.force_low.z", -1.0f));
        m_WindZoneForceHigh = new Vector3(m_ResetParams.GetWithDefault("wind_zone.force_high.x", 1.0f),
                                          m_ResetParams.GetWithDefault("wind_zone.force_high.y", 0.0f),
                                          m_ResetParams.GetWithDefault("wind_zone.force_high.z", 1.0f));

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
        if (m_ResetParams.GetWithDefault("rigid_body.freeze_rotation.x", 0.0f) > 0.0f)
        {
            m_RigidBody.constraints = m_RigidBody.constraints | RigidbodyConstraints.FreezeRotationX;
        }
        if (m_ResetParams.GetWithDefault("rigid_body.freeze_rotation.y", 0.0f) > 0.0f)
        {
            m_RigidBody.constraints = m_RigidBody.constraints | RigidbodyConstraints.FreezeRotationY;
        }
        if (m_ResetParams.GetWithDefault("rigid_body.freeze_rotation.z", 0.0f) > 0.0f)
        {
            m_RigidBody.constraints = m_RigidBody.constraints | RigidbodyConstraints.FreezeRotationZ;
        }

        // cloud shadow
        m_Light.GetComponent<EntroPi.CloudShadows>().enabled = m_ResetParams.GetWithDefault("cloud_shadow.enable", 0.0f) > 0.0f;
        m_Light.GetComponent<EntroPi.CloudShadows>().SpeedMultiplier = m_ResetParams.GetWithDefault("cloud_shadow.speed_multiplier", 5.0f);
        m_Light.GetComponent<EntroPi.CloudShadows>().CoverageModifier = m_ResetParams.GetWithDefault("cloud_shadow.coverage_modifier", 0.0f);

        // lighting
        m_Light.transform.position = new Vector3(0.0f, 3.0f, 0.0f);
        m_Light.transform.rotation = Quaternion.Euler(21.6f, -261.4f, 0.0f);
        m_rotationalLightEnable = m_ResetParams.GetWithDefault("rotational_light.enable", 0.0f) > 0.0f;
        m_rotationalLightInterval = m_ResetParams.GetWithDefault("rotational_light.interval", 10.0f);
        m_rotationalLightStep = m_ResetParams.GetWithDefault("rotational_light.step", 0.1f);
        m_rotationalLightBound.x = m_Light.transform.rotation.eulerAngles.x - m_rotationalLightInterval;
        m_rotationalLightBound.y = m_Light.transform.rotation.eulerAngles.x + m_rotationalLightInterval;

        // landing zone
        m_LandingZoneEnable = m_ResetParams.GetWithDefault("landing_zone.enable", 0.0f) > 0.0f;
        m_LandingZone.SetActive(m_LandingZoneEnable);
        if (m_LandingZoneEnable)
        {
            m_LandingZoneOffset = new Vector3(m_ResetParams.GetWithDefault("landing_zone.offset.x", 31.5f),
                                              m_ResetParams.GetWithDefault("landing_zone.offset.y", -47.4f),
                                              m_ResetParams.GetWithDefault("landing_zone.offset.z", 23.5f));
            Vector3 l_position = m_LandingZoneOffset + transform.position;
            Vector3 lo_position = m_LandingZone.transform.position;
            lo_position = l_position;
            m_LandingZone.GetComponent<LandinigZone>().ResetPose();
        }
    }
}
