import sys
import os
import argparse
from pathlib import Path
import json
import uuid
import re
import time
import numpy as np
from shutil import copyfile

class VQAQues():
    def __init__(self, js=None):
        if js != None:
            self.question = js
        else:
            self.question = {'image_id': None,
                             'question': '',
                             'question_id': None}
        return

    def from_vizwiz(self, vizwiz):
        # [Issue]
        # - question_id - use image_id*1000 + question_n
        #                 since only 1 question per image
        image_id = int(re.findall(r'\d+', vizwiz.data['image'])[0])
        question = vizwiz.data['question']
        question_id = int(image_id * 1000 + 0)

        self.update('image_id', image_id)
        self.update('question', question)
        self.update('question_id', question_id)
        return

    def update(self, key, value):
        self.question.update({key: value})

    def get(self):
        return self.question


class VQAAnno():
    def __init__(self, js=None):
        if js != None:
            self.annotation = js
        else:
            self.annotation = {'question_type': '',
                               'multiple_choice_answer': '',
                               'answers': [],
                               'image_id': None,
                               'answer_type': '',
                               'question_id': None}
        return

    def add_answer(self, answer, answer_confidence, answer_id):
        answer = {'answer': answer,
                  'answer_confidence': answer_confidence,
                  'answer_id': answer_id}
        self.annotation['answers'] += [answer]

    def from_vizwiz(self, vizwiz):
        # [Issue]
        # + answerable? - add
        # - question type - leave blank
        # - multiple_choice_answer - leave blank

        answers = vizwiz.data['answers']
        image_id = int(re.findall(r'\d+', vizwiz.data['image'])[0])
        answer_type = vizwiz.data['answer_type']
        answerable = vizwiz.data['answerable']

        for i, ans in enumerate(answers):
            self.add_answer(ans['answer'], ans['answer_confidence'], i)
        self.update('image_id', image_id)
        self.update('answer_type', answer_type)
        self.update('answerable', answerable)
        return

    def update(self, key, value):
        self.annotation.update({key: value})

    def get(self):
        return self.annotation


class VizWiz():
    def __init__(self, js=None):
        if js != None:
            self.data = js
        else:
            self.data = {'image': '',
                         'question': '',
                         'answers': [],
                         'answer_type': '',
                         'answerable': ''}
        return

    def add_answer(self, answer, answer_confidence):
        answer = {'answer': answer,
                  'answer_confidence': answer_confidence}
        self.data['answers'] += [answer]

    def from_vqa(self, vqa_q, vqa_a, _img_id_dict, split):
        vqa_img_id = vqa_q['image_id']
        vqa_question_id = vqa_q['question_id']
        vqa_question = vqa_q['question']
        if vqa_img_id in _img_id_dict.keys():
            _img_id_dict[vqa_img_id] += 1
        else:
            _img_id_dict[vqa_img_id] = 0

        vizwiz_img_id = int(vqa_img_id*100 + _img_id_dict[vqa_img_id])
        # vizwiz_question_id = int(vizwiz_img_id * 1000 + vqa_question_id % 1000)
        # need to save the dict
        vizwiz_img_name = "VizWiz_"+split+"_%012d" % vizwiz_img_id + ".jpg"

        vqa_answers = vqa_a['answers']
        vqa_answer_type = vqa_a['answer_type']
        for ans in vqa_answers:
            self.add_answer(ans['answer'], ans['answer_confidence'])

        self.update('image', vizwiz_img_name)
        self.update('question', vqa_question)
        self.update('answer_type', vqa_answer_type)
        self.update('answerable', int(True))
        return

    def update(self, key, value):
        self.data.update({key: value})

    def get(self):
        return self.data


def vizwiz2vqa(path, output_dir):
    with open(path, 'r') as f:
        rawdata = f.readlines()
    # load vizwiz
    data = json.loads(' '.join(rawdata))
    annotation = {'info': time.asctime(time.localtime(time.time())),
                  'annotations': [],
                  'data_type': 'vizwiz_vqa'}
    question = {'info': time.asctime(time.localtime(time.time())),
                'questions': [],
                'data_type': 'vizwiz_vqa'}
    for d in data:
        vw = VizWiz(d)

        vqa_a = VQAAnno()
        vqa_a.from_vizwiz(vw)
        annotation['annotations'] += [vqa_a.get()]
        vqa_q = VQAQues()
        vqa_q.from_vizwiz(vw)
        question['questions'] += [vqa_q.get()]

    # save
    if not os.path.exists(output_dir):
        output_dir.mkdir()
    annotation_string = json.dumps(annotation)
    question_string = json.dumps(question)

    with open(str(output_dir/'conveted_vqa_annotations.json'), 'w') as f:
        f.write(annotation_string)

    with open(str(output_dir/'conveted_vqa_questions.json'), 'w') as f:
        f.write(question_string)

    return


def vqa2vizwiz(vqa_a_source, vqa_q_source, vqa_i_source, output_dir, split):
    with open(vqa_a_source, 'r') as f:
        rawdata = f.readlines()
    # load vqav2
    vqa_a = json.loads(rawdata[0])
    _image_id_dict = {}
    data = []
    with open(vqa_q_source, 'r') as f:
        rawdata = f.readlines()
    vqa_q = json.loads(rawdata[0])

    for idx, q in enumerate(vqa_q['questions']):
        a = vqa_a['annotations'][idx]
        vizwiz = VizWiz()
        vizwiz.from_vqa(q, a, _image_id_dict, split)
        data += [vizwiz.get()]

    data_string = json.dumps(data)
    with open(str(output_dir/'converted_vizwiz_' + split + '.json'), 'w') as f:
        f.write(data_string)


    print('Duplicating images...')
    if not os.path.exists(output_dir/"converted_vizwiz_images"):
        (output_dir/"converted_vizwiz_images").mkdir()

    image_name_list = os.listdir(vqa_i_source)
    if len(image_name_list) == 0:
        print("Error: Empty image directory")

    for name in image_name_list:
        vqa_img_id = int(re.findall(r'_\d+', name)[0][1:])
        N = _image_id_dict[vqa_img_id]
        for i in range(N):
            vizwiz_img_id = int(vqa_img_id*100 + i)
            new_img_name = "VizWiz_"+split+"_%012d" % vizwiz_img_id + ".jpg"
            copyfile(vqa_i_source / name, output_dir/"converted_vizwiz_images"/new_img_name)
    return


def main(args):
    if args.mode == 'vqa2vizwiz':
        vqa_q_source = Path(args.vqa_question_source)
        vqa_a_source = Path(args.vqa_annotation_source)
        vqa_i_source = Path(args.vqa_image_source)
        vizwiz_output_dir = Path(args.output_dir)

        if args.split is None:
            print('Missing split: train/test/val')
        vqa2vizwiz(vqa_a_source, vqa_q_source,
                   vizwiz_output_dir, vqa_i_source, args.split)
    elif args.mode == 'vizwiz2vqa':
        source_dir = Path(args.source)
        output_dir = Path(args.output_dir)
        vizwiz2vqa(source_dir, output_dir)
    else:
        print("Error: Unknown mode")
    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", default=None, type=str,
                        help="Mode: vqa2vizwiz or vizwiz2vqa")
    # args = parser.parse_args()
    parser.add_argument("--vqa_question_source", default=None,
                        help="Path to vqa source question data file")
    parser.add_argument("--vqa_annotation_source", default=None,
                        help="Path to vqa source annotation file")
    parser.add_argument("--vqa_image_source", default=None,
                        help='Path to vqa image folder')
    parser.add_argument("--split", default=None, type=str,
                        required=False, help="train or val or test")
    parser.add_argument("--source", required=False,
                        default=None, help="Path to VizWiz source data file")
    parser.add_argument("--output_dir", default=None,
                        required=False, help="Path of output vqa question folder")
    args = parser.parse_args()
    main(args)
