# -*- coding: UTF-8 -*-
"""
脚本主要生成逻辑

Authors: logic4nil(logic4nil@gmail.com)
Date:    2024/05/20 15:22:39
"""

class CodeGenerator(object):
    def __init__(self, envs={}, functions={}, tasks=[]):
        self._envs = envs
        self._functions = functions
        self._tasks = tasks

    def _generate_envs_shell_script(self):
        env_script_lines = []
        for key, value in self._envs.items():
            env_script_lines.append(f"""
  if [ "${{{key}}}x" = "x" ]; then
      export {key}={value}
  fi
""")
        str_env_script = "".join(env_script_lines)

        return f"""
function env_init() {{
    {str_env_script}
}} \n"""

    def _generate_func_shell_script(self):
        script_lines = []
        for function_name, function_body in self._functions.items():
            script_lines.append(f"{function_name}() {{\n{function_body}\n}}\n")
        script_lines.append("\n")

        return script_lines

    def _generate_task_shell_script(self):
        script_lines = []
        # Add task functions
        for task in self._tasks:
            retries = task.get('retries', 1)
            notify = task.get('notify', [])
            debug = task.get('debug', False)
            errexit = task.get('errexit', False)
            log = task.get('log', None)

            beforeExtraInfo = []
            afterExtraInfo = []
            if debug:
                beforeExtraInfo.append("set -x")
                afterExtraInfo.append("set +x")
            if errexit:
                beforeExtraInfo.append("set -e")
                afterExtraInfo.append("set +e")
            if log is not None:
                beforeExtraInfo.append(f"exec 3>&1 && exec 1>> {log} && exec 2>&1")
                afterExtraInfo.append("exec 1>&3 && exec 2>&1")


            task_script = f"""
{task['name']}() {{
    {" && ".join(beforeExtraInfo)}
    {task['script']}
    result=$?
    {" && ".join(afterExtraInfo)}
    return $result
}}\n"""
            script_lines.append(task_script)

        # Create wrapper functions with retry and notification logic
        for task in self._tasks:
            notify_cmd = " ".join([f'send_notification "{email}" "Task {task["name"]} failed" "Task {task["name"]} failed after {retries} attempts."' for email in notify])
            script_lines.append(f"""
{task['name']}_wrapper() {{
  echo "Starting task: {task['name']}"
  retry {task.get('retries', 1)} {task['name']}
  result=$?
  if [ $result -ne 0 ]; then
    {notify_cmd}
    echo "Finished task: {task['name']}, Error"
    exit 1
  else
    echo "Finished task: {task['name']}"
  fi
  return $result
}} \n""")

        return script_lines

    def _generate_call_shell_script(self):
        script_lines = []
        # depends
        task_depends_on = {}
        task_depends_by = {}
        for task in self._tasks:
            dependencies = task.get('depends_on', [])
            task_depends_on[task['name']] = dependencies
            for dependency in dependencies:
                if dependency not in task_depends_on:
                    task_depends_on[dependency] = []

                if dependency not in task_depends_by:
                    task_depends_by[dependency] = []
                task_depends_by[dependency].append(task['name'])

        while len(task_depends_on) > 0:
            for task_name in list(task_depends_on.keys()):
                dependencies = task_depends_on[task_name]
                if len(dependencies) == 0:
                    script_lines.append(f"{task_name}_wrapper || exit 1\n")

                    del task_depends_on[task_name]

                    if task_name in task_depends_by:
                        for depend_by in task_depends_by[task_name]:
                            task_depends_on[depend_by].remove(task_name)

        # Add wait for all background jobs to finish
        script_lines.append("wait\n")

        return script_lines

    def _generate_shell_script(self):
        script_lines = ["#!/bin/bash\n",]

        env_script_line = self._generate_envs_shell_script()
        script_lines.append(env_script_line)

        func_script_lines = self._generate_func_shell_script()
        script_lines.extend(func_script_lines)

        task_script_lines = self._generate_task_shell_script()
        script_lines.extend(task_script_lines)

        # add init call
        script_lines.append("init\n")
        script_lines.extend(self._generate_call_shell_script())

        return ''.join(script_lines)

    def write(self, output="/dev/stdout"):
        script_lines = self._generate_shell_script()
        with open(output, "w") as fd:
            fd.write(''.join(script_lines))




