"""
迁移与种子脚本：
1. 为已有的 countries 表新增 10 个详情字段
2. 新建 cities 表
3. 将 data/ 目录下五个详情字典写入数据库（按 name 匹配）
"""
import sys
import os
from sqlalchemy import inspect, text

# 允许直接 python seed_data.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import Base, engine, SessionLocal
from models import Country, City

from data.countries_data_eu1 import COUNTRY_DETAILS_EU1
from data.countries_data_eu2 import COUNTRY_DETAILS_EU2
from data.countries_data_asia import COUNTRY_DETAILS_ASIA
from data.countries_data_americas import COUNTRY_DETAILS_AMERICAS
from data.countries_data_africa_oceania import COUNTRY_DETAILS_AFRICA_OCEANIA
from data.countries_data_extra import COUNTRY_DETAILS_EXTRA
from data.countries_data_africa_extra import COUNTRY_DETAILS_AFRICA_EXTRA
from data.countries_data_africa_extra_2 import COUNTRY_DETAILS_AFRICA_EXTRA_2
from data.countries_data_americas_extra import COUNTRY_DETAILS_AMERICAS_EXTRA
from data.countries_data_oceania_extra import COUNTRY_DETAILS_OCEANIA_EXTRA
from data.countries_data_caribbean_extra import COUNTRY_DETAILS_CARIBBEAN_EXTRA
from data.countries_data_territories_1 import COUNTRY_DETAILS_TERRITORIES_1
from data.countries_data_territories_2 import COUNTRY_DETAILS_TERRITORIES_2
# image_url 由独立脚本 fetch_wiki_images.py 写入, seed_data 不再触碰该字段


# 合并所有详情
ALL_DETAILS = {}
for d in (
    COUNTRY_DETAILS_EU1,
    COUNTRY_DETAILS_EU2,
    COUNTRY_DETAILS_ASIA,
    COUNTRY_DETAILS_AMERICAS,
    COUNTRY_DETAILS_AFRICA_OCEANIA,
    COUNTRY_DETAILS_EXTRA,
    COUNTRY_DETAILS_AFRICA_EXTRA,
    COUNTRY_DETAILS_AFRICA_EXTRA_2,
    COUNTRY_DETAILS_AMERICAS_EXTRA,
    COUNTRY_DETAILS_OCEANIA_EXTRA,
    COUNTRY_DETAILS_CARIBBEAN_EXTRA,
    COUNTRY_DETAILS_TERRITORIES_1,
    COUNTRY_DETAILS_TERRITORIES_2,
):
    ALL_DETAILS.update(d)


