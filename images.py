import matplotlib.pyplot as plt
import pandas as pd

import constants as consts

figure_name = "safe_people.png"

def generate_saved_agents_plot(df, folder_path, parameters):
    plt.figure(figsize=(15, 5))
    positions = df["step"]
    bar_width = 0.5

    # Create the bars
    plt.bar(positions, df[consts.ADULT_KEY], bar_width, label=consts.ADULT_KEY)
    plt.bar(positions, df[consts.CHILD_KEY], bar_width, bottom=df[consts.ADULT_KEY], label=consts.CHILD_KEY)
    plt.bar(positions, df[consts.LIM_MOB_KEY], bar_width, bottom=df[consts.ADULT_KEY] + df[consts.CHILD_KEY], label=consts.LIM_MOB_KEY)
    plt.bar(positions, df[consts.ELDER_KEY], bar_width, bottom=df[consts.ADULT_KEY] + df[consts.CHILD_KEY] + df[consts.LIM_MOB_KEY], label=consts.ELDER_KEY)
    plt.bar(positions, df[consts.EMPLOYEE_KEY], bar_width, bottom=df[consts.ADULT_KEY] + df[consts.CHILD_KEY] + df[consts.LIM_MOB_KEY] + df[consts.ELDER_KEY], label=consts.EMPLOYEE_KEY)

    # Add labels, title, and legend
    # TODO: Get parameters to plot the title
    # Alguns que preciso pegar:
    # Quantidade total de agentes
    # Porcentagem de agentes
    # Quantidade de saidas de emergência
    # Quantidade de avisos
    # Porcentagem de obstáculos
    # Estratégia

    plt.xlabel('Steps')
    plt.ylabel('Safe people')
    plt.title('Simulation for building evacuation \n Strategy: Employees with Follow Me \n Environment: 4 exits, 4 signs')
    plt.legend()

    # Show the plot
    plt.savefig(f"{folder_path}/{figure_name}")

