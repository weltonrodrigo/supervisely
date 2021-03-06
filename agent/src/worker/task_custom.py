# coding: utf-8

import json
import supervisely_lib as sly
import os

from supervisely_lib.task.paths import TaskPaths

from worker.task_dockerized import TaskDockerized, TaskStep


class TaskCustom(TaskDockerized):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.action_map = {}
        self.docker_runtime = 'nvidia'

        self.dir_data = os.path.join(self.dir_task, os.path.basename(TaskPaths.DATA_DIR))
        self.dir_results = os.path.join(self.dir_task, os.path.basename(TaskPaths.RESULTS_DIR))
        self.dir_model = os.path.join(self.dir_task, os.path.basename(TaskPaths.MODEL_DIR))
        self.config_path1 = os.path.join(self.dir_task, os.path.basename(TaskPaths.SETTINGS_PATH))
        self.config_path2 = os.path.join(self.dir_task, os.path.basename(TaskPaths.TASK_CONFIG_PATH))

    def init_additional(self):
        super().init_additional()
        sly.fs.mkdir(self.dir_data)
        sly.fs.mkdir(self.dir_results)

    def download_step(self):
        for model_info in self.info['models']:
            self.data_mgr.download_nn(model_info['title'], model_info['id'], model_info['hash'], self.dir_model)

        self.logger.info("DOWNLOAD_DATA")
        json.dump(self.info['config'], open(self.config_path1, 'w'))  # Deprecated 'task_settings.json'
        json.dump(self.info['config'], open(self.config_path2, 'w'))  # New style task_config.json

        for pr_info in self.info['projects']:
            project = sly.api_proto.Project(id=pr_info['id'], title=pr_info['title'])
            datasets = [sly.api_proto.Dataset(id=ds['id'], title=ds['title']) for ds in pr_info['datasets']]
            self.data_mgr.download_project(self.dir_data, project, datasets)

        self.report_step_done(TaskStep.DOWNLOAD)

    def before_main_step(self):
        sly.fs.clean_dir(self.dir_results)

    def upload_step(self):
        pass