# 全球扩展国家的基础字段 (name -> capital, language, currency, description)
# 这些是 100+ 编号的新国家, 数据库初次构建时需要先 INSERT 这些基础信息
NEW_COUNTRY_BASICS = {
    '巴基斯坦':       ('伊斯兰堡', '乌尔都语、英语', '巴基斯坦卢比', '南亚伊斯兰共和国，印度河文明发源地，K2山与喀喇昆仑山脉所在'),
    '阿富汗':         ('喀布尔', '普什图语、达里语', '阿富汗尼', '中亚内陆国，"帝国坟场"，丝路要冲，巴米扬大佛遗址'),
    '伊朗':           ('德黑兰', '波斯语', '伊朗里亚尔', '波斯文明古国，什叶派伊斯兰共和国，伊斯法罕与设拉子古都'),
    '伊拉克':         ('巴格达', '阿拉伯语、库尔德语', '伊拉克第纳尔', '两河流域文明摇篮，巴比伦古城与底格里斯-幼发拉底河'),
    '叙利亚':         ('大马士革', '阿拉伯语', '叙利亚镑', '世界最古老持续居住城市之一，倭马亚王朝古都，2024政权更迭'),
    '黎巴嫩':         ('贝鲁特', '阿拉伯语、法语', '黎巴嫩镑', '腓尼基字母发源地，"中东巴黎"，雪松与马龙派基督教文化'),
    '约旦':           ('安曼', '阿拉伯语', '约旦第纳尔', '哈希姆王国，佩特拉古城所在地，死海与瓦迪拉姆沙漠'),
    '巴勒斯坦':       ('东耶路撒冷', '阿拉伯语', '以色列谢克尔', '联合国观察员国，包含西岸与加沙地带，伯利恒与耶利哥古城'),
    '卡塔尔':         ('多哈', '阿拉伯语', '卡塔尔里亚尔', '海湾天然气富国，2022世界杯东道主，半岛电视台总部'),
    '巴林':           ('麦纳麦', '阿拉伯语', '巴林第纳尔', '海湾岛国，古Dilmun文明，F1赛车与珍珠采集传统'),
    '科威特':         ('科威特城', '阿拉伯语', '科威特第纳尔', '海湾石油富国，1990海湾战争主要事件地，议会民主'),
    '阿曼':           ('马斯喀特', '阿拉伯语', '阿曼里亚尔', '阿拉伯半岛东南端，乳香之路，伊巴德派伊斯兰国家'),
    '也门':           ('萨那', '阿拉伯语', '也门里亚尔', '阿拉伯半岛南端，示巴女王故乡，泥砖塔楼老城与索科特拉岛'),
    '不丹':           ('廷布', '宗喀语', '努尔特鲁姆', '喜马拉雅佛教王国，世界唯一碳负国，国民幸福总值GNH'),
    '孟加拉国':       ('达卡', '孟加拉语', '孟加拉塔卡', '南亚季风三角洲国，世界第八人口大国，孙德尔本斯红树林'),
    '马尔代夫':       ('马累', '迪维希语', '马尔代夫拉菲亚', '印度洋珊瑚岛国，世界最低国家，奢华海岛度假胜地'),
    '文莱':           ('斯里巴加湾市', '马来语', '文莱元', '婆罗洲北部小国，石油富国，伊斯兰君主制'),
    '东帝汶':         ('帝力', '德顿语、葡萄牙语', '美元', '东南亚最年轻国家，前葡萄牙殖民地，天主教与咖啡之国'),
    '吉尔吉斯斯坦':   ('比什凯克', '吉尔吉斯语、俄语', '吉尔吉斯索姆', '中亚天山游牧国，伊塞克湖与帕米尔山脉，Manas史诗故乡'),
    '塔吉克斯坦':     ('杜尚别', '塔吉克语', '塔吉克索莫尼', '中亚最贫但最美山地国，帕米尔高原"世界屋脊"'),
    '土库曼斯坦':     ('阿什哈巴德', '土库曼语', '土库曼马纳特', '中亚封闭沙漠国，永久中立，"地狱之门"火坑与白色大理石城'),
    '乌兹别克斯坦':   ('塔什干', '乌兹别克语', '乌兹别克索姆', '中亚丝路核心，撒马尔罕/布哈拉/希瓦三大世界遗产古城'),
    '朝鲜':           ('平壤', '朝鲜语', '朝鲜圆', '东亚朝鲜半岛北部国家，主体思想，最封闭国家之一'),
    # ==================== 非洲扩展 43 国 ====================
    '阿尔及利亚':     ('阿尔及尔', '阿拉伯语、柏柏尔语、法语', '阿尔及利亚第纳尔', '北非地中海大国，非洲面积最大国，撒哈拉沙漠+柏柏尔文化'),
    '突尼斯':         ('突尼斯城', '阿拉伯语、法语', '突尼斯第纳尔', '北非地中海小国，迦太基古城+茉莉花革命发源地'),
    '利比亚':         ('的黎波里', '阿拉伯语', '利比亚第纳尔', '北非地中海产油国，撒哈拉与罗马遗址，2011卡扎菲倒台后内战'),
    '苏丹':           ('喀土穆', '阿拉伯语、英语', '苏丹镑', '东北非内陆大国，古努比亚文明+尼罗河汇流地'),
    '南苏丹':         ('朱巴', '英语', '南苏丹镑', '世界最年轻主权国（2011），白尼罗河+Sudd湿地+Dinka文化'),
    '厄立特里亚':     ('阿斯马拉', '提格雷尼亚语、阿拉伯语、英语', '厄立特里亚纳克法', '红海沿岸国，前意属东非殖民地，"非洲北朝鲜"封闭独裁'),
    '吉布提':         ('吉布提市', '法语、阿拉伯语', '吉布提法郎', '东非小国，曼德海峡门户，全球各大国军事基地最集中地'),
    '索马里':         ('摩加迪沙', '索马里语、阿拉伯语', '索马里先令', '非洲之角"诗人之国"，1991内战至今分裂，海盗与Al-Shabaab问题'),
    '乌干达':         ('坎帕拉', '英语、斯瓦希里语', '乌干达先令', '东非高原"非洲明珠"，山地大猩猩+维多利亚湖+白尼罗河源'),
    '布隆迪':         ('基特加', '基隆迪语、法语、英语', '布隆迪法郎', '东非小国，胡图-图西冲突与皇家鼓乐手非遗，坦噶尼喀湖畔'),
    '刚果民主共和国': ('金沙萨', '法语、林加拉语', '刚果法郎', '非洲第二大国，刚果河+热带雨林+矿产，"非洲世界大战"创伤'),
    '刚果共和国':     ('布拉柴维尔', '法语、林加拉语', '中非法郎', '刚果河北岸法语小国，Rumba音乐+Sapeurs绅士亚文化+石油'),
    '中非':           ('班吉', '法语、桑戈语', '中非法郎', '中非内陆贫国，BaAka俾格米人+Sangha雨林+宗教冲突'),
    '喀麦隆':         ('雅温得', '法语、英语', '中非法郎', '"非洲缩影"，250部族法英双官方，足球+Mount Cameroon活火山'),
    '加蓬':           ('利伯维尔', '法语', '中非法郎', '中非赤道森林国，石油富而少人，世界第二碳吸收国'),
    '赤道几内亚':     ('马拉博', '西班牙语、法语、葡萄牙语', '中非法郎', '中非小国，唯一西班牙语非洲国，石油暴富+Obiang独裁45年'),
    '圣多美和普林西比': ('圣多美', '葡萄牙语', '圣多美多布拉', '几内亚湾岛国，赤道穿越，可可咖啡+葡式克里奥尔文化'),
    '安哥拉':         ('罗安达', '葡萄牙语', '安哥拉宽扎', '南部非洲产油大国，27年内战+葡萄牙殖民遗产+Semba舞起源'),
    '赞比亚':         ('卢萨卡', '英语', '赞比亚克瓦查', '南部非洲铜矿国，维多利亚瀑布+Luangwa游猎+Kuomboka洪水节'),
    '马拉维':         ('利隆圭', '英语、奇切瓦语', '马拉维克瓦查', '"温暖之心非洲"，马拉维湖+Cichlid慈鲷鱼+Gule Wamkulu面具舞'),
    '莫桑比克':       ('马普托', '葡萄牙语', '莫桑比克梅蒂卡尔', '印度洋长海岸线国，葡式殖民+Bazaruto岛+Marrabenta音乐'),
    '博茨瓦纳':       ('哈博罗内', '英语、茨瓦纳语', '博茨瓦纳普拉', '南部非洲钻石稳定民主国，Okavango三角洲+卡拉哈里沙漠+San人'),
    '纳米比亚':       ('温得和克', '英语', '纳米比亚元、南非兰特', '西南非沙漠国，Sossusvlei红沙丘+德国殖民遗产+骷髅海岸'),
    '莱索托':         ('马塞卢', '塞索托语、英语', '莱索托洛蒂', '"非洲屋脊"高原国，南非完全包围，Basotho毛毯+尖顶草帽'),
    '斯威士兰':       ('姆巴巴内', '斯瓦蒂语、英语', '埃马兰吉尼', '南部非洲绝对君主小国，Umhlanga芦苇节+Incwala国王仪式'),
    '科摩罗':         ('莫罗尼', '科摩罗语、阿拉伯语、法语', '科摩罗法郎', '印度洋香料群岛国，依朗依朗+丁香+19次政变历史'),
    '毛里求斯':       ('路易港', '英语、法语、克里奥尔语', '毛里求斯卢比', '印度洋多元文化富国，Dodo鸟+Sega舞+印中法克里奥尔融合'),
    '塞舌尔':         ('维多利亚', '塞舌尔克里奥尔语、英语、法语', '塞舌尔卢比', '印度洋珊瑚岛国，Coco de Mer双椰子+巨陆龟+人均GDP非洲最高之一'),
    '佛得角':         ('普拉亚', '葡萄牙语', '佛得角埃斯库多', '大西洋火山岛国，Morna音乐（Cesária Évora）+葡式克里奥尔文化'),
    '几内亚比绍':     ('比绍', '葡萄牙语', '中非法郎', '西非葡语小国，Bijagós母系群岛+Cabral独立运动+毒品中转'),
    '几内亚':         ('科纳克里', '法语', '几内亚法郎', '西非"水塔"，Fouta Djallon高原+全球最大铝土矿+Mande文化摇篮'),
    '塞拉利昂':       ('弗里敦', '英语', '塞拉利昂利昂', '"狮山"，前英属解放奴隶定居地，2002钻石内战创伤+埃博拉'),
    '利比里亚':       ('蒙罗维亚', '英语', '利比里亚元', '美国解放奴隶建国（1847），非洲第一独立黑人共和国+Charles Taylor战乱'),
    '科特迪瓦':       ('亚穆苏克罗', '法语', '中非法郎', '"象牙海岸"，世界可可+腰果第一出口国，亚穆苏克罗巨型大教堂'),
    '多哥':           ('洛美', '法语', '中非法郎', '西非细长小国，伏都教文化区+Tata泥砖塔楼+Eyadéma父子王朝'),
    '贝宁':           ('波多诺伏', '法语', '中非法郎', '伏都教Vodoun发源地（传到海地），达荷美王朝+女战士Amazon'),
    '布基纳法索':     ('瓦加杜古', '法语', '中非法郎', '"廉洁人民之地"，Mossi帝国+FESPACO泛非电影节+Sankara遗产'),
    '马里':           ('巴马科', '法语', '中非法郎', '古马里帝国+桑海帝国，Timbuktu传奇沙漠学城+Mali Music音乐宝库'),
    '尼日尔':         ('尼亚美', '法语', '中非法郎', 'Sahel内陆国，世界最贫之一，铀矿大国+Tuareg蓝人+Wodaabe男选美'),
    '乍得':           ('恩贾梅纳', '法语、阿拉伯语', '中非法郎', '中非Sahel国，乍得湖+Tibesti山+Ennedi岩画+南北宗教族裔分裂'),
    '毛里塔尼亚':     ('努瓦克肖特', '阿拉伯语、法语', '毛里塔尼亚乌吉亚', 'Sahel伊斯兰共和国，Chinguetti沙漠学城+绿茶三杯仪式+撒哈拉之眼'),
    '塞内加尔':       ('达喀尔', '法语', '中非法郎', '"非洲西门"，戈雷岛奴隶港+Touba穆里德苏菲圣城+Mbalax音乐'),
    '冈比亚':         ('班珠尔', '英语', '冈比亚达拉西', '非洲大陆最小国（细如冈比亚河条状），《根》Kunta Kinte故乡'),
    # ==================== 美洲扩展 14 国 ====================
    '危地马拉':           ('危地马拉城', '西班牙语、玛雅语', '格查尔', '中美洲玛雅文明核心区，Tikal+Antigua世界遗产，火山链与玛雅原住民文化'),
    '伯利兹':             ('贝尔莫潘', '英语、克里奥尔语', '伯利兹元', '中美洲唯一英语国，大蓝洞潜水+世界遗产珊瑚礁+玛雅遗址+Garifuna文化'),
    '萨尔瓦多':           ('圣萨尔瓦多', '西班牙语', '美元', '中美洲最小最密国，Pupusa国菜+Bukele比特币法币+反帮派"超级监狱"'),
    '洪都拉斯':           ('特古西加尔巴', '西班牙语', '伦皮拉', '"香蕉共和国"原型，玛雅Copán遗址+Roatán加勒比潜水+移民潮源'),
    '尼加拉瓜':           ('马那瓜', '西班牙语', '科多巴', '中美洲最大湖之国，殖民古城Granada+León+Ometepe双火山岛+Sandinista革命'),
    '哥斯达黎加':         ('圣何塞', '西班牙语', '哥斯达黎加科朗', '"中美瑞士"，废军1948+95%可再生能源+Pura Vida生活哲学+生态旅游标杆'),
    '巴拿马':             ('巴拿马城', '西班牙语', '巴拿马巴波亚、美元', '巴拿马运河+Casco Viejo世界遗产+Guna Yala原住民+San Blas群岛'),
    '海地':               ('太子港', '法语、海地克里奥尔语', '海地古德', '世界第一黑人独立国（1804），Citadelle Laferrière世界遗产+伏都教+多灾'),
    '多米尼加':           ('圣多明各', '西班牙语', '多米尼加比索', '新世界第一城（1496），Merengue+Bachata音乐发源+棒球大国+加勒比海滩'),
    '牙买加':             ('金斯敦', '英语、Patois克里奥尔语', '牙买加元', '雷鬼Reggae发源地+Bob Marley+蓝山咖啡+Usain Bolt短跑王国+拉斯塔法里教'),
    '巴哈马':             ('拿骚', '英语', '巴哈马元', '加勒比700岛国+Pig Beach游泳猪+Atlantis度假村+Junkanoo大游行+蓝洞潜水'),
    '特立尼达和多巴哥':   ('西班牙港', '英语', '特立尼达和多巴哥元', 'Steelpan钢鼓+Carnival嘉年华+石油富国+印裔+非裔+加勒比共同体'),
    '圭亚那':             ('乔治敦', '英语', '圭亚那元', '南美唯一英语国+Kaieteur最高瀑布+石油新富+9部族原住民+印度教+伊斯兰多元'),
    '苏里南':             ('帕拉马里博', '荷兰语、Sranan Tongo', '苏里南元', '南美最小+唯一荷兰语国，世界遗产殖民木建筑+印度+爪哇+非洲+原住民多元'),
    # ==================== 大洋洲扩展 10 国 + 极地 2 ====================
    '所罗门群岛':         ('霍尼亚拉', '英语、Pijin皮钦语', '所罗门群岛元', '美拉尼西亚岛国，二战瓜岛血战转折点+Marovo潟湖+Wantok互助传统'),
    '瓦努阿图':           ('维拉港', 'Bislama克里奥尔语、英语、法语', '瓦图', '美拉尼西亚83岛国，蹦极发源地（Pentecost跳塔）+Yasur活火山+Kava仪式'),
    '萨摩亚':             ('阿皮亚', '萨摩亚语、英语', '塔拉', '波利尼西亚太平洋第一独立国（1962），Pe\'a纹身+橄榄球大国+教堂密度世界最高'),
    '汤加':               ('努库阿洛法', '汤加语、英语', '潘加', '唯一从未被欧洲全殖民的太平洋国+最古君主制+鲸观察+Tu\'i Tonga古帝国遗产'),
    '基里巴斯':           ('塔拉瓦', '吉尔伯特语、英语', '澳元', '密克罗尼西亚33岛跨3500公里3时区+赤道+国际日期线+气候难民头号目标'),
    '密克罗尼西亚联邦':   ('帕利基尔', '英语+八种本土语', '美元', '607岛跨大洋+Nan Madol水上王城世界遗产+Yap石币+Chuuk沉船潜水'),
    '马绍尔群岛':         ('马朱罗', '马绍尔语、英语', '美元', '密克罗尼西亚环礁国，Bikini核试场（67次）+海平面上升存亡危机+Stick chart导航'),
    '帕劳':               ('恩格鲁尔穆德', 'Palauan、英语', '美元', '密克罗尼西亚-马来岛国，Rock Islands世界遗产+Jellyfish Lake水母湖+反核宪法'),
    '瑙鲁':               ('亚伦', '瑙鲁语、英语', '澳元', '世界第三小国+前磷矿暴富后破产+今澳难民拘留+全球最高肥胖率'),
    '图瓦卢':             ('富纳富提', '图瓦卢语、英语', '澳元、图瓦卢元', '世界第四小国+海拔最低+气候难民头号目标+建立"数字双胞胎国"应对沉没'),
    '南极洲':             ('Amundsen–Scott基地', '科考多语', '无', '地球最冷+最干+最大风之大陆，54国《南极条约》冻结主权+无原住民+无政府'),
    '北极地区':           ('Longyearbyen', '多语（含因纽特+萨米+俄+英+北欧语）', '多种', '8国领土+北冰洋海域，Inuit+Sami等原住民数千年定居+气候最敏感区+航道开通争夺'),
    # ==================== 加勒比小安的列斯 7 国 ====================
    '安提瓜和巴布达':       ('圣约翰', '英语、Antiguan Creole', '东加勒比元', '加勒比365海滩岛国，Nelson船坞世界遗产+Carnival嘉年华+板球大国'),
    '多米尼克':             ('罗索', '英语、Kwéyòl', '东加勒比元', '"自然之岛"，沸湖+Morne Trois Pitons世界遗产+加勒比唯一Kalinago原住民保留地'),
    '格林纳达':             ('圣乔治', '英语、Grenadian Creole', '东加勒比元', '"香料之岛"豆蔻+丁香+肉桂，1983美军入侵+水下雕塑公园'),
    '圣基茨和尼维斯':       ('巴斯特尔', '英语、St. Kitts Creole', '东加勒比元', '西半球最小独立国+Brimstone Hill硫磺山要塞世界遗产+Hamilton出生地'),
    '圣卢西亚':             ('卡斯特里', '英语、Kwéyòl', '东加勒比元', 'Pitons双火山峰世界遗产+drive-in volcano+人均诺贝尔奖比例世界最高'),
    '圣文森特和格林纳丁斯': ('金斯敦', '英语、Vincentian Creole', '东加勒比元', '32岛国+La Soufrière 2021喷发+Tobago Cays珊瑚礁+Garifuna黑人原住民起源'),
    '巴巴多斯':             ('布里奇敦', '英语、Bajan Creole', '巴巴多斯元', 'Crop Over嘉年华+Rihanna国家英雄+2021废君主成共和国+Mount Gay最古朗姆厂'),
    # ==================== 海外属地与非主权区 16 ====================
    '格陵兰':         ('努克', '格陵兰语、丹麦语', '丹麦克朗', '世界最大岛屿，丹麦自治区，冰盖+Inuit文化+伊卢利萨特冰峡湾世界遗产'),
    '法罗群岛':       ('托尔斯港', '法罗语、丹麦语', '法罗克朗、丹麦克朗', '丹麦自治区，北大西洋18岛+维京文化+草顶教堂+Mulafossur瀑布'),
    '法属波利尼西亚': ('帕皮提', '法语、塔希提语', '太平洋法郎', '法国海外集体，塔希提+波拉波拉+118岛+黑珍珠+水上别墅'),
    '新喀里多尼亚':   ('努美阿', '法语', '太平洋法郎', '法国特殊集体，世界第二大珊瑚礁+Kanak原住民+镍矿'),
    '关岛':           ('哈加特纳', '英语、Chamorro语', '美元', '美国未合并领土，西太平洋战略要冲+Chamorro文化+二战遗址'),
    '库克群岛':       ('阿瓦鲁阿', '英语、库克毛利语', '新西兰元', '与新西兰自由联合，15岛波利尼西亚+Aitutaki世界最美泻湖之一'),
    '直布罗陀':       ('直布罗陀城', '英语、西班牙语', '直布罗陀镑', '英国海外领土，地中海要塞+巨岩+欧洲唯一野生猴群+Brexit边界'),
    '波多黎各':       ('圣胡安', '西班牙语、英语', '美元', '美国自由联系邦，加勒比+老城世界遗产+生物发光湾+雷鬼顿发源地'),
    '库拉索':         ('威廉斯塔德', '荷兰语、Papiamentu语、英语', '加勒比荷兰盾', '荷兰王国构成国，威廉斯塔德彩色港城世界遗产+橙皮酒'),
    '阿鲁巴':         ('奥拉涅斯塔德', '荷兰语、Papiamento语', '阿鲁巴弗罗林', '荷兰王国构成国，"One Happy Island"+Eagle Beach+无飓风加勒比'),
    '马提尼克':       ('法兰西堡', '法语、马提尼克克里奥尔语', '欧元', '法国海外省，加勒比火山岛+1902 Mt. Pelée毁城+Zouk音乐发源地'),
    '百慕大':         ('汉密尔顿', '英语', '百慕大元', '英国海外领土，北大西洋粉红沙滩+百慕大三角+离岸金融中心'),
    '留尼汪':         ('圣丹尼', '法语', '欧元', '法国海外省，印度洋火山岛+Cirques三冰斗世界遗产+多元文化融合'),
    '马约特':         ('马穆楚', '法语', '欧元', '法国海外省，印度洋伊斯兰岛屿+世界最大封闭泻湖+科摩罗争议主权'),
    '法属圭亚那':     ('凯宴', '法语', '欧元', '法国海外省，南美洲飞地+亚马逊雨林+欧空局火箭发射场+恶魔岛流放营'),
    '福克兰群岛':     ('斯坦利', '英语', '福克兰镑', '英国海外领土，南大西洋企鹅天堂+1982阿福战争+羊比人多120倍'),
}


