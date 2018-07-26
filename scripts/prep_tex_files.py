import os
import pathlib
import re
import sys

# mdown matches
heading_1_re = re.compile('^# (.*)')
heading_2_re = re.compile('^## (.*)')
heading_3_re = re.compile('^### (.*)')
heading_4_re = re.compile('^#### (.*)')
heading_6_re = re.compile('^###### (.*)')
unordered_list_re = re.compile('^- (.*)')
unordered_sublist_re = re.compile('^      -  (.*)')
author_list_re = re.compile('^## Author: (.*)')

# tex template matches
include_re = re.compile('^%% part ([\d])')


class MarkdownConverter(object):

    def __init__(self, source_directory, temp_directory, template_file):
        self.source_directory = source_directory
        self.temp_directory = temp_directory
        self.template_file = template_file
        self.chapters_directory = os.path.join(temp_directory, 'chapters')
        self.appx_directory = os.path.join(temp_directory, 'appendices')
        self.template_directives = {'inputs': {}}
        self.current_section = None
        self.in_subsection = False
        

    def convert_files(self):
        # filenames = sorted(
        #     [filename for filename in os.listdir(self.source_directory)
        #      if filename.startswith(('0.0', '1.0', '2.0', '3.', '4.0')) 
        #      and not filename in ['3.00.0_template.mdown']])

        filenames = sorted(
            [filename for filename in os.listdir(self.source_directory)
             if filename.startswith(('0.0', '1.0', '2.', '3.', '4.0')) 
             and filename not in ['3.00.0_template.mdown',]])

        print(filenames)
        # with open(self.template_file, 'a') as tout:
        for filename in filenames:
            self.convert_file(filename)
        
        new_template_file = os.path.join(self.temp_directory, os.path.basename(self.template_file))
        print(self.template_directives)
        with open(self.template_file, 'r') as fin:
            with open(new_template_file, 'w') as fout:
                print('Writing contents of {0} to {1}'.format(self.template_file, new_template_file))
                print('Directives: {0}'.format(self.template_directives))
                for line in fin:
                    part_include_match = include_re.match(line)
                    if line.startswith('\\newcommand'):
                        line = line.replace('DocumentTitle', self.template_directives.get('DocumentTitle'))
                        line = line.replace('DocumentSubTitle', self.template_directives.get('DocumentSubTitle'))
                        line = line.replace('Author', self.template_directives.get('Author'))
                        fout.write(line)
                        
                    elif part_include_match:
                        part = part_include_match.groups()[0]
                        for include in self.template_directives.get('inputs').get(part, []):
                            fout.write('\input{{{0}}}\n'.format(include))                            
                    else:
                        fout.write(line)

            

    def convert_file(self, filename):
        print('Converting file {0}'.format(filename))
        if filename.startswith('0.0'):
            self.convert_title_file(filename)
        # if filename.startswith('1.0') or filename.startswith('2.0'):
        else:
            part_prefix = filename[0]
            part_inputs = self.template_directives.get('inputs').setdefault(part_prefix, [])

            with open (filename, 'r') as fin:
                name, _ = os.path.splitext(os.path.basename(filename))
                out_file_name = os.path.join(
                    self.chapters_directory, '{name}.tex'.format(name=name))
                with open(out_file_name, 'w') as fout:
                    with open(filename, 'r') as fin:
                        for line in fin:
                            fout.write(self.convert_line(line))
                    fout.write(self.convert_line(None))
                
                part_inputs.append(os.path.join(os.path.basename(self.chapters_directory), out_file_name))

    def convert_title_file(self, filename):
        with open (filename, 'r') as fin:
            for line in fin:
                match_results = heading_1_re.match(line)
                if match_results:
                    self.template_directives['DocumentTitle'] = match_results.groups()[0]
                match_results = heading_6_re.match(line)
                if match_results:
                    self.template_directives['DocumentSubTitle'] = match_results.groups()[0]
                match_results = author_list_re.match(line)
                if match_results:
                    self.template_directives['Author'] = match_results.groups()[0]

    def convert_appendix_file(self, filename):
        pass

    def cleanup_section(self, section=None, subsection=None):
        # print('section: {0}, self.current_section: {1}, subsection: {2}, self.in_subsection: {3}'.format(section, self.current_section, subsection, self.in_subsection))
        cleanup = ''
        # subsection logic first
        if section and subsection and not self.in_subsection:
            self.in_subsection = True
            cleanup += '\t\\begin{{{section}}}\n'.format(section=section)
        elif section and not subsection and self.in_subsection:
            # end subsection
            self.in_subsection = False
            end_section = self.current_section
            cleanup += '\n\t\\end{{{section}}}\n\n'.format(section=end_section)
        elif self.in_subsection and not section:
            self.in_subsection = False
            end_section = self.current_section
            cleanup += '\n\t\\end{{{section}}}\n\n'.format(section=end_section)

        # section logic similar to subsection
        if self.current_section and not section:
            end_section = self.current_section
            self.current_section = None
            cleanup += '\n\\end{{{section}}}\n\n'.format(section=end_section)
        elif section and section != self.current_section:
            self.current_section = section
            cleanup += '\\begin{{{section}}}\n'.format(section=section)
        elif not section and self.current_section:
            end_section = self.current_section
            self.current_section = None
            cleanup += '\n\\end{{{section}}}\n\n'.format(section=end_section)
        
        return cleanup

    def convert_line(self, line):
        """
            Markdown heading 1 is converted to a part
            \hypertarget{doctrine}{%
            \part{Doctrine}\label{doctrine}}
        """
        if not (line):
            # end of file
            return self.cleanup_section()
        
        # replace bold/italic with \textbf{\textit{x}
        line = re.sub(r"(\*__)(.*)(__\*)", r"\\textbf{\\textit{\2}}", line)

        match_results = heading_1_re.match(line)
        # \hypertarget{introduction}{%
        # \section{1.0. Introduction}\label{introduction}}
        if match_results:            
            # print('matched {0} with {1}'.format(match_results.groups(), heading_1_re))
            title = match_results.groups()[0]
            return '{cleanup}\hypertarget{{{title}}}{{%\n\part{{{title}}}\label{{{title}}}}}\n'.format(
                cleanup=self.cleanup_section(),
                title=title)
        match_results = heading_2_re.match(line)
        if match_results:
            # print('matched {0} with {1}'.format(match_results.groups(), heading_2_re))
            title = match_results.groups()[0]
            return '{cleanup}\hypertarget{{chapter_{title}}}{{%\n\chapter{{{title}}}\label{{{title}}}}}\n'.format(
                cleanup=self.cleanup_section(),
                title=title)
        match_results = heading_3_re.match(line)
        if match_results:
            # print('matched {0} with {1}'.format(match_results.groups(), heading_2_re))
            title = match_results.groups()[0]
            return '{cleanup}\hypertarget{{section_{title}}}{{%\n\section{{{title}}}\label{{{title}}}}}\n'.format(
                cleanup=self.cleanup_section(),
                title=title)
        match_results = heading_4_re.match(line)
        if match_results:
            # print('matched {0}'.format(match_results.groups()))
            title = match_results.groups()[0]
            return '{cleanup}\hypertarget{{subsection_{title}}}{{%\n\subsection{{{title}}}\label{{{title}}}}}\n'.format(
                cleanup=self.cleanup_section(),
                title=title)
        match_results = heading_6_re.match(line)
        if match_results:
            # print('matched {0}'.format(match_results.groups()))
            title = match_results.groups()[0]
            return '{cleanup}\hypertarget{{subsubsection_{title}}}{{%\n\subsubsection{{{title}}}\label{{{title}}}}}\n'.format(
                cleanup=self.cleanup_section(),
                title=title)
            # return '{cleanup}\hypertarget{{subsubsection_{title}}}{{%\n\subsubsection{{{title}}}\label{{{title}}}}}\n'.format(
            #     cleanup=self.cleanup_section(),
            #     title=title)
        match_results = unordered_list_re.match(line)
        if match_results:
            # print('matched unordered_list: {0}'.format(line))
            return '{cleanup}\n\item {line}'.format(cleanup=self.cleanup_section(section='itemize'),line=match_results.groups()[0])
        
        match_results = unordered_sublist_re.match(line)
        if match_results:
            # print('matched unordered_sublist: {0}'.format(line))
            return '{cleanup}\n\t\item {line}'.format(cleanup=self.cleanup_section(section='itemize', subsection=True),line=match_results.groups()[0])

        return '{cleanup}{line}'.format(cleanup=self.cleanup_section(), line=line)


def main(source_directory, output_directory, template_file):

    converter = MarkdownConverter(
        source_directory, output_directory, template_file
    )

    converter.convert_files()


    
    # out_file = os.path.join(output_directory, 'rational_governance.mdown')
    # num_files = len(filenames)
    # cur_file_num = 0
    # with open(out_file, 'w') as fout:
    #     for filename in filenames:
    #         if filename.startswith((('1.0', '2.0', '4.0'))):
    #             with open(filename, 'r') as fin:
    #                 cur_file_num += 1
    #                 for line in fin:
    #                     fout.write(line)
    #                 print('{0} {1}'.format(num_files, cur_file_num))
    #                 if cur_file_num < num_files:
    #                     fout.write('-------------------------------')
    #                     fout.write('\n\n  \n\n')
    #                     fout.write('<div style="page-break-after: always;"></div>')


if __name__ == '__main__':
    print(sys.argv)
    args = sys.argv
    if len(args) < 3:
        exit(1)
    main(args[1], args[2], args[3])
