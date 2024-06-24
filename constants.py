ADULT_KEY = 'adult'
EMPLOYEE_KEY = 'employee'
CHILD_KEY = 'child'
ELDER_KEY = 'elder'
LIM_MOB_KEY = 'limited_mobility'
ENV_KNOW_KEY = 'environment_knowledge'
PHYS_CAP_KEY = 'physical_capacity'
MEMORY_KEY = 'memory'

WALL_KEY = 'W'
SIGN_KEY = 'S'
EXIT_KEY = 'E'
WIDTH_KEY = 'width'
HEIGHT_KEY = 'height'
STEP_KEY = 'step'
CUSTOM_RECORD_KEY = 'custom_record'
IS_SAFE_KEY = 'is_safe'

AGENTS_CLASS_CHARACTERISTICS_MAPPING = {
    ADULT_KEY: {
        PHYS_CAP_KEY: 1,
        ENV_KNOW_KEY: 10,
        MEMORY_KEY: 20
    },
    EMPLOYEE_KEY: {
        PHYS_CAP_KEY: 1,
        ENV_KNOW_KEY: 10,
        MEMORY_KEY: 20
    },
    CHILD_KEY: {
        PHYS_CAP_KEY: 0.5,
        ENV_KNOW_KEY: 6,
        MEMORY_KEY: 15
    },
    ELDER_KEY: {
        PHYS_CAP_KEY: 0.5,
        ENV_KNOW_KEY: 8,
        MEMORY_KEY: 10
    },
    LIM_MOB_KEY: {
        PHYS_CAP_KEY: 0.35,
        ENV_KNOW_KEY: 6,
        MEMORY_KEY: 15
    }
}

EMERGENCY_EXIT_SIGN_VISIBLITY_RADIUS = 2
EMERGENCY_EXIT_VISIBLITY_RADIUS = 1
