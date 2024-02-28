#!/usr/bin/python
# -*- coding: UTF-8 -*-

import random
import string
import time
from datetime import datetime
from as_constants import *
from loggers import logger
from process_generate import processinput, infer_server, postprocess


class WebResponseJson():
    '''
    the restful api response of yuan web server
    '''

    def __init__(self):
        self.basic = {"flag": True,  # 是否成功？True、False
                      "errCode": "0",
                      "errMessage": "success",  # 如果错误，此次应返回错误日志
                      "exceptionMsg": "",  # 如果错误，此次应返回错误日志
                      "resData": {}}

    def success(self, ques_id='0', message="success"):
        self.basic = {"flag": True,  # 是否成功？True、False
                      "errCode": "0",
                      "errMessage": message,  # 如果错误，此次应返回错误日志
                      "exceptionMsg": "",  # 如果错误，此次应返回错误日志
                      "resData": {"ques_id": ques_id}}
        return self.basic

    def fail(self, err_message, result, err_code=AS_CHECK_INFER_CODE):
        self.basic = {"flag": False,  # 是否成功？True、False
                      "errCode": err_code,
                      "errMessage": err_message,  # 如果错误，此次应返回错误日志
                      "exceptionMsg": err_message,  # 如果错误，此次应返回错误日志
                      "resData": result}
        logger.info('\n fail exception:  {0}'.format(str(self.basic)))
        return self.basic


    # Yuan2.0 模型测试
    def modelsYuanInfer(self, paras_dict):

        result = {"model_gene":[""], "model_input":[""]}
        self.success()
        # 以时间作为问题id
        t = list(time.localtime(time.time()))
        s_t = [str(i) for i in t]
        ques_id = "-".join(s_t[:6]) + "-" + ''.join(random.sample(string.ascii_letters + string.digits, 8))
        result["ques_id"] = ques_id
        paras_dict["ques_id"] = ques_id

        # -----------------推理过程---------------------
        startTime = datetime.now()
        # os.makedirs(LOG_GENE_ALL, exist_ok=True)

        # 第一步：处理UI传入文本，包括组成prompt
        flag, data = processinput(paras_dict)
        if flag == False:
            return self.fail(data, result)
        Time1 = datetime.now()
        howLong = Time1 - startTime
        print(howLong)
        logger.info('\n ques_id:{0}\n processtime:{1}\n input:{2}\n processinput:{3}'.format(ques_id, howLong, paras_dict['input'], data))

        # 第二步：调用模型接口进行推理，保存图像，并输出保存图像路径字典
        infer_out = infer_server(ques_id, data, paras_dict)
        if infer_out is None or infer_out == []:
            return self.fail("模型输出为空，请重试", result)
        Time2 = datetime.now()
        howLong = Time2 - Time1
        print(howLong)
        logger.info('\n ques_id:{0}\n infer_time:{1}\n model_infer_out:{2}'.format(ques_id, howLong, str(infer_out)))

        # 第三步：后处理
        match_output = postprocess(data, paras_dict, infer_out)

        result["model_input"] = [dt.replace('"', '\\"') for dt in data]  #引号加转义符
        result["model_gene"] = [iout.replace('"', '\\"') for iout in infer_out]
        # result["model_input"] = data
        # result["model_gene"] = infer_out

        result["output"] = match_output
        self.basic["resData"] = result
        Time3 = datetime.now()
        howLong = Time3 - Time2
        print(howLong)
        logger.info('\n ques_id:{0}\n postprocesstime:{1}\n postprocess output:{2}'.format(ques_id, howLong, match_output))

        return self.basic


    # 检索增强LLM
    def modelsYuanInfer_web(self, paras_dict):
        from process_generate_web import processinput,infer_server,postprocess, modify_dict

        result = {"model_gene":[""], "model_input":[""]}
        self.success()
        # 以时间作为问题id
        t = list(time.localtime(time.time()))
        s_t = [str(i) for i in t]
        ques_id = "-".join(s_t[:6]) + "-" + ''.join(random.sample(string.ascii_letters + string.digits, 8))
        result["ques_id"] = ques_id
        paras_dict["ques_id"] = ques_id

        # -----------------推理过程---------------------
        startTime = datetime.now()
        # os.makedirs(LOG_GENE_ALL, exist_ok=True)

        # 第一步：处理UI传入文本，包括组成prompt
        flag, data = processinput(paras_dict)
        if flag == False:
            return self.fail(data, result)
        Time1 = datetime.now()
        howLong = Time1 - startTime
        print(howLong)
        logger.info('\n ques_id:{0}\n processtime:{1}\n input:{2}\n processinput:{3}'.format(ques_id, howLong, paras_dict['input'], data))

        # 第二步：调用web检索，组成prompt，LLM推理
        try:
            infer_out = infer_server(ques_id, data, paras_dict)
        except Exception as e:
            return self.fail(str(e), result)

        if infer_out is None or infer_out == []:
            return self.fail("模型输出为空，请重试", result)
        Time2 = datetime.now()
        howLong = Time2 - Time1
        print(howLong)
        logger.info('\n ques_id:{0}\n infer_time:{1}\n model_infer_out:{2}'.format(ques_id, howLong, str(infer_out)))

        # 第三步：后处理
        match_output = postprocess(data, paras_dict, infer_out)

        result["model_input"] = [data]
        result["model_gene"] = [infer_out[0]]
        result["output"] = match_output
        # 修改字典所有值，所有str中"用\\"替换
        result = modify_dict(result)

        self.basic["resData"] = result
        Time3 = datetime.now()
        howLong = Time3 - Time2
        print(howLong)
        logger.info('\n ques_id:{0}\n postprocesstime:{1}\n postprocess output:{2}'.format(ques_id, howLong, result))

        return self.basic


if __name__ == '__main__':
    response = WebResponseJson()
    paras_dict = {"input":[{"question":"泰山在哪里？", "answer": ""}], 'multidialogue':True,
                  "url":[["http://172.31.4.32:8900/yuan"]], "style":100,
                  "response_length": 5000, "temperature": 0.6, "top_p": 0.95, "top_k": 0,
                  "retrieve_topk": 3,
                  "template": "说明：您是一位认真的研究者。使用提供的网络搜索结果，对给定的问题写一个全面而详细的回复。\n用语言回答：中文\n问题：",
                  "embeddings_model_path": r"D:\E\Code\NLP\yuan_checkpoints\text2vec-base-chinese",
                  "serper_api_key": "e4e726300b3804897d394c87fc50aa81357015b5"}
    res = response.modelsYuanInfer_web(paras_dict)

    pass