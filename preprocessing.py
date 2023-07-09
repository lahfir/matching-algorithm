import pandas as pd
import random


def add_project_count():
    # Step 1: Load the Portfolios.csv file
    portfolios_df = pd.read_csv("data/Portfolios.csv")

    # Step 2: Load the Developers.csv file
    developers_df = pd.read_csv("data/Developers.csv")

    # Check if the "projects" column exists, if not, create it
    if "projects" not in developers_df.columns:
        developers_df["projects"] = 0

    # Step 3: Iterate over the Developers.csv file
    for index, row in developers_df.iterrows():
        developer_id = row["developerID"]
        projects_count = 0

        # Step 3.1: Loop through the Portfolios.csv file to find the count of developerId
        for _, portfolio_row in portfolios_df.iterrows():
            if portfolio_row["developerID"] == developer_id:
                projects_count += 1

        # Step 4: Update the projects count in the corresponding projects column
        developers_df.at[index, "projects"] = projects_count

    # Save the updated Developers DataFrame back to Developers.csv file
    developers_df.to_csv("data/Developers.csv", index=False)


def allocate_projects():
    # Load the Portfolios.csv file
    portfolios_df = pd.read_csv("data/Portfolios.csv")

    # Load the Developers.csv file
    developers_df = pd.read_csv("data/Developers.csv")

    # Create a dictionary to store the allocated projects for each developer
    allocated_projects = {}

    # Sort developers by score in descending order
    developers_df = developers_df.sort_values(by="score", ascending=False)

    # Iterate over each developer in Developers.csv
    for index, developer_row in developers_df.iterrows():
        developer_id = developer_row["developerID"]
        developer_score = developer_row["score"]

        # Calculate the number of projects based on the developer's score
        if developer_score == 0:
            num_projects = 0
        elif developer_score > 7:
            num_projects = min(random.randint(5, 7), len(portfolios_df))
        elif developer_score >= 3:
            num_projects = min(random.randint(3, 5), len(portfolios_df))
        else:
            num_projects = min(random.randint(1, 3), len(portfolios_df))

        # Select projects from the Portfolios.csv file
        selected_projects = pd.DataFrame()

        while len(selected_projects) < num_projects:
            available_projects = portfolios_df[
                ~portfolios_df["Name"].isin(allocated_projects.values())
            ]
            if len(available_projects) == 0:
                break
            new_project = available_projects.sample()
            selected_projects = pd.concat([selected_projects, new_project])

        if num_projects > 0:
            # Assign the developer ID to the selected projects
            selected_projects["developerID"] = developer_id

            # Update the developer ID in the Portfolios.csv file
            portfolios_df.loc[selected_projects.index, "developerID"] = developer_id

            # Store the allocated projects in the dictionary
            allocated_projects.update(
                selected_projects.set_index("developerID")["Name"].to_dict()
            )

    # Save the updated Portfolios DataFrame back to Portfolios.csv
    portfolios_df.to_csv("data/Portfolios.csv", index=False)


add_project_count()
# allocate_projects()