# 需要补充到 countries 表的新列（列名 -> SQL 类型）
NEW_COLUMNS = [
    ("climate", "TEXT"),
    ("festivals", "TEXT"),
    ("attractions", "TEXT"),
    ("history", "TEXT"),
    ("cuisine", "TEXT"),
    ("culture", "TEXT"),
    ("population", "VARCHAR"),
    ("area", "VARCHAR"),
    ("timezone", "VARCHAR"),
    ("religion", "VARCHAR"),
]


def migrate_schema():
    """安全地为已有 countries 表新增列；创建 cities 表（如不存在）。"""
    inspector = inspect(engine)
    existing_cols = {c["name"] for c in inspector.get_columns("countries")}

    with engine.begin() as conn:
        for col_name, col_type in NEW_COLUMNS:
            if col_name not in existing_cols:
                print(f"  [+] countries 新增列 {col_name} {col_type}")
                conn.execute(text(f"ALTER TABLE countries ADD COLUMN {col_name} {col_type}"))
            else:
                print(f"  [=] countries 已有列 {col_name}，跳过")

    # 创建 cities 表（Base.metadata 会跳过已存在的表）
    Base.metadata.create_all(bind=engine)
    print("  [+] 已确保 cities 表存在")


def seed_details():
    db = SessionLocal()
    try:
        # ---- 阶段 0：自动创建数据库中尚不存在的扩展国家（NEW_COUNTRY_BASICS） ----
        created_new = 0
        for cn_name, (capital, language, currency, description) in NEW_COUNTRY_BASICS.items():
            exists = db.query(Country).filter(Country.name == cn_name).first()
            if not exists:
                new_country = Country(
                    name=cn_name,
                    capital=capital,
                    language=language,
                    currency=currency,
                    description=description,
                )
                db.add(new_country)
                created_new += 1
        if created_new:
            db.commit()
            print(f"  [+] 自动创建 {created_new} 个扩展国家的基础记录")

        total_countries = 0
        total_cities = 0
        not_found = []

        for cn_name, detail in ALL_DETAILS.items():
            country = db.query(Country).filter(Country.name == cn_name).first()
            if not country:
                not_found.append(cn_name)
                continue

            # 写入详情字段
            country.climate = detail.get("climate", "")
            country.festivals = detail.get("festivals", "")
            country.attractions = detail.get("attractions", "")
            country.history = detail.get("history", "")
            country.cuisine = detail.get("cuisine", "")
            country.culture = detail.get("culture", "")
            country.population = detail.get("population", "")
            country.area = detail.get("area", "")
            country.timezone = detail.get("timezone", "")
            country.religion = detail.get("religion", "")
            # 注意: image_url 字段由独立的 fetch_wiki_images.py 脚本管理,
            # seed_data 不动该字段, 重复运行也不会覆盖已写入的图片 URL.

            # 清空原有城市（重复执行脚本时保持幂等）
            db.query(City).filter(City.country_id == country.id).delete()

            # 插入城市
            for city_tuple in detail.get("cities", []):
                name_cn, name_en, lat, lng, is_cap, desc = city_tuple
                city = City(
                    country_id=country.id,
                    name=name_cn,
                    name_en=name_en,
                    latitude=str(lat),
                    longitude=str(lng),
                    is_capital=int(is_cap),
                    description=desc,
                )
                db.add(city)
                total_cities += 1

            total_countries += 1

        db.commit()
        print(f"\n  [√] 已更新 {total_countries} 个国家详情")
        print(f"  [√] 已写入 {total_cities} 个城市记录")
        if not_found:
            print(f"\n  [!] 以下国家在数据库中未找到（请检查名称是否一致）：")
            for n in not_found:
                print(f"      - {n}")
    finally:
        db.close()


def main():
    print("=" * 60)
    print("Atlas Mundi 数据迁移与种子脚本")
    print("=" * 60)

    print("\n[1/2] 数据库结构迁移")
    migrate_schema()

    print("\n[2/2] 写入国家详情与城市数据")
    seed_details()

    print("\n[完成] 寰宇图鉴已就绪，可启动 uvicorn main:app --reload")


if __name__ == "__main__":
    main()
