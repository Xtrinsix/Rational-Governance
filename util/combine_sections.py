import os
import pathlib


def main():
    section_directory = pathlib.Path(__file__).resolve().parents[1]
    output_directory = os.path.join(section_directory, 'output')

    filenames = sorted(os.listdir(section_directory))
    for filename in filenames:
        if filename.startswith((('1.0', '2.0', '4.0'))):
            print(filename)


if __name__ == '__main__':
    main()
