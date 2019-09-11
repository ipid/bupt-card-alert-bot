"""
更新所有目录下的 __init__ 文件，令其内容为“从当前目录所有模块中 import *”
"""

from pathlib import Path
from typing import List


def write_init(file: Path, module_names: List[str]):
    with file.open('w', encoding='utf-8') as f:
        for name in module_names:
            f.write(f'from .{name} import *\n')


path = Path('.')
if not (path / 'update_init.py').is_file():
    print('请将工作目录移动到此脚本所在目录。')

root = Path('./bupt_card_alert_bot/')
all_modules = [x for x in root.iterdir() if x.is_dir() and not x.name.startswith('_')]

for module in all_modules:
    print(f'Processing {module.stem}')

    pyfiles = set(x for x in module.glob('*.py') if x.name != '__init__.py')
    assert all(x.suffix == '.py' for x in pyfiles)

    write_init(module / '__init__.py', [x.stem for x in pyfiles])

write_init(root / '__init__.py', [x.stem for x in all_modules])
