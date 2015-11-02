from __future__ import unicode_literals
import pytest
import os.path

from clearnlp.converter import SubprocessConverter


def test_command_string():
    converter = SubprocessConverter()
    assert converter.java_command == 'java'
    converter = SubprocessConverter(java_command='java8')
    assert converter.java_command == 'java8'


def test_convert_file():
    converter = SubprocessConverter()
    output = converter.convert_file(os.path.abspath('sample/wsj_0001.parse'), debug=True)
    assert output
    assert output.split('\n')[0] == '1\tPierre\tpierre\tNNP\t_\t2\tcompound\t_\t_\t_'


def test_convert_trees():
    converter = SubprocessConverter()
    trees = [
'''(TOP (S (NP-SBJ (NP (NNP Pierre)
                    (NNP Vinken))
                (, ,)
                (ADJP (NML (CD 61)
                           (NNS years))
                      (JJ old))
                (, ,))
        (VP (MD will)
            (VP (VB join)
                (NP (DT the)
                    (NN board))
                (PP-CLR (IN as)
                        (NP (DT a)
                            (JJ nonexecutive)
                            (NN director)))
                (NP-TMP (NNP Nov.)
                        (CD 29))))
        (. .)))''',
'''(TOP (S (NP-SBJ (NNP Mr.)
                (NNP Vinken))
        (VP (VBZ is)
            (NP-PRD (NP (NN chairman))
                    (PP (IN of)
                        (NP (NP (NNP Elsevier)
                                (NNP N.V.))
                            (, ,)
                            (NP (DT the)
                                (NNP Dutch)
                                (VBG publishing)
                                (NN group))))))
        (. .)))''']
    output = converter.convert_trees(trees, debug=True)
    assert len(output) == len(trees)
    assert output[0].split('\n')[0] == '1\tPierre\tpierre\tNNP\t_\t2\tcompound\t_\t_\t_'


