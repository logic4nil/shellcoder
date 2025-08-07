# -*- coding: UTF-8 -*-
"""
本文件提供了命令行工具的入口逻辑。

Authors: logic4nil(logic4nil@gmail.com)
Date:    2024/05/20 15:22:39
"""
import os
import sys

import argparse

from shellcoder.config import ConfigLoader
from shellcoder.generate import CodeGenerator

def main(args=None):
    """主程序入口"""

    module_name = os.path.splitext(os.path.basename(os.path.dirname(sys.modules['__main__'].__file__)))[0]

    parser = argparse.ArgumentParser(description='Generate shell script from YAML config.', prog=module_name)
    parser.add_argument('--bg', action="store_true", default=False, help='If task exec in the backgroud')
    parser.add_argument('yaml_files', nargs='+', type=str, help='Paths to the YAML config files')
    parser.add_argument('output_file', type=str, help='Path to the output shell script file')

    args = parser.parse_args()

    loader = ConfigLoader()

    loader.load(args.yaml_files)

    generator = CodeGenerator(loader.envs(), loader.functions(), loader.tasks(), args.bg)


    generator.write(args.output_file)

    print(f"Shell script generated at {args.output_file}")


if __name__ == "__main__":
    main()
