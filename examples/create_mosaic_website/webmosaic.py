from pathlib import Path

import typer as tp


def create_mosaic(base_folder: Path, output_folder: str):
    import subprocess
    subprocess.run(f'ffmpeg -i {base_folder}/easytest/gt/{base_folder.name}_00.mp4 -i {base_folder}/easytest/image/{base_folder.name}_02.mp4 -i {base_folder}/easytest/gt/{base_folder.name}_01.mp4 -i {base_folder}/easytest/image/{base_folder.name}_00.mp4 -i {base_folder}/easytest/gt/{base_folder.name}_02.mp4 -i {base_folder}/easytest/image/{base_folder.name}_01.mp4 -filter_complex "[0:v][1:v]hstack=inputs=2[top];[2:v][3:v]hstack=inputs=2[middle];[4:v][5:v]hstack=inputs=2[bottom];[top][middle][bottom]vstack=inputs=3[v]" -map "[v]" {output_folder}', shell=True)

if __name__=="__main__":
    tp.run(create_mosaic)