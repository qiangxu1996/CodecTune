# -*- coding: utf-8 -*-
"""
desciption: Knob information

"""

import utils
import configs
import collections

# 700GB
memory_size = 360*1024*1024
#
disk_size = 8*1024*1024*1024
instance_name = ''


KNOBS = [
         # ADD
         'ctu',
         'min-cu-size',
         'bframes',
         'b-adapt',
         'rc-lookahead',
         'lookahead-slices',
         'scenecut',
         'ref',
         'limit-refs',
         'me',
         'merange',
         'subme',
         'rect',
         'amp',
         'limit-modes',
         'max-merge',
         'early-skip',
         'recursion-skip',
         'fast-intra',
         'b-intra',
         'sao',
         'signhide',
         'weightp',
         'weightb',
         'aq-mode',
         'cuTree',
         'rdLevel',
         'rdoq-level',
         'tu-intra',
         'tu-inter',
         'limit-tu',
         ]

KNOB_DETAILS = None
EXTENDED_KNOBS = None
num_knobs = len(KNOBS)


def init_knobs(instance, num_more_knobs):
    #global instance_name
    #global memory_size
    #global disk_size
    global KNOB_DETAILS
    global EXTENDED_KNOBS
    # instance_name = instance
    # TODO: Test the request
    # use_request = False
    # if use_request:
    #     if instance_name.find('tencent') != -1:
    #         memory_size, disk_size = utils.get_tencent_instance_info(instance_name)
    #     else:
    #         memory_size = configs.instance_config[instance_name]['memory']
    #         #disk_size = configs.instance_config[instance_name]['disk']
    # else:
    #     memory_size = configs.instance_config[instance_name]['memory']
    #     #disk_size = configs.instance_config[instance_name]['disk']

    KNOB_DETAILS = {        
        'ctu': ['enum', [16, 64, 64]],
        'min-cu-size': ['enum', [8, 32, 8]],
        'bframes': ['integer', [0, 16, 4]],
        'b-adapt': ['integer', [0, 2, 2]],
        'rc-lookahead': ['integer', [0, 250, 20]], # Between the maximum consecutive bframe count (--bframes) and 250, default 20
        'lookahead-slices': ['integer', [0, 16, 8]],
        'scenecut': ['integer', [0, 40, 40]], # How aggressively I-frames need to be inserted, max value undetermined
        'ref': ['integer', [1, 16, 3]],
        'limit-refs': ['integer', [0, 3, 3]],
        'me': ['integer', [0, 5, 1]], # <integer|string>
                                            # 0 dia
                                            # 1 hex (default)
                                            # 2 umh
                                            # 3 star
                                            # 4 sea
                                            # 5 full

        'merange': ['integer', [0, 32768, 57]],
        'subme': ['integer', [0, 7, 2]],
        'rect': ['enum', [0, 1, 0]],
        'amp': ['enum', [0, 1, 0]], # See documentation for constraints
        'limit-modes': ['enum', [0, 1, 0]], # This can significantly improve performance when rect and/or --amp are enabled at minimal compression efficiency loss.
        'max-merge': ['integer', [1, 5, 2]],
        'early-skip': ['enum', [0, 1, 0]],
        'recursion-skip': ['integer', [0, 2, 1]], # --rskip
        'fast-intra': ['enum', [0, 1, 0]], # Only applicable for --rd levels 4 and below (medium preset and faster)
        'b-intra': ['enum', [0, 1, 0]],
        'sao': ['enum', [0, 1, 0]],
        'signhide': ['enum', [0, 1, 0]],
        'weightp': ['enum', [0, 1, 0]],
        'weightb': ['enum', [0, 1, 0]],
        'aq-mode': ['integer', [0, 4, 2]],
        'cuTree': ['enum', [0, 1, 0]],
        'rdLevel': ['integer', [0, 6, 2]],
        'rdoq-level': ['integer', [0, 2, 0]],
        'tu-intra': ['integer', [1, 4, 1]],
        'tu-inter': ['integer', [1, 4, 1]],
        'limit-tu': ['integer', [0, 4, 0]],
    }

    # TODO: ADD Knobs HERE! Format is the same as the KNOB_DETAILS
    UNKNOWN = 0
    EXTENDED_KNOBS = {
    }
    # ADD Other Knobs, NOT Random Selected
    i = 0
    EXTENDED_KNOBS = dict(sorted(EXTENDED_KNOBS.items(), key=lambda d: d[0]))
    for k, v in EXTENDED_KNOBS.items():
        if i < num_more_knobs:
            KNOB_DETAILS[k] = v
            KNOBS.append(k)
            i += 1
        else:
            break
    # print("Instance: %s Memory: %s" % (instance_name, memory_size))


def get_init_knobs():

    knobs = {}

    for name, value in KNOB_DETAILS.items():
        knob_value = value[1]
        knobs[name] = knob_value[-1]

    return knobs


def gen_continuous(action):
    knobs = {}

    for idx in xrange(len(KNOBS)):
        name = KNOBS[idx]
        value = KNOB_DETAILS[name]

        knob_type = value[0]
        knob_value = value[1]
        min_value = knob_value[0]

        if knob_type == 'integer':
            max_val = knob_value[1]
            eval_value = int(max_val * action[idx])
            eval_value = max(eval_value, min_value)
        else:
            enum_size = len(knob_value)
            enum_index = int(enum_size * action[idx])
            enum_index = min(enum_size - 1, enum_index)
            eval_value = knob_value[enum_index]

        #if name == 'innodb_log_file_size':
        #    max_val = disk_size / knobs['innodb_log_files_in_group']
        #    eval_value = int(max_val * action[idx])
        #    eval_value = max(eval_value, min_value)

        #if name == 'binlog_cache_size':
        #    if knobs['binlog_cache_size'] > knobs['max_binlog_cache_size']:
        #        max_val = knobs['max_binlog_cache_size']
        #        eval_value = int(max_val * action[idx])
        #        eval_value = max(eval_value, min_value)

        knobs[name] = eval_value

    #if 'tmp_table_size' in knobs.keys():
        # tmp_table_size
        #max_heap_table_size = knobs.get('max_heap_table_size', -1)
        #act_value = knobs['tmp_table_size']/EXTENDED_KNOBS['tmp_table_size'][1][1]
        #max_val = min(EXTENDED_KNOBS['tmp_table_size'][1][1], max_heap_table_size)\
            #if max_heap_table_size > 0 else EXTENDED_KNOBS['tmp_table_size'][1][1]
        #eval_value = int(max_val * act_value)
        #eval_value = max(eval_value, EXTENDED_KNOBS['tmp_table_size'][1][0])
        #knobs['tmp_table_size'] = eval_value

    return knobs


def save_knobs(knob, metrics, knob_file):
    """ Save Knobs and their metrics to files
    Args:
        knob: dict, knob content
        metrics: list, tps and latency
        knob_file: str, file path
    """
    # format: tps, latency, knobstr: [#knobname=value#]
    knob_strs = []
    for kv in knob.items():
        knob_strs.append('{}:{}'.format(kv[0], kv[1]))
    result_str = '{},{},{},'.format(metrics[0], metrics[1], metrics[2])
    knob_str = "#".join(knob_strs)
    result_str += knob_str

    with open(knob_file, 'a+') as f:
        f.write(result_str+'\n')

