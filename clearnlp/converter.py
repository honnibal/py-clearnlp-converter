# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# 
# Based on PyStanfordDependencies

from __future__ import print_function
from __future__ import unicode_literals
import os
import os.path
import io
import subprocess
import tempfile


PWD = os.path.abspath(os.path.dirname(__file__))


class SubprocessConverter(object):
    def __init__(self, filenames=None, java_command='java',
                 head_rule_path=None,
                 class_name='edu.emory.clir.clearnlp.bin.C2DConvert'):
        if filenames is None:
            filenames = [
                'clearnlp-3.1.2.jar', 'args4j-2.0.29.jar', 'log4j-1.2.17.jar',
                'hppc-0.6.1.jar', 'xz-1.5.jar', 'clearnlp-dictionary-3.2.jar',
                'clearnlp-global-lexica-3.1.jar'
            ]
        if head_rule_path is None:
            head_rule_path = os.path.join(PWD, 'ext', 'headrule_en_stanford.txt')

        self.class_name = class_name
        self.head_rule_path = head_rule_path
        self.java_command = java_command
        self.classpath = [os.path.join(PWD, 'ext', filename)
                          for filename in filenames]

    def convert_trees(self, trees, debug=False):
        tmp_loc = os.path.join(PWD, 'tmp.parse')
        with io.open(tmp_loc, 'wt', encoding='utf8') as file_:
            for tree in trees:
                file_.write(tree.strip())
                file_.write('\n\n')
        return self.convert_file(tmp_loc).strip().split('\n\n')

    def convert_file(self, file_loc, debug=False):
        #with TemporaryTextFile(ptb_trees) as file_:
        command = [self.java_command,
                   '-ea',
                   '-cp', ':'.join(self.classpath),
                   self.class_name,
                   '-h', self.head_rule_path,
                   '-i', file_loc]
        clear_process = subprocess.Popen(command, stdout=subprocess.PIPE,
                                          stderr=subprocess.PIPE,
                                          universal_newlines=True)
        return_code = clear_process.wait()
        stderr = clear_process.stderr.read()
        stdout = clear_process.stdout.read()

        if debug:
            print(' '.join(command))
            print("stdout: {%s}" % stdout)
            print("stderr: {%s}" % stderr)
            print('Exit code:', return_code)

        with io.open(file_loc + '.dep', 'rt', encoding='utf8') as file_:
            output = file_.read()
        return output

    @staticmethod
    def _raise_on_bad_exit_or_output(return_code, stderr):
        if 'PennTreeReader: warning:' in stderr:
            raise ValueError("Tree(s) not in valid Penn Treebank format")

        if return_code:
            if 'Unsupported major.minor version' in stderr:
                # Oracle Java error message
                raise JavaRuntimeVersionError()
            elif 'JVMCFRE003 bad major version' in stderr:
                # IBM Java error message
                raise JavaRuntimeVersionError()
            else:
                raise ValueError("Bad exit code from Stanford CoreNLP")


class TemporaryTextFile(object):
    def __enter__(self):
        input_file = tempfile.NamedTemporaryFile(delete=False)
        for ptb_tree in ptb_trees:
            self._raise_on_bad_input(ptb_tree)
            tree_with_line_break = ptb_tree + "\n"
            input_file.write(tree_with_line_break.encode("utf-8"))
        input_file.flush()
        return input_file


class JavaRuntimeVersionError(EnvironmentError):
    """Error for when the Java runtime environment is too old to support
    the specified version of Stanford CoreNLP."""
    def __init__(self):
        message = "Your Java runtime is too old (must be 1.8+ to use " \
                  "CoreNLP version 3.5.0 or later and 1.6+ to use CoreNLP " \
                  "version 1.3.1 or later)"
        super(JavaRuntimeVersionError, self).__init__(message)


