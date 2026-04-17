from sqlalchemy import create_engine, text, inspect
from app.config import settings

DEFAULT_IMAGING_CHECKS = [
    {"check_id":"XRAY_CHEST_FRONT","check_category":"X线检查","check_subcategory":"胸部正位片","check_part":"胸部","is_enhanced":0,"applicable_gender":"通用","check_desc":"体检/常规胸部基础检查，观察肺部、心脏、胸廓","department":"放射科","sort_num":1},
    {"check_id":"XRAY_CHEST_FRONT_SIDE","check_category":"X线检查","check_subcategory":"胸部正侧位片","check_part":"胸部","is_enhanced":0,"applicable_gender":"通用","check_desc":"更全面观察胸部病变，补充正位片盲区","department":"放射科","sort_num":2},
    {"check_id":"XRAY_SKULL_FRONT_SIDE","check_category":"X线检查","check_subcategory":"头颅正侧位片","check_part":"头颅","is_enhanced":0,"applicable_gender":"通用","check_desc":"观察头颅骨质结构，排查骨折、畸形","department":"放射科","sort_num":3},
    {"check_id":"XRAY_CERVICAL_SPINE","check_category":"X线检查","check_subcategory":"颈椎正侧位/双斜位","check_part":"颈椎","is_enhanced":0,"applicable_gender":"通用","check_desc":"观察颈椎骨质、椎间隙、生理曲度","department":"放射科","sort_num":4},
    {"check_id":"XRAY_THORACIC_SPINE","check_category":"X线检查","check_subcategory":"胸椎正侧位","check_part":"胸椎","is_enhanced":0,"applicable_gender":"通用","check_desc":"排查胸椎骨折、骨质增生、侧弯","department":"放射科","sort_num":5},
    {"check_id":"XRAY_LUMBAR_SPINE","check_category":"X线检查","check_subcategory":"腰椎正侧位/过伸过屈位","check_part":"腰椎","is_enhanced":0,"applicable_gender":"通用","check_desc":"观察腰椎间盘、椎间隙、椎体形态","department":"放射科","sort_num":6},
    {"check_id":"XRAY_SHOULDER_JOINT","check_category":"X线检查","check_subcategory":"肩关节正位","check_part":"肩关节","is_enhanced":0,"applicable_gender":"通用","check_desc":"排查肩关节脱位、骨折、骨质增生","department":"放射科","sort_num":7},
    {"check_id":"XRAY_ELBOW_JOINT","check_category":"X线检查","check_subcategory":"肘关节正侧位","check_part":"肘关节","is_enhanced":0,"applicable_gender":"通用","check_desc":"观察肘关节骨质、关节间隙","department":"放射科","sort_num":8},
    {"check_id":"XRAY_WRIST_JOINT","check_category":"X线检查","check_subcategory":"腕关节正侧位","check_part":"腕关节","is_enhanced":0,"applicable_gender":"通用","check_desc":"排查腕骨骨折、脱位、关节炎","department":"放射科","sort_num":9},
    {"check_id":"XRAY_HIP_JOINT","check_category":"X线检查","check_subcategory":"髋关节正位","check_part":"髋关节","is_enhanced":0,"applicable_gender":"通用","check_desc":"观察髋关节发育、骨质、关节间隙","department":"放射科","sort_num":10},
    {"check_id":"XRAY_KNEE_JOINT","check_category":"X线检查","check_subcategory":"膝关节正侧位","check_part":"膝关节","is_enhanced":0,"applicable_gender":"通用","check_desc":"排查膝关节骨折、骨质增生、退变","department":"放射科","sort_num":11},
    {"check_id":"XRAY_ANKLE_JOINT","check_category":"X线检查","check_subcategory":"踝关节正侧位","check_part":"踝关节","is_enhanced":0,"applicable_gender":"通用","check_desc":"观察踝关节骨质、关节间隙","department":"放射科","sort_num":12},
    {"check_id":"XRAY_PELVIS","check_category":"X线检查","check_subcategory":"骨盆正位","check_part":"骨盆","is_enhanced":0,"applicable_gender":"通用","check_desc":"排查骨盆骨折、髋关节病变","department":"放射科","sort_num":13},
    {"check_id":"XRAY_LIMB_LONG_BONE","check_category":"X线检查","check_subcategory":"四肢长骨正侧位","check_part":"四肢长骨","is_enhanced":0,"applicable_gender":"通用","check_desc":"排查四肢长骨骨折、骨质病变","department":"放射科","sort_num":14},
    {"check_id":"XRAY_ABDOMEN_STANDING","check_category":"X线检查","check_subcategory":"腹部立位平片","check_part":"腹部","is_enhanced":0,"applicable_gender":"通用","check_desc":"排查肠梗阻、消化道穿孔","department":"放射科","sort_num":15},
    {"check_id":"XRAY_KUB","check_category":"X线检查","check_subcategory":"泌尿系平片（KUB）","check_part":"泌尿系","is_enhanced":0,"applicable_gender":"通用","check_desc":"观察尿路结石、肾脏轮廓","department":"放射科","sort_num":16},
    {"check_id":"XRAY_MAMMOGRAPHY","check_category":"X线检查","check_subcategory":"乳腺钼靶","check_part":"乳腺","is_enhanced":0,"applicable_gender":"女","check_desc":"乳腺钙化、肿瘤筛查（40岁以上女性）","department":"放射科","sort_num":17},
    {"check_id":"CT_HEAD_PLAIN","check_category":"CT检查","check_subcategory":"头部CT平扫","check_part":"头颅","is_enhanced":0,"applicable_gender":"通用","check_desc":"急诊/常规头颅病变筛查，无造影剂","department":"放射科","sort_num":1},
    {"check_id":"CT_HEAD_ENHANCED","check_category":"CT检查","check_subcategory":"头部CT增强","check_part":"头颅","is_enhanced":1,"applicable_gender":"通用","check_desc":"需注射造影剂，用于病变定性诊断","department":"放射科","sort_num":2},
    {"check_id":"CT_HEAD_CTA","check_category":"CT检查","check_subcategory":"头部CTA（脑血管成像）","check_part":"头颅血管","is_enhanced":1,"applicable_gender":"通用","check_desc":"观察脑血管形态，排查动脉瘤、狭窄","department":"放射科","sort_num":3},
    {"check_id":"CT_NECK_PLAIN","check_category":"CT检查","check_subcategory":"颈部CT平扫","check_part":"颈部","is_enhanced":0,"applicable_gender":"通用","check_desc":"排查颈部软组织、骨质病变","department":"放射科","sort_num":4},
    {"check_id":"CT_NECK_ENHANCED","check_category":"CT检查","check_subcategory":"颈部CT增强","check_part":"颈部","is_enhanced":1,"applicable_gender":"通用","check_desc":"颈部病变定性，如肿瘤、淋巴结肿大","department":"放射科","sort_num":5},
    {"check_id":"CT_NECK_CTA","check_category":"CT检查","check_subcategory":"颈部CTA","check_part":"颈部血管","is_enhanced":1,"applicable_gender":"通用","check_desc":"观察颈部血管狭窄、斑块","department":"放射科","sort_num":6},
    {"check_id":"CT_CHEST_PLAIN","check_category":"CT检查","check_subcategory":"胸部CT平扫","check_part":"胸部","is_enhanced":0,"applicable_gender":"通用","check_desc":"肺部结节、炎症、肿瘤筛查","department":"放射科","sort_num":7},
    {"check_id":"CT_CHEST_ENHANCED","check_category":"CT检查","check_subcategory":"胸部CT增强","check_part":"胸部","is_enhanced":1,"applicable_gender":"通用","check_desc":"胸部病变定性，如肿瘤分期、血管病变","department":"放射科","sort_num":8},
    {"check_id":"CT_CHEST_CTA","check_category":"CT检查","check_subcategory":"胸部CTA（肺动脉/主动脉）","check_part":"胸部血管","is_enhanced":1,"applicable_gender":"通用","check_desc":"排查肺栓塞、主动脉夹层","department":"放射科","sort_num":9},
    {"check_id":"CT_ABDOMEN_PLAIN","check_category":"CT检查","check_subcategory":"腹部CT平扫","check_part":"腹部","is_enhanced":0,"applicable_gender":"通用","check_desc":"腹部脏器病变初筛","department":"放射科","sort_num":10},
    {"check_id":"CT_ABDOMEN_ENHANCED","check_category":"CT检查","check_subcategory":"腹部CT增强","check_part":"腹部","is_enhanced":1,"applicable_gender":"通用","check_desc":"腹部肿瘤、血管病变定性诊断","department":"放射科","sort_num":11},
    {"check_id":"CT_PELVIS_PLAIN","check_category":"CT检查","check_subcategory":"盆腔CT平扫","check_part":"盆腔","is_enhanced":0,"applicable_gender":"通用","check_desc":"盆腔脏器、骨质病变初筛","department":"放射科","sort_num":12},
    {"check_id":"CT_PELVIS_ENHANCED","check_category":"CT检查","check_subcategory":"盆腔CT增强","check_part":"盆腔","is_enhanced":1,"applicable_gender":"通用","check_desc":"盆腔肿瘤、炎症定性诊断","department":"放射科","sort_num":13},
    {"check_id":"CT_SPINE_CERVICAL","check_category":"CT检查","check_subcategory":"颈椎CT","check_part":"颈椎","is_enhanced":0,"applicable_gender":"通用","check_desc":"观察颈椎间盘、椎管、骨质细节","department":"放射科","sort_num":14},
    {"check_id":"CT_SPINE_THORACIC","check_category":"CT检查","check_subcategory":"胸椎CT","check_part":"胸椎","is_enhanced":0,"applicable_gender":"通用","check_desc":"排查胸椎细微骨折、椎管病变","department":"放射科","sort_num":15},
    {"check_id":"CT_SPINE_LUMBAR","check_category":"CT检查","check_subcategory":"腰椎CT","check_part":"腰椎","is_enhanced":0,"applicable_gender":"通用","check_desc":"观察腰椎间盘突出、椎管狭窄","department":"放射科","sort_num":16},
    {"check_id":"CT_JOINT","check_category":"CT检查","check_subcategory":"骨关节CT","check_part":"骨关节","is_enhanced":0,"applicable_gender":"通用","check_desc":"观察骨关节细微骨折、脱位","department":"放射科","sort_num":17},
    {"check_id":"CT_CORONARY_CTA","check_category":"CT检查","check_subcategory":"冠状动脉CTA（冠脉CT）","check_part":"心脏冠脉","is_enhanced":1,"applicable_gender":"通用","check_desc":"无创筛查冠心病、冠脉狭窄","department":"放射科","sort_num":18},
    {"check_id":"CT_CTU","check_category":"CT检查","check_subcategory":"CT泌尿系成像（CTU）","check_part":"泌尿系","is_enhanced":1,"applicable_gender":"通用","check_desc":"全面观察泌尿系形态、病变","department":"放射科","sort_num":19},
    {"check_id":"CT_GUIDE_PUNCTURE","check_category":"CT检查","check_subcategory":"CT引导下穿刺/定位","check_part":"全身","is_enhanced":0,"applicable_gender":"通用","check_desc":"精准定位穿刺，获取病理样本","department":"放射科","sort_num":20},
    {"check_id":"MRI_HEAD_PLAIN","check_category":"MRI检查","check_subcategory":"头颅MRI平扫","check_part":"头颅","is_enhanced":0,"applicable_gender":"通用","check_desc":"观察脑实质、脑室病变，无辐射","department":"放射科","sort_num":1},
    {"check_id":"MRI_HEAD_ENHANCED","check_category":"MRI检查","check_subcategory":"头颅MRI增强","check_part":"头颅","is_enhanced":1,"applicable_gender":"通用","check_desc":"脑肿瘤、炎症定性诊断","department":"放射科","sort_num":2},
    {"check_id":"MRI_HEAD_MRA","check_category":"MRI检查","check_subcategory":"头颅MRA（脑血管）","check_part":"头颅血管","is_enhanced":0,"applicable_gender":"通用","check_desc":"无创观察脑血管形态，排查狭窄","department":"放射科","sort_num":3},
    {"check_id":"MRI_PITUITARY","check_category":"MRI检查","check_subcategory":"垂体MRI","check_part":"垂体","is_enhanced":1,"applicable_gender":"通用","check_desc":"观察垂体大小、形态，排查腺瘤","department":"放射科","sort_num":4},
    {"check_id":"MRI_NECK","check_category":"MRI检查","check_subcategory":"颈部MRI","check_part":"颈部","is_enhanced":0,"applicable_gender":"通用","check_desc":"观察颈部软组织、淋巴结病变","department":"放射科","sort_num":5},
    {"check_id":"MRI_CERVICAL_SPINE","check_category":"MRI检查","check_subcategory":"颈椎MRI","check_part":"颈椎","is_enhanced":0,"applicable_gender":"通用","check_desc":"观察颈椎间盘、脊髓、神经根","department":"放射科","sort_num":6},
    {"check_id":"MRI_THORACIC_SPINE","check_category":"MRI检查","check_subcategory":"胸椎MRI","check_part":"胸椎","is_enhanced":0,"applicable_gender":"通用","check_desc":"排查胸椎脊髓病变、椎体转移瘤","department":"放射科","sort_num":7},
    {"check_id":"MRI_LUMBAR_SPINE","check_category":"MRI检查","check_subcategory":"腰椎MRI","check_part":"腰椎","is_enhanced":0,"applicable_gender":"通用","check_desc":"腰椎间盘突出、椎管狭窄确诊","department":"放射科","sort_num":8},
    {"check_id":"MRI_CHEST","check_category":"MRI检查","check_subcategory":"胸部MRI","check_part":"胸部","is_enhanced":0,"applicable_gender":"通用","check_desc":"观察胸部软组织、纵隔病变","department":"放射科","sort_num":9},
    {"check_id":"MRI_UPPER_ABDOMEN","check_category":"MRI检查","check_subcategory":"上腹部MRI","check_part":"上腹部","is_enhanced":0,"applicable_gender":"通用","check_desc":"观察肝、胆、胰、脾病变","department":"放射科","sort_num":10},
    {"check_id":"MRI_LOWER_ABDOMEN","check_category":"MRI检查","check_subcategory":"下腹部/盆腔MRI","check_part":"下腹部/盆腔","is_enhanced":0,"applicable_gender":"通用","check_desc":"观察盆腔脏器、软组织病变","department":"放射科","sort_num":11},
    {"check_id":"MRI_SHOULDER_JOINT","check_category":"MRI检查","check_subcategory":"肩关节MRI","check_part":"肩关节","is_enhanced":0,"applicable_gender":"通用","check_desc":"观察肩关节韧带、肌腱、软骨病变","department":"放射科","sort_num":12},
    {"check_id":"MRI_ELBOW_JOINT","check_category":"MRI检查","check_subcategory":"肘关节MRI","check_part":"肘关节","is_enhanced":0,"applicable_gender":"通用","check_desc":"排查肘关节软组织、韧带损伤","department":"放射科","sort_num":13},
    {"check_id":"MRI_WRIST_JOINT","check_category":"MRI检查","check_subcategory":"腕关节MRI","check_part":"腕关节","is_enhanced":0,"applicable_gender":"通用","check_desc":"观察腕关节软骨、韧带、肌腱","department":"放射科","sort_num":14},
    {"check_id":"MRI_HIP_JOINT","check_category":"MRI检查","check_subcategory":"髋关节MRI","check_part":"髋关节","is_enhanced":0,"applicable_gender":"通用","check_desc":"排查髋关节股骨头坏死、滑膜炎","department":"放射科","sort_num":15},
    {"check_id":"MRI_KNEE_JOINT","check_category":"MRI检查","check_subcategory":"膝关节MRI","check_part":"膝关节","is_enhanced":0,"applicable_gender":"通用","check_desc":"观察膝关节软骨、韧带、半月板","department":"放射科","sort_num":16},
    {"check_id":"MRI_ANKLE_JOINT","check_category":"MRI检查","check_subcategory":"踝关节MRI","check_part":"踝关节","is_enhanced":0,"applicable_gender":"通用","check_desc":"排查踝关节韧带、软骨损伤","department":"放射科","sort_num":17},
    {"check_id":"MRI_PROSTATE","check_category":"MRI检查","check_subcategory":"前列腺MRI","check_part":"前列腺","is_enhanced":1,"applicable_gender":"男","check_desc":"前列腺癌筛查、分期","department":"放射科","sort_num":18},
    {"check_id":"MRI_BREAST","check_category":"MRI检查","check_subcategory":"乳腺MRI","check_part":"乳腺","is_enhanced":1,"applicable_gender":"女","check_desc":"乳腺病变定性，补充钼靶/超声","department":"放射科","sort_num":19},
    {"check_id":"MRI_MRCP","check_category":"MRI检查","check_subcategory":"MRCP（磁共振胰胆管成像）","check_part":"胰胆管","is_enhanced":0,"applicable_gender":"通用","check_desc":"无创观察胰胆管形态，排查结石、梗阻","department":"放射科","sort_num":20},
    {"check_id":"MRI_MRU","check_category":"MRI检查","check_subcategory":"MRU（磁共振泌尿系成像）","check_part":"泌尿系","is_enhanced":0,"applicable_gender":"通用","check_desc":"观察泌尿系形态，排查梗阻、畸形","department":"放射科","sort_num":21},
    {"check_id":"USG_ABDOMEN","check_category":"超声检查","check_subcategory":"腹部超声（肝、胆、胰、脾、双肾）","check_part":"腹部","is_enhanced":0,"applicable_gender":"通用","check_desc":"腹部脏器常规筛查，无辐射、无创","department":"超声科","sort_num":1},
    {"check_id":"USG_URINARY","check_category":"超声检查","check_subcategory":"泌尿系超声（肾、输尿管、膀胱、前列腺）","check_part":"泌尿系","is_enhanced":0,"applicable_gender":"通用","check_desc":"排查泌尿系结石、积水、前列腺增生","department":"超声科","sort_num":2},
    {"check_id":"USG_GYNECOLOGY","check_category":"超声检查","check_subcategory":"妇科超声（子宫、附件）","check_part":"盆腔","is_enhanced":0,"applicable_gender":"女","check_desc":"排查子宫肌瘤、卵巢囊肿、盆腔炎","department":"超声科","sort_num":3},
    {"check_id":"USG_OBSTETRICS","check_category":"超声检查","check_subcategory":"产科超声（早孕/中孕/晚孕）","check_part":"盆腔","is_enhanced":0,"applicable_gender":"女","check_desc":"观察胎儿发育、胎位、羊水","department":"超声科","sort_num":4},
    {"check_id":"USG_HEART","check_category":"超声检查","check_subcategory":"心脏超声（心超/彩超）","check_part":"心脏","is_enhanced":0,"applicable_gender":"通用","check_desc":"观察心脏结构、功能、瓣膜病变","department":"超声科","sort_num":5},
    {"check_id":"USG_NECK_VESSEL","check_category":"超声检查","check_subcategory":"颈部血管超声","check_part":"颈部血管","is_enhanced":0,"applicable_gender":"通用","check_desc":"排查颈部血管斑块、狭窄、闭塞","department":"超声科","sort_num":6},
    {"check_id":"USG_LIMB_VESSEL","check_category":"超声检查","check_subcategory":"四肢血管超声","check_part":"四肢血管","is_enhanced":0,"applicable_gender":"通用","check_desc":"观察四肢动静脉血栓、狭窄","department":"超声科","sort_num":7},
    {"check_id":"USG_THYROID","check_category":"超声检查","check_subcategory":"甲状腺超声","check_part":"甲状腺","is_enhanced":0,"applicable_gender":"通用","check_desc":"甲状腺结节、甲亢/甲减筛查","department":"超声科","sort_num":8},
    {"check_id":"USG_BREAST","check_category":"超声检查","check_subcategory":"乳腺超声","check_part":"乳腺","is_enhanced":0,"applicable_gender":"女","check_desc":"乳腺结节、增生筛查，适合致密型乳腺","department":"超声科","sort_num":9},
    {"check_id":"USG_LYMPH_NODE","check_category":"超声检查","check_subcategory":"淋巴结超声","check_part":"全身淋巴结","is_enhanced":0,"applicable_gender":"通用","check_desc":"排查淋巴结肿大、性质","department":"超声科","sort_num":10},
    {"check_id":"USG_SCROTUM","check_category":"超声检查","check_subcategory":"阴囊/睾丸超声","check_part":"阴囊/睾丸","is_enhanced":0,"applicable_gender":"男","check_desc":"排查睾丸附睾炎、精索静脉曲张","department":"超声科","sort_num":11},
    {"check_id":"USG_SOFT_TISSUE","check_category":"超声检查","check_subcategory":"肌肉软组织超声","check_part":"全身软组织","is_enhanced":0,"applicable_gender":"通用","check_desc":"排查肌肉、肌腱、筋膜病变","department":"超声科","sort_num":12},
    {"check_id":"USG_EFFUSION_LOCATION","check_category":"超声检查","check_subcategory":"胸腔/腹腔积液超声定位","check_part":"胸腔/腹腔","is_enhanced":0,"applicable_gender":"通用","check_desc":"精准定位积液位置，指导穿刺抽液","department":"超声科","sort_num":13},
    {"check_id":"USG_GUIDE_PUNCTURE","check_category":"超声检查","check_subcategory":"超声引导下穿刺","check_part":"全身","is_enhanced":0,"applicable_gender":"通用","check_desc":"实时引导穿刺，如甲状腺、肝穿刺","department":"超声科","sort_num":14},
    {"check_id":"INTERVENTION_CAG","check_category":"介入/造影检查","check_subcategory":"冠状动脉造影（CAG）","check_part":"心脏冠脉","is_enhanced":1,"applicable_gender":"通用","check_desc":"冠心病诊断金标准，需造影剂","department":"介入科","sort_num":1},
    {"check_id":"INTERVENTION_DSA","check_category":"介入/造影检查","check_subcategory":"脑血管造影（DSA）","check_part":"脑血管","is_enhanced":1,"applicable_gender":"通用","check_desc":"脑血管病变确诊金标准","department":"介入科","sort_num":2},
    {"check_id":"INTERVENTION_LOWER_LIMB_ANGIO","check_category":"介入/造影检查","check_subcategory":"下肢血管造影","check_part":"下肢血管","is_enhanced":1,"applicable_gender":"通用","check_desc":"排查下肢血管狭窄、闭塞、血栓","department":"介入科","sort_num":3},
    {"check_id":"INTERVENTION_GI_ANGIO","check_category":"介入/造影检查","check_subcategory":"上/下消化道造影（钡餐）","check_part":"消化道","is_enhanced":1,"applicable_gender":"通用","check_desc":"观察消化道形态、蠕动、溃疡","department":"放射科","sort_num":4},
    {"check_id":"INTERVENTION_IVP","check_category":"介入/造影检查","check_subcategory":"静脉肾盂造影（IVP）","check_part":"泌尿系","is_enhanced":1,"applicable_gender":"通用","check_desc":"观察尿路形态、排泄功能","department":"放射科","sort_num":5},
    {"check_id":"INTERVENTION_BILIARY_ANGIO","check_category":"介入/造影检查","check_subcategory":"胆道造影","check_part":"胆道","is_enhanced":1,"applicable_gender":"通用","check_desc":"排查胆道梗阻、结石","department":"介入科","sort_num":6},
    {"check_id":"INTERVENTION_FALLOPIAN_ANGIO","check_category":"介入/造影检查","check_subcategory":"输卵管造影","check_part":"输卵管","is_enhanced":1,"applicable_gender":"女","check_desc":"排查输卵管堵塞、畸形","department":"放射科","sort_num":7},
    {"check_id":"NUCLEAR_PET_CT","check_category":"核医学检查","check_subcategory":"PET-CT全身显像","check_part":"全身","is_enhanced":1,"applicable_gender":"通用","check_desc":"肿瘤筛查、转移灶定位、疗效评估","department":"核医学科","sort_num":1},
    {"check_id":"NUCLEAR_THYROID_SCAN","check_category":"核医学检查","check_subcategory":"甲状腺核素扫描","check_part":"甲状腺","is_enhanced":1,"applicable_gender":"通用","check_desc":"评估甲状腺功能、结节性质","department":"核医学科","sort_num":2},
    {"check_id":"NUCLEAR_KIDNEY_SCAN","check_category":"核医学检查","check_subcategory":"肾动态显像","check_part":"肾脏","is_enhanced":1,"applicable_gender":"通用","check_desc":"评估肾功能、分肾功能","department":"核医学科","sort_num":3},
    {"check_id":"NUCLEAR_BONE_SCAN","check_category":"核医学检查","check_subcategory":"骨扫描（全身骨显像）","check_part":"全身骨骼","is_enhanced":1,"applicable_gender":"通用","check_desc":"肿瘤骨转移、骨坏死筛查","department":"核医学科","sort_num":4},
    {"check_id":"NUCLEAR_MYOCARDIAL_SCAN","check_category":"核医学检查","check_subcategory":"心肌灌注显像","check_part":"心脏","is_enhanced":1,"applicable_gender":"通用","check_desc":"评估心肌缺血、心肌存活","department":"核医学科","sort_num":5},
    {"check_id":"SPECIAL_BMD","check_category":"特殊影像检查","check_subcategory":"骨密度检查","check_part":"腰椎/股骨颈","is_enhanced":0,"applicable_gender":"通用","check_desc":"诊断骨质疏松，评估骨折风险","department":"放射科","sort_num":1},
    {"check_id":"SPECIAL_ENDOSCOPE_IMAGE","check_category":"特殊影像检查","check_subcategory":"内镜相关影像（胃镜/肠镜/支气管镜）","check_part":"消化道/呼吸道","is_enhanced":0,"applicable_gender":"通用","check_desc":"内镜下病变图像采集","department":"内镜中心","sort_num":2},
    {"check_id":"SPECIAL_FUNDUS_PHOTO","check_category":"特殊影像检查","check_subcategory":"眼底照相/眼底OCT","check_part":"眼底","is_enhanced":0,"applicable_gender":"通用","check_desc":"观察视网膜、视神经病变","department":"眼科","sort_num":3}
]

