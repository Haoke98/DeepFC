# 这是一个示例 Python 脚本。

# 按 ⌃R 执行或将其替换为您的代码。
# 按 双击 ⇧ 在所有地方搜索类、文件、工具窗口、操作和设置。


import os
import subprocess

import click


def arrow_choice(choices):
    prompt = 'Use arrow keys to choose, Enter to select:'
    options = [click.style(f' {choice} ', fg='white', bg='blue') for choice in choices]
    selected_index = 0

    while True:
        choices_str = ' '.join(options)
        click.clear()
        click.echo(f'{prompt} {choices_str}')

        key = click.getchar()
        if key == '\r':
            return choices[selected_index]
        elif key == click.Keys.UP:
            selected_index = (selected_index - 1) % len(choices)
        elif key == click.Keys.DOWN:
            selected_index = (selected_index + 1) % len(choices)


def convert_bytes(size):
    # 转换单位为可读性强的格式
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            break
        size /= 1024.0
    return f"{size:.2f} {unit}"


def find_largest_files(directory):
    file_sizes = []

    for foldername, subfolders, filenames in os.walk(directory):
        for filename in filenames:
            filepath = os.path.join(foldername, filename)
            if os.path.exists(filepath):
                file_size = os.path.getsize(filepath)
                file_sizes.append((filepath, file_size))

    file_sizes.sort(key=lambda x: x[1], reverse=True)
    while True:
        print("Top 20 largest files in the directory:")
        options = []
        for i, (filepath, size) in enumerate(file_sizes[:20], start=1):
            size_readable = convert_bytes(size)
            print(f"{i}. {filepath} - {size_readable}")
            options.append(str(i))

        choice = input("Enter your choice: ")
        click.echo(f'You chose: {choice}')
        dir_path = os.path.dirname(file_sizes[int(choice)][0])
        print(choice, dir_path)
        subprocess.Popen(['open', dir_path])


@click.command()
@click.option('-d', '--directory', required=True, type=click.Path(exists=True), help='Directory to scan.',
              prompt='Enter the directory to scan.')
def main(directory):
    # 调用函数
    find_largest_files(directory)


# 按装订区域中的绿色按钮以运行脚本。
if __name__ == '__main__':
    main()

# 访问 https://www.jetbrains.com/help/pycharm/ 获取 PyCharm 帮助
