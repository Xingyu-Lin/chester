import wandb


def group_runs_with_legend(project_name, group_name, custom_legend, group_key='custom_key_1'):
    """
    Example:
    def custom_legend(config):
        return f"Env name: {config['env_name']}, seed: {config['seed']}"
    group_runs('DiffSkill', '1225_liftspread_train_full', custom_legend)

    :param project_name:
    :param group_name: Group of the experiments
    :param custom_legend: A function that takes in config and return the legend
    :param group_key: Key that will show up in the wandb terminal
    :return:
    """

    api = wandb.Api()
    runs = api.runs(path=project_name,  # Project name
                    filters={"config.wandb_group": group_name})
    for run in runs:
        run.config[group_key] = custom_legend(run.config)
        print(f"Set exp {run.config['exp_name']}, key: {group_key}, val:{run.config[group_key]}")
        run.update()