def update_db():
    print(f"Connecting to database: {settings.DATABASE_URL}")
    engine = create_engine(settings.DATABASE_URL)
    inspector = inspect(engine)
    
    with engine.connect() as conn:
        pd_columns = [c["name"] for c in inspector.get_columns("patient_diseases")]
        
        # Add hospital column if not exists
        if "hospital" not in pd_columns:
            try:
                conn.execute(text("ALTER TABLE patient_diseases ADD COLUMN hospital VARCHAR(100)"))
                conn.commit()
                print("Added hospital column")
            except Exception as e:
                print(f"Error adding hospital: {e}")
        else:
            print("Hospital column already exists")

        # Add doctor_name column if not exists
        if "doctor_name" not in pd_columns:
            try:
                conn.execute(text("ALTER TABLE patient_diseases ADD COLUMN doctor_name VARCHAR(50)"))
                conn.commit()
                print("Added doctor_name column")
            except Exception as e:
                print(f"Error adding doctor_name: {e}")
        else:
            print("Doctor_name column already exists")

        diseases_columns = [c["name"] for c in inspector.get_columns("diseases")]
        new_diseases_columns = [
            ("chapter", "VARCHAR(50)"),
            ("chapter_code_range", "VARCHAR(100)"),
            ("chapter_name", "VARCHAR(200)"),
            ("section_code_range", "VARCHAR(100)"),
            ("section_name", "VARCHAR(200)"),
            ("subcategory_code", "VARCHAR(50)"),
            ("subcategory_name", "VARCHAR(200)"),
            ("diagnosis_code", "VARCHAR(50)"),
            ("diagnosis_name", "VARCHAR(200)"),
            ("is_active", "BOOLEAN DEFAULT TRUE"),
        ]
        for col_name, col_type in new_diseases_columns:
            if col_name in diseases_columns:
                continue
            try:
                conn.execute(text(f"ALTER TABLE diseases ADD COLUMN {col_name} {col_type}"))
                conn.commit()
                print(f"Added diseases.{col_name}")
            except Exception as e:
                print(f"Error adding diseases.{col_name}: {e}")

        if settings.DATABASE_URL.startswith("postgresql"):
            try:
                constraints = conn.execute(
                    text(
                        """
                        SELECT conname, pg_get_constraintdef(oid) AS def
                        FROM pg_constraint
                        WHERE conrelid = 'diseases'::regclass
                          AND contype = 'u'
                        """
                    )
                ).fetchall()
                for conname, condef in constraints:
                    if "UNIQUE (name)" in condef or "UNIQUE (code)" in condef:
                        conn.execute(text(f'ALTER TABLE diseases DROP CONSTRAINT "{conname}"'))
                        print(f"Dropped constraint: {conname}")
                conn.commit()
            except Exception as e:
                print(f"Error dropping diseases unique constraints: {e}")

        if not settings.DATABASE_URL.startswith("sqlite"):
            try:
                conn.execute(text("ALTER TABLE diseases ALTER COLUMN category DROP NOT NULL"))
                conn.commit()
                print("Set diseases.category nullable")
            except Exception as e:
                print(f"Error setting diseases.category nullable: {e}")

        # Medication plans update
        mp_columns = [c["name"] for c in inspector.get_columns("medication_plans")]
        if "manufacturer" not in mp_columns:
            try:
                conn.execute(text("ALTER TABLE medication_plans ADD COLUMN manufacturer VARCHAR(200)"))
                conn.commit()
                print("Added medication_plans.manufacturer column")
            except Exception as e:
                print(f"Error adding medication_plans.manufacturer: {e}")
        
        if "stock" not in mp_columns:
            try:
                conn.execute(text("ALTER TABLE medication_plans ADD COLUMN stock NUMERIC(10, 2)"))
                conn.commit()
                print("Added medication_plans.stock column")
            except Exception as e:
                print(f"Error adding medication_plans.stock: {e}")

        # ========== medications 表：清空并重建新字段结构 ==========
        try:
            conn.execute(text("DELETE FROM medications"))
            conn.commit()
            print("Cleared medications table")
        except Exception as e:
            print(f"Error clearing medications: {e}")

        # 检查并添加 medications 表新字段
        med_columns = [c["name"] for c in inspector.get_columns("medications")]
        new_med_columns = [
            ("title", "VARCHAR(300)"),
            ("title_url", "VARCHAR(500)"),
            ("number", "VARCHAR(100)"),
            ("r3", "VARCHAR(200)"),
            ("generic_name", "VARCHAR(200)"),
            ("pinyin", "VARCHAR(300)"),
            ("drug_nature", "VARCHAR(100)"),
            ("related_diseases", "TEXT"),
            ("properties", "TEXT"),
            ("main_ingredients", "TEXT"),
            ("indications", "TEXT"),
            ("adverse_reactions", "TEXT"),
            ("contraindications", "TEXT"),
            ("precautions", "TEXT"),
            ("pregnancy_lactation", "TEXT"),
            ("pediatric_use", "TEXT"),
            ("geriatric_use", "TEXT"),
            ("drug_interactions", "TEXT"),
            ("pharmacology_toxicology", "TEXT"),
            ("pharmacokinetics", "TEXT"),
            ("storage", "TEXT"),
            ("expiry_period", "VARCHAR(200)"),
        ]
        # 删除旧字段（如果存在）
        old_med_cols_to_drop = [
            "name", "english_name", "dosage_form", "production_address",
            "approval_date", "original_approval_number", "holder", "holder_address",
            "code", "code_remark", "description", "side_effects"
        ]
        if not settings.DATABASE_URL.startswith("sqlite"):
            for col_name in old_med_cols_to_drop:
                if col_name in med_columns:
                    try:
                        conn.execute(text(f"ALTER TABLE medications DROP COLUMN {col_name}"))
                        conn.commit()
                        print(f"Dropped medications.{col_name}")
                    except Exception as e:
                        print(f"Error dropping medications.{col_name}: {e}")
        
        # 刷新列名
        med_columns = [c["name"] for c in inspector.get_columns("medications")]
        for col_name, col_type in new_med_columns:
            if col_name in med_columns:
                continue
            try:
                conn.execute(text(f"ALTER TABLE medications ADD COLUMN {col_name} {col_type}"))
                conn.commit()
                print(f"Added medications.{col_name}")
            except Exception as e:
                print(f"Error adding medications.{col_name}: {e}")
        print("medications table schema updated")
        # =====================================================

        table_names = inspector.get_table_names()
        if "hospital_imaging_check" not in table_names:
            try:
                conn.execute(
                    text(
                        """
                        CREATE TABLE IF NOT EXISTS hospital_imaging_check (
                          check_id VARCHAR(32) PRIMARY KEY,
                          check_category VARCHAR(20) NOT NULL,
                          check_subcategory VARCHAR(50) NOT NULL,
                          check_part VARCHAR(30) NOT NULL,
                          is_enhanced SMALLINT NOT NULL DEFAULT 0,
                          applicable_gender VARCHAR(10) NOT NULL DEFAULT '通用',
                          check_desc VARCHAR(200) NOT NULL DEFAULT '',
                          department VARCHAR(20) NOT NULL,
                          sort_num INTEGER NOT NULL DEFAULT 0
                        )
                        """
                    )
                )
                conn.commit()
                print("Created hospital_imaging_check table")
            except Exception as e:
                print(f"Error creating hospital_imaging_check: {e}")
        try:
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_hic_category ON hospital_imaging_check (check_category)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_hic_part ON hospital_imaging_check (check_part)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_hic_gender ON hospital_imaging_check (applicable_gender)"))
            conn.commit()
        except Exception as e:
            print(f"Error creating hospital_imaging_check indexes: {e}")

        try:
            count = conn.execute(text("SELECT COUNT(*) FROM hospital_imaging_check")).scalar() or 0
            if int(count) == 0:
                for item in DEFAULT_IMAGING_CHECKS:
                    conn.execute(
                        text(
                            """
                            INSERT INTO hospital_imaging_check
                            (check_id, check_category, check_subcategory, check_part, is_enhanced, applicable_gender, check_desc, department, sort_num)
                            VALUES
                            (:check_id, :check_category, :check_subcategory, :check_part, :is_enhanced, :applicable_gender, :check_desc, :department, :sort_num)
                            """
                        ),
                        item
                    )
                conn.commit()
                print(f"Seeded hospital_imaging_check with {len(DEFAULT_IMAGING_CHECKS)} rows")
        except Exception as e:
            print(f"Error seeding hospital_imaging_check: {e}")

        # ========== members 表：创建成员管理表 ==========
        table_names = inspector.get_table_names()
        if "members" not in table_names:
            try:
                conn.execute(
                    text(
                        """
                        CREATE TABLE IF NOT EXISTS members (
                            id UUID PRIMARY KEY,
                            patient_id UUID NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
                            nickname VARCHAR(50) NOT NULL,
                            relation VARCHAR(20) NOT NULL,
                            age INTEGER,
                            gender VARCHAR(10),
                            height NUMERIC(5, 2),
                            weight NUMERIC(5, 2),
                            blood_type VARCHAR(10),
                            lifestyle TEXT,
                            allergy_history TEXT,
                            past_history TEXT,
                            family_history TEXT,
                            surgery_history TEXT,
                            other_notes TEXT,
                            is_current BOOLEAN DEFAULT FALSE,
                            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                        )
                        """
                    )
                )
                conn.commit()
                print("Created members table")
            except Exception as e:
                print(f"Error creating members table: {e}")
        
        # 为 members 表创建索引
        try:
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_members_patient_id ON members (patient_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_members_is_current ON members (is_current)"))
            conn.commit()
            print("Created members indexes")
        except Exception as e:
            print(f"Error creating members indexes: {e}")

        # ========== 为现有表添加 member_id 字段 ==========
        tables_to_add_member_id = [
            "patient_diseases",
            "reports",
            "health_readings",
            "reminders",
            "revisit_plans",
            "revisit_records",
            "medication_plans"
        ]
        
        for table_name in tables_to_add_member_id:
            try:
                columns = [c["name"] for c in inspector.get_columns(table_name)]
                if "member_id" not in columns:
                    conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN member_id UUID"))
                    conn.commit()
                    print(f"Added member_id column to {table_name}")
                else:
                    print(f"member_id column already exists in {table_name}")
            except Exception as e:
                print(f"Error adding member_id to {table_name}: {e}")
        
        # 为 member_id 字段创建索引
        for table_name in tables_to_add_member_id:
            try:
                conn.execute(text(f"CREATE INDEX IF NOT EXISTS idx_{table_name}_member_id ON {table_name} (member_id)"))
                conn.commit()
                print(f"Created member_id index for {table_name}")
            except Exception as e:
                print(f"Error creating member_id index for {table_name}: {e}")

        # ========== 创建通知中心表 ==========
        table_names = inspector.get_table_names()
        if "notifications" not in table_names:
            try:
                conn.execute(
                    text(
                        """
                        CREATE TABLE IF NOT EXISTS notifications (
                            id SERIAL PRIMARY KEY,
                            patient_id UUID NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
                            member_id UUID REFERENCES members(id) ON DELETE CASCADE,
                            title VARCHAR(200) NOT NULL,
                            content TEXT NOT NULL,
                            type VARCHAR(50) NOT NULL,
                            category VARCHAR(50) NOT NULL,
                            source_id VARCHAR(100),
                            source_type VARCHAR(50),
                            is_read BOOLEAN DEFAULT FALSE,
                            read_at TIMESTAMP WITH TIME ZONE,
                            priority INTEGER DEFAULT 0,
                            extra_data JSON,
                            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                        )
                        """
                    )
                )
                conn.commit()
                print("Created notifications table")
            except Exception as e:
                print(f"Error creating notifications table: {e}")
        
        # 为 notifications 表创建索引
        try:
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_notifications_patient_id ON notifications (patient_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_notifications_member_id ON notifications (member_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_notifications_is_read ON notifications (is_read)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_notifications_category ON notifications (category)"))
            conn.commit()
            print("Created notifications indexes")
        except Exception as e:
            print(f"Error creating notifications indexes: {e}")

        # ========== 为 members 表添加 avatar_url 字段 ==========
        try:
            member_columns = [c["name"] for c in inspector.get_columns("members")]
            if "avatar_url" not in member_columns:
                conn.execute(text("ALTER TABLE members ADD COLUMN avatar_url VARCHAR(500)"))
                conn.commit()
                print("Added avatar_url column to members table")
            else:
                print("avatar_url column already exists in members table")
        except Exception as e:
            print(f"Error adding avatar_url to members: {e}")

        # ========== 创建微信订阅消息授权表 ==========
        table_names = inspector.get_table_names()
        if "wechat_subscriptions" not in table_names:
            try:
                conn.execute(
                    text(
                        """
                        CREATE TABLE IF NOT EXISTS wechat_subscriptions (
                            id SERIAL PRIMARY KEY,
                            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                            openid VARCHAR(100) NOT NULL,
                            template_id VARCHAR(100) NOT NULL,
                            is_subscribed BOOLEAN DEFAULT TRUE,
                            subscribe_count INTEGER DEFAULT 0,
                            used_count INTEGER DEFAULT 0,
                            last_used_at TIMESTAMP WITH TIME ZONE,
                            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                        )
                        """
                    )
                )
                conn.commit()
                print("Created wechat_subscriptions table")
            except Exception as e:
                print(f"Error creating wechat_subscriptions table: {e}")
        
        # 为 wechat_subscriptions 表创建索引
        try:
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_wechat_sub_user_id ON wechat_subscriptions (user_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_wechat_sub_openid ON wechat_subscriptions (openid)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_wechat_sub_template_id ON wechat_subscriptions (template_id)"))
            conn.commit()
            print("Created wechat_subscriptions indexes")
        except Exception as e:
            print(f"Error creating wechat_subscriptions indexes: {e}")

if __name__ == "__main__":
    update_db()
