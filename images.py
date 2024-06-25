import matplotlib.pyplot as plt

import constants as consts

figure_name = "safe_people.png"

STRATEGY_TRANSLATION_MAPPING = {
    consts.EVERY_MAN_FOR_HIMSELF_KEY: "Cada um por si",
    consts.COMMUNICATION_KEY: "Comunicação",
    consts.EVACUATION_PLAN_KEY: "Placo de evacuação"
}

def generate_saved_agents_plot(df, folder_path, parameters):
    plt.figure(figsize=(15, 5))
    positions = df["step"]
    bar_width = 0.5

    # Create the bars
    plt.bar(positions, df[consts.ADULT_KEY], bar_width, label=f"Adulto ({parameters['adults_percentage']})")
    plt.bar(positions, df[consts.CHILD_KEY], bar_width, bottom=df[consts.ADULT_KEY], label=f"Criança ({parameters['child_percentage']})")
    plt.bar(positions, df[consts.LIM_MOB_KEY], bar_width, bottom=df[consts.ADULT_KEY] + df[consts.CHILD_KEY], label=f"Dificuldade locomoção ({parameters['limited_mobility_percentage']})")
    plt.bar(positions, df[consts.ELDER_KEY], bar_width, bottom=df[consts.ADULT_KEY] + df[consts.CHILD_KEY] + df[consts.LIM_MOB_KEY], label=f"Idoso ({parameters['elder_percentage']})")
    plt.bar(positions, df[consts.EMPLOYEE_KEY], bar_width, bottom=df[consts.ADULT_KEY] + df[consts.CHILD_KEY] + df[consts.LIM_MOB_KEY] + df[consts.ELDER_KEY], label=f"Funcionário ({parameters['employee_percentage']})")

    plt.axhline(y=parameters['n_agents'], color='black', linestyle='--', linewidth=2, label="Numero de agentes")

    plt.xlabel('Passos de simulação')
    plt.ylabel('Pessoas salvas')
    plt.title(f"Simulação de evacuação de prédio \n Estratégia: {STRATEGY_TRANSLATION_MAPPING[parameters['strategy']]} \n Ambiente: {parameters['n_of_emergency_exits']} saídas, {parameters['n_of_emergency_exit_signs']} placas, {parameters['random_obstacles_percentage']} % obstáculos")
    plt.legend()

    # Show the plot
    plt.savefig(f"{folder_path}/{figure_name}")

