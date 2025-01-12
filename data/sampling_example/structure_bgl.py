# pipeline
# 1. read origin logs
# 2. extract label, time and origin event
# 3. match event to the template
# 构建自己的日志
# 此python代码主要是读取bgl2_100k文件，并把它每一行的第九个值之后的字符串和 templates 中 EventTemplate 匹配，然后提取时间，标签，还有匹配的值
# 组成一个表格BGL_100k_structured.csv, 输出文件。
import re
import pandas as pd
from tqdm import tqdm
para = {"bgl":"bgl/bgl2_100k","template":"bgl/templates.csv","structured_file":"bgl/BGL_100k_structured.csv"}
# read origin logs
# 读文件，python 中这样写
def data_read(filepath):
    fp = open(filepath, "r")
    datas = []
    lines = fp.readlines()
    i = 0
    for line in tqdm(lines):
        row = line.strip("\n").split()
        datas.append(row)
        i = i + 1
    fp.close()
    return datas

def match(BGL):
    # match event to the template
    template = pd.read_csv(para["template"])

    event = []
    event2id = {}

    for i in range(template.shape[0]):
        event_id = template.iloc[i, template.columns.get_loc("EventId")]
        event_template = template.iloc[i, template.columns.get_loc("EventTemplate")]
        event2id[event_template] = event_id
        event.append(event_template)

    error_log = []
    eventmap = []
    print("Matching...")
    for log in tqdm(BGL):
        log_event = " ".join(log[9:])
        for i,item in enumerate(event):
            if re.match(r''+item,log_event) and re.match(r''+item,log_event).span()[1] == len(log_event):
                eventmap.append(event2id[item])
                break
            if i == len(event)-1:
                eventmap.append('error')
                error_log.append(log_event)
    return eventmap
def structure(BGL,eventmap):
    # extract label, time and origin event
    label = []
    time = []
    for log in tqdm(BGL):
        label.append(log[0])
        time.append(log[4])

    BGL_structured = pd.DataFrame(columns=["label","time","event_id"])
    BGL_structured["label"] = label
    BGL_structured["time"] = time
    BGL_structured["event_id"] = eventmap
    # Remove logs which do not match the template(very few logs ......)
    # 在这里，-BGL_structured["event_id"].isin(["error"]) 表示删除 event_id 列中值为 “error” 的行
    # error 是提前 标记的 行，匹配不到模版 46行
    BGL_structured = BGL_structured[(-BGL_structured["event_id"].isin(["error"]))]
    # 在这里，index=None 表示不将行索引写入到csv文件中
    BGL_structured.to_csv(para["structured_file"],index=None)

if __name__ == "__main__":
    BGL = data_read(para["bgl"])
    eventmap = match(BGL)
    structure(BGL,eventmap)
