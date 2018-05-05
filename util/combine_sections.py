import os
import pathlib


def main():
    section_directory = pathlib.Path(__file__).resolve().parents[1]
    output_directory = os.path.join(section_directory, 'output')

    filenames = sorted(
        [filename for filename in os.listdir(section_directory)
         if filename.startswith(('1.0', '2.0', '4.0'))])
    out_file = os.path.join(output_directory, 'rational_governance.mdown')
    num_files = len(filenames)
    cur_file_num = 0
    with open(out_file, 'w') as fout:
        for filename in filenames:
            if filename.startswith((('1.0', '2.0', '4.0'))):
                with open(filename, 'r') as fin:
                    cur_file_num += 1
                    for line in fin:
                        fout.write(line)
                    print('{0} {1}'.format(num_files, cur_file_num))
                    if cur_file_num < num_files:
                        fout.write('-------------------------------')
                        fout.write('\n\n  \n\n')


if __name__ == '__main__':
    main()
