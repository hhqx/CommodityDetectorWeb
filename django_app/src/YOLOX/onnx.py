### 1. 读取图片并预处理
#导包
import cv2
import os
import numpy as np
#预处理
def preproc(img, input_size, swap=(2, 0, 1)):
    if len(img.shape) == 3:
        padded_img = np.ones((input_size[0], input_size[1], 3), dtype=np.uint8) * 114
    else:
        padded_img = np.ones(input_size, dtype=np.uint8) * 114

    r = min(input_size[0] / img.shape[0], input_size[1] / img.shape[1])
    resized_img = cv2.resize(
        img,
        (int(img.shape[1] * r), int(img.shape[0] * r)),
        interpolation=cv2.INTER_LINEAR,
    ).astype(np.uint8)
    padded_img[: int(img.shape[0] * r), : int(img.shape[1] * r)] = resized_img

    padded_img = padded_img.transpose(swap)
    padded_img = np.ascontiguousarray(padded_img, dtype=np.float32)
    return padded_img, r
#图片path
# image_path = os.path.join('./')
image_path = 'a.jpg'
origin_img = cv2.imread(image_path)
#input_shape 跟pytorch转onnx时候设置的shape一致
img, ratio = preproc(origin_img, (640,640))
### 2.加载onnx并前向一次
#导包
import onnxruntime

model = os.path.join('./yolox_s.onnx')#onnx模型陆军
session = onnxruntime.InferenceSession(model)

ort_inputs = {session.get_inputs()[0].name: img[None, :, :, :]}
output = session.run(None, ort_inputs)

