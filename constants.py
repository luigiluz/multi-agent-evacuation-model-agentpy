ADULT_KEY = 'adult'
EMPLOYEE_KEY = 'employee'
CHILD_KEY = 'child'
ELDER_KEY = 'elder'
LIM_MOB_KEY = 'limited_mobility'
ENV_KNOW_KEY = 'environment_knowledge'
PHYS_CAP_KEY = 'physical_capacity'

AGENTS_CLASS_CHARACTERISTICS_MAPPING = {
    ADULT_KEY: {
        PHYS_CAP_KEY: 3,
        ENV_KNOW_KEY: 2
    },
    EMPLOYEE_KEY: {
        PHYS_CAP_KEY: 3,
        ENV_KNOW_KEY: 3
    },
    CHILD_KEY: {
        PHYS_CAP_KEY: 2,
        ENV_KNOW_KEY: 1
    },
    ELDER_KEY: {
        PHYS_CAP_KEY: 2,
        ENV_KNOW_KEY: 1
    },
    LIM_MOB_KEY: {
        PHYS_CAP_KEY: 1,
        ENV_KNOW_KEY: 1
    }
}

EMERGENCY_EXIT_SIGN_VISIBLITY_RADIUS = 2
EMERGENCY_EXIT_VISIBLITY_RADIUS = 1

PERSON_AGENT_MEMORY_SIZE = 10