### 3.输出结果后处理-解码
def demo_postprocess(outputs, img_size, p6=False):
    grids = []
    expanded_strides = []

    if not p6:
        strides = [8, 16, 32]
    else:
        strides = [8, 16, 32, 64]

    hsizes = [img_size[0] // stride for stride in strides]
    wsizes = [img_size[1] // stride for stride in strides]

    for hsize, wsize, stride in zip(hsizes, wsizes, strides):
        xv, yv = np.meshgrid(np.arange(wsize), np.arange(hsize))
        grid = np.stack((xv, yv), 2).reshape(1, -1, 2)
        grids.append(grid)
        shape = grid.shape[:2]
        expanded_strides.append(np.full((*shape, 1), stride))

    grids = np.concatenate(grids, 1)
    expanded_strides = np.concatenate(expanded_strides, 1)
    outputs[..., :2] = (outputs[..., :2] + grids) * expanded_strides
    outputs[..., 2:4] = np.exp(outputs[..., 2:4]) * expanded_strides

    return outputs


predictions = demo_postprocess(output[0], (640,640), False)[0]
boxes = predictions[:, :4]
scores = predictions[:, 4:5] * predictions[:, 5:]

boxes_xyxy = np.ones_like(boxes)
boxes_xyxy[:, 0] = boxes[:, 0] - boxes[:, 2]/2.
boxes_xyxy[:, 1] = boxes[:, 1] - boxes[:, 3]/2.
boxes_xyxy[:, 2] = boxes[:, 0] + boxes[:, 2]/2.
boxes_xyxy[:, 3] = boxes[:, 1] + boxes[:, 3]/2.
boxes_xyxy /= ratio

### 4.预测框 nms -- 画出结果
def nms(boxes, scores, nms_thr):
    """Single class NMS implemented in Numpy."""
    x1 = boxes[:, 0]
    y1 = boxes[:, 1]
    x2 = boxes[:, 2]
    y2 = boxes[:, 3]

    areas = (x2 - x1 + 1) * (y2 - y1 + 1)
    order = scores.argsort()[::-1]

    keep = []
    while order.size > 0:
        i = order[0]
        keep.append(i)
        xx1 = np.maximum(x1[i], x1[order[1:]])
        yy1 = np.maximum(y1[i], y1[order[1:]])
        xx2 = np.minimum(x2[i], x2[order[1:]])
        yy2 = np.minimum(y2[i], y2[order[1:]])

        w = np.maximum(0.0, xx2 - xx1 + 1)
        h = np.maximum(0.0, yy2 - yy1 + 1)
        inter = w * h
        ovr = inter / (areas[i] + areas[order[1:]] - inter)

        inds = np.where(ovr <= nms_thr)[0]
        order = order[inds + 1]

    return keep

def multiclass_nms(boxes, scores, nms_thr, score_thr):
    """Multiclass NMS implemented in Numpy. Class-agnostic version."""
    cls_inds = scores.argmax(1)
    cls_scores = scores[np.arange(len(cls_inds)), cls_inds]

    valid_score_mask = cls_scores > score_thr
    if valid_score_mask.sum() == 0:
        return None
    valid_scores = cls_scores[valid_score_mask]
    valid_boxes = boxes[valid_score_mask]
    valid_cls_inds = cls_inds[valid_score_mask]
    keep = nms(valid_boxes, valid_scores, nms_thr)
    if keep:
        dets = np.concatenate(
            [valid_boxes[keep], valid_scores[keep, None], valid_cls_inds[keep, None]], 1
        )
    return dets
def vis(img, boxes, scores, cls_ids, conf=0.5, class_names=None):

    for i in range(len(boxes)):
        box = boxes[i]
        cls_id = int(cls_ids[i])
        score = scores[i]
        if score < conf:
            continue
        x0 = int(box[0])
        y0 = int(box[1])
        x1 = int(box[2])
        y1 = int(box[3])

        color = (_COLORS[cls_id] * 255).astype(np.uint8).tolist()
        text = '{}:{:.1f}%'.format(class_names[cls_id], score * 100)
        txt_color = (0, 0, 0) if np.mean(_COLORS[cls_id]) > 0.5 else (255, 255, 255)
        font = cv2.FONT_HERSHEY_SIMPLEX

        txt_size = cv2.getTextSize(text, font, 0.4, 1)[0]
        cv2.rectangle(img, (x0, y0), (x1, y1), color, 2)

        txt_bk_color = (_COLORS[cls_id] * 255 * 0.7).astype(np.uint8).tolist()
        cv2.rectangle(
            img,
            (x0, y0 + 1),
            (x0 + txt_size[0] + 1, y0 + int(1.5*txt_size[1])),
            txt_bk_color,
            -1
        )
        cv2.putText(img, text, (x0, y0 + txt_size[1]), font, 0.4, txt_color, thickness=1)

    return img
_COLORS = np.array(
    [
        0.000, 0.447, 0.741,
        0.850, 0.325, 0.098,
        0.929, 0.694, 0.125,
        0.494, 0.184, 0.556,
        0.466, 0.674, 0.188,
        0.301, 0.745, 0.933,
        0.635, 0.078, 0.184,
        0.300, 0.300, 0.300,
        0.600, 0.600, 0.600,
        1.000, 0.000, 0.000,
        1.000, 0.500, 0.000,
        0.749, 0.749, 0.000,
        0.000, 1.000, 0.000,
        0.000, 0.000, 1.000,
        0.667, 0.000, 1.000,
        0.333, 0.333, 0.000,
        0.333, 0.667, 0.000,
        0.333, 1.000, 0.000,
        0.667, 0.333, 0.000,
        0.667, 0.667, 0.000,
        0.667, 1.000, 0.000,
        1.000, 0.333, 0.000,
        1.000, 0.667, 0.000,
        1.000, 1.000, 0.000,
        0.000, 0.333, 0.500,
        0.000, 0.667, 0.500,
        0.000, 1.000, 0.500,
        0.333, 0.000, 0.500,
        0.333, 0.333, 0.500,
        0.333, 0.667, 0.500,
        0.333, 1.000, 0.500,
        0.667, 0.000, 0.500,
        0.667, 0.333, 0.500,
        0.667, 0.667, 0.500,
        0.667, 1.000, 0.500,
        1.000, 0.000, 0.500,
        1.000, 0.333, 0.500,
        1.000, 0.667, 0.500,
        1.000, 1.000, 0.500,
        0.000, 0.333, 1.000,
        0.000, 0.667, 1.000,
        0.000, 1.000, 1.000,
        0.333, 0.000, 1.000,
        0.333, 0.333, 1.000,
        0.333, 0.667, 1.000,
        0.333, 1.000, 1.000,
        0.667, 0.000, 1.000,
        0.667, 0.333, 1.000,
        0.667, 0.667, 1.000,
        0.667, 1.000, 1.000,
        1.000, 0.000, 1.000,
        1.000, 0.333, 1.000,
        1.000, 0.667, 1.000,
        0.333, 0.000, 0.000,
        0.500, 0.000, 0.000,
        0.667, 0.000, 0.000,
        0.833, 0.000, 0.000,
        1.000, 0.000, 0.000,
        0.000, 0.167, 0.000,
        0.000, 0.333, 0.000,
        0.000, 0.500, 0.000,
        0.000, 0.667, 0.000,
        0.000, 0.833, 0.000,
        0.000, 1.000, 0.000,
        0.000, 0.000, 0.167,
        0.000, 0.000, 0.333,
        0.000, 0.000, 0.500,
        0.000, 0.000, 0.667,
        0.000, 0.000, 0.833,
        0.000, 0.000, 1.000,
        0.000, 0.000, 0.000,
        0.143, 0.143, 0.143,
        0.286, 0.286, 0.286,
        0.429, 0.429, 0.429,
        0.571, 0.571, 0.571,
        0.714, 0.714, 0.714,
        0.857, 0.857, 0.857,
        0.000, 0.447, 0.741,
        0.314, 0.717, 0.741,
        0.50, 0.5, 0,
        0.000, 0.447, 0.741,## new
        0.850, 0.325, 0.098,
        0.929, 0.694, 0.125,
        0.494, 0.184, 0.556,
        0.466, 0.674, 0.188,
        0.301, 0.745, 0.933,
        0.635, 0.078, 0.184,
        0.300, 0.300, 0.300,
        0.600, 0.600, 0.600,
        1.000, 0.000, 0.000,
        1.000, 0.500, 0.000,
        0.749, 0.749, 0.000,
        0.000, 1.000, 0.000,
        0.000, 0.000, 1.000,
        0.667, 0.000, 1.000,
        0.333, 0.333, 0.000,
        0.333, 0.667, 0.000,
        0.333, 1.000, 0.000,
        0.667, 0.333, 0.000,
        0.667, 0.667, 0.000,
        0.667, 1.000, 0.000,
        1.000, 0.333, 0.000,
        1.000, 0.667, 0.000,
        1.000, 1.000, 0.000,
        0.000, 0.333, 0.500,
        0.000, 0.667, 0.500,
        0.000, 1.000, 0.500,
        0.333, 0.000, 0.500,
        0.333, 0.333, 0.500,
        0.333, 0.667, 0.500,
        0.333, 1.000, 0.500,
        0.667, 0.000, 0.500,
        0.667, 0.333, 0.500,
    ]
).astype(np.float32).reshape(-1, 3)
VOC_CLASSES=(
    "3+2-2",
    "3jia2",
    "aerbeisi",
    "anmuxi",
    "aoliao",
    "asamu",
    "baicha",
    "baishikele",
    "baishikele-2",
    "baokuangli",
    "binghongcha",
    "bingqilinniunai",
    "bingtangxueli",
    "buding",
    "chacui",
    "chapai",
    "chapai2",
    "damaicha",
    "daofandian1",
    "daofandian2",
    "daofandian3",
    "daofandian4",
    "dongpeng",
    "dongpeng-b",
    "fenda",
    "gudasao",
    "guolicheng",
    "guolicheng2",
    "haitai",
    "haochidian",
    "haoliyou",
    "heweidao",
    "heweidao2",
    "heweidao3",
    "hongniu",
    "hongniu2",
    "hongshaoniurou",
    "jianjiao",
    "jianlibao",
    "jindian",
    "kafei",
    "kaomo_gali",
    "kaomo_jiaoyan",
    "kaomo_shaokao",
    "kaomo_xiangcon",
    "kebike",
    "kele",
    "kele-b",
    "kele-b-2",
    "laotansuancai",
    "liaomian",
    "libaojian",
    "lingdukele",
    "lingdukele-b",
    "liziyuan",
    "lujiaoxiang",
    "lujikafei",
    "luxiangniurou",
    "maidong",
    "mangguoxiaolao",
    "meiniye",
    "mengniu",
    "mengniuzaocan",
    "moliqingcha",
    "nfc",
    "niudufen",
    "niunai",
    "nongfushanquan",
    "qingdaowangzi-1",
    "qingdaowangzi-2",
    "qinningshui",
    "quchenshixiangcao",
    "rancha-1",
    "rancha-2",
    "rousongbing",
    "rusuanjunqishui",
    "suanlafen",
    "suanlaniurou",
    "taipingshuda",
    "tangdaren",
    "tangdaren2",
    "tangdaren3",
    "ufo",
    "ufo2",
    "wanglaoji",
    "wanglaoji-c",
    "wangzainiunai",
    "weic",
    "weitanai",
    "weitanai2",
    "weitanaiditang",
    "weitaningmeng",
    "weitaningmeng-bottle",
    "weiweidounai",
    "wuhounaicha",
    "wulongcha",
    "xianglaniurou",
    "xianguolao",
    "xianxiayuban",
    "xuebi",
    "xuebi-b",
    "xuebi2",
    "yezhi",
    "yibao",
    "yida",
    "yingyangkuaixian",
    "yitengyuan",
    "youlemei",
    "yousuanru",
    "youyanggudong",
    "yuanqishui",
    "zaocanmofang",
    "zihaiguo",
)

#-------#
dets = multiclass_nms(boxes_xyxy, scores, nms_thr=0.45, score_thr=0.1)#阈值修改
if dets is not None:
    final_boxes, final_scores, final_cls_inds = dets[:, :4], dets[:, 4], dets[:, 5]
    #画出检测框
    origin_img = vis(origin_img, final_boxes, final_scores, final_cls_inds,
                     conf=0.1, class_names=VOC_CLASSES)

###########计算价格######################
#######两张图片 final_cls_inds#########
# 仅供参考
statistic_dic_b = {name: 0 for name in VOC_CLASSES}
statistic_dic_a = {name: 0 for name in VOC_CLASSES}
list_cls_b = final_cls_inds_b.tolist()  # 开门前--类别
list_cls_a = final_cls_inds_a.tolist()  # 开门后--类别
for c in list_cls_a:  # 计算物品个数
    statistic_dic_a[VOC_CLASSES[int(c)]] += 1
    for c in list_cls_b:
        statistic_dic_b[VOC_CLASSES[int(c)]] += 1
# 开门前--
statistic_dic = sorted(statistic_dic_b.items(), key=lambda x: x[1], reverse=True)
statistic_dic = [i for i in statistic_dic if i[1] > 0]
# [('红烧牛肉'，5),('可乐','1')...]
results = [' ' + str(i[0]) + '：' + str(i[1]) for i in statistic_dic]  # to string
# 开门后--
statistic_dic = sorted(statistic_dic_a.items(), key=lambda x: x[1], reverse=True)
statistic_dic = [i for i in statistic_dic if i[1] > 0]
# [('红烧牛肉'，5),('可乐','1')...]
results = [' ' + str(i[0]) + '：' + str(i[1]) for i in statistic_dic]  # to string


JIAGE = {
    "3+2-2":1,
    "3jia2":1,
    "aerbeisi":1,
    "anmuxi":1,
    "aoliao":1,
    "asamu":1,
    "baicha":1,
    "baishikele":1,
    "baishikele-2":1,
    "baokuangli":1,
    "binghongcha":1,
    "bingqilinniunai":1,
    "bingtangxueli":1,
    "buding":1,
    "chacui":1,
    "chapai":1,
    "chapai2":1,
    "damaicha":1,
    "daofandian1":1,
    "daofandian2":1,
    "daofandian3":1,
    "daofandian4":1,
    "dongpeng":1,
    "dongpeng-b":1,
    "fenda":1,
    "gudasao":1,
    "guolicheng":1,
    "guolicheng2":1,
    "haitai":1,
    "haochidian":1,
    "haoliyou":1,
    "heweidao":1,
    "heweidao2":1,
    "heweidao3":1,
    "hongniu":1,
    "hongniu2":1,
    "hongshaoniurou":1,
    "jianjiao":1,
    "jianlibao":1,
    "jindian":1,
    "kafei":1,
    "kaomo_gali":1,
    "kaomo_jiaoyan":1,
    "kaomo_shaokao":1,
    "kaomo_xiangcon":1,
    "kebike":1,
    "kele":1.5,
    "kele-b":1,
    "kele-b-2":1,
    "laotansuancai":1,
    "liaomian":1,
    "libaojian":1,
    "lingdukele":1,
    "lingdukele-b":1,
    "liziyuan":1,
    "lujiaoxiang":1,
    "lujikafei":1,
    "luxiangniurou":1,
    "maidong":1,
    "mangguoxiaolao":1,
    "meiniye":1,
    "mengniu":1,
    "mengniuzaocan":1,
    "moliqingcha":1,
    "nfc":1,
    "niudufen":1,
    "niunai":1,
    "nongfushanquan":1,
    "qingdaowangzi-1":1,
    "qingdaowangzi-2":1,
    "qinningshui":1,
    "quchenshixiangcao":1,
    "rancha-1":1,
    "rancha-2":1,
    "rousongbing":1,
    "rusuanjunqishui":1,
    "suanlafen":1,
    "suanlaniurou":1,
    "taipingshuda":1,
    "tangdaren":1,
    "tangdaren2":1,
    "tangdaren3":1,
    "ufo":1,
    "ufo2":1,
    "wanglaoji":1,
    "wanglaoji-c":1,
    "wangzainiunai":1,
    "weic":1,
    "weitanai":1,
    "weitanai2":1,
    "weitanaiditang":1,
    "weitaningmeng":1,
    "weitaningmeng-bottle":1,
    "weiweidounai":1,
    "wuhounaicha":1,
    "wulongcha":1,
    "xianglaniurou":1,
    "xianguolao":1,
    "xianxiayuban":1,
    "xuebi":1,
    "xuebi-b":1,
    "xuebi2":1,
    "yezhi":1,
    "yibao":1,
    "yida":1,
    "yingyangkuaixian":1,
    "yitengyuan":1,
    "youlemei":1,
    "yousuanru":1,
    "youyanggudong":1,
    "yuanqishui":1,
    "zaocanmofang":1,
    "zihaiguo":1
}
# 开始计算 购物及其个数
# 需要一个 价格 字典表
item_out = {}
item_b = list(statistic_dic_b.keys())  # 购物前的物品名称
item_a = list(statistic_dic_a.keys())  # 购物后的物品名称
# 加入 try -- item_a 包含于 item_b
for k in item_a:
    vb = statistic_dic_b[k]
va = statistic_dic_a[k]
item_out[k] = abs(vb - va)
item_b.remove(k)
if len(item_b) > 0:
    for k in item_b:
        item_out[k] = statistic_dic_b[k]

statistic_dic = sorted(item_out.items(), key=lambda x: x[1], reverse=True)
statistic_dic = [i for i in statistic_dic if i[1] > 0]
results = ['  ' + str(i[0]) + '：' + str(i[1]) + '个      ' + str(JIAGE[i[0]]) + '元' for i in statistic_dic]
out = 0
for i in statistic_dic:
    out += i[1] * JIAGE[i[0]]

print('购物总价格',out)

