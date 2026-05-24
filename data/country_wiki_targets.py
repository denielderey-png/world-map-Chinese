"""
99 国 -> 英文 Wikipedia 词条名映射。

工作原理:
  fetch_wiki_images.py 把每个词条名传给 Wikipedia REST API:
    https://en.wikipedia.org/api/rest_v1/page/summary/{title}
  API 返回的 JSON 里 thumbnail.source 字段就是该词条主图的 URL.
  这个 URL 直接可在 <img> 标签里使用.

选词条原则:
  1. 优先具体地标词条 (Eiffel_Tower) > 国名词条 (France)
     因为国名词条主图常是地图/国徽, 地标词条主图通常是该地标本身
  2. 选 Wikipedia 上"该国最有名"的地标
  3. 词条名用英文形式 (URL safe), 空格用下划线

字段: '国名(中文)' -> ('Wikipedia词条名(英文)', '中文地标说明')
"""

COUNTRY_WIKI_TARGETS = {
    # ========== 欧洲 ==========
    '法国':   ('Eiffel_Tower',                      '埃菲尔铁塔'),
    '意大利': ('Colosseum',                         '罗马斗兽场'),
    '西班牙': ('Sagrada_Família',                   '圣家堂'),
    '德国':   ('Neuschwanstein_Castle',             '新天鹅堡'),
    '英国':   ('Big_Ben',                           '大本钟'),
    '葡萄牙': ('Belém_Tower',                       '贝伦塔'),
    '荷兰':   ('Kinderdijk',                        '小孩堤防风车群'),
    '比利时': ('Grand-Place',                       '布鲁塞尔大广场'),
    '瑞士':   ('Matterhorn',                        '马特洪峰'),
    '奥地利': ('Schönbrunn_Palace',                 '美泉宫'),
    '希腊':   ('Acropolis_of_Athens',               '雅典卫城'),
    '瑞典':   ('Stockholm_City_Hall',               '斯德哥尔摩市政厅'),
    '挪威':   ('Geirangerfjord',                    '盖朗厄尔峡湾'),
    '丹麦':   ('Nyhavn',                            '哥本哈根新港'),
    '芬兰':   ('Helsinki_Cathedral',                '赫尔辛基大教堂'),
    '冰岛':   ('Seljalandsfoss',                    '塞里雅兰瀑布'),
    '爱尔兰': ('Cliffs_of_Moher',                   '莫赫悬崖'),
    '波兰':   ('Wawel_Castle',                      '瓦维尔城堡'),
    '捷克':   ('Charles_Bridge',                    '布拉格查理大桥'),
    '匈牙利': ('Hungarian_Parliament_Building',     '匈牙利国会大厦'),
    '罗马尼亚': ('Bran_Castle',                     '布朗城堡(德古拉城堡)'),
    '保加利亚': ('Rila_Monastery',                  '里拉修道院'),
    '克罗地亚': ('Plitvice_Lakes_National_Park',    '十六湖国家公园'),
    '斯洛文尼亚': ('Lake_Bled',                     '布莱德湖'),
    '斯洛伐克': ('Bratislava_Castle',               '布拉迪斯拉发城堡'),
    '乌克兰': ('Saint_Sophia_Cathedral,_Kyiv',      '基辅圣索菲亚大教堂'),
    '白俄罗斯': ('Mir_Castle_Complex',              '米尔城堡'),
    '立陶宛': ('Trakai_Island_Castle',              '特拉凯水中城堡'),
    '拉脱维亚': ('House_of_the_Black_Heads',        '里加黑头宫'),
    '爱沙尼亚': ('Old_Town_of_Tallinn',             '塔林老城'),
    '塞尔维亚': ('Belgrade_Fortress',               '贝尔格莱德要塞'),
    '黑山':   ('Bay_of_Kotor',                      '科托尔湾'),
    '波斯尼亚和黑塞哥维那': ('Stari_Most',          '莫斯塔尔老桥'),
    '阿尔巴尼亚': ('Berat',                         '培拉特古城'),
    '北马其顿': ('Lake_Ohrid',                      '奥赫里德湖'),
    '科索沃': ('Gračanica_Monastery',               '格拉查尼察修道院'),
    '摩尔多瓦': ('Orheiul_Vechi',                   '老奥尔黑修道院'),
    '卢森堡': ('Vianden_Castle',                    '维安登城堡'),
    '列支敦士登': ('Vaduz_Castle',                  '瓦杜兹城堡'),
    '摩纳哥': ('Monte_Carlo_Casino',                '蒙特卡洛赌场'),
    '安道尔': ('Casa_de_la_Vall',                   '安道尔议会大厅'),
    '圣马力诺': ('Guaita',                          '瓜伊塔塔楼'),
    '梵蒂冈': ("St._Peter's_Basilica",              '圣彼得大教堂'),
    '马耳他': ('Valletta',                          '瓦莱塔'),
    '塞浦路斯': ('Kyrenia_Castle',                  '凯里尼亚城堡'),
    
    # ========== 亚洲 ==========
    '俄罗斯': ('Saint_Basil%27s_Cathedral',         '圣瓦西里大教堂'),
    '土耳其': ('Hagia_Sophia',                      '圣索菲亚大教堂'),
    '中国':   ('Great_Wall_of_China',               '万里长城'),
    '日本':   ('Mount_Fuji',                        '富士山'),
    '韩国':   ('Gyeongbokgung',                     '景福宫'),
    '印度':   ('Taj_Mahal',                         '泰姬陵'),
    '泰国':   ('Wat_Arun',                          '郑王庙'),
    '越南':   ('Hạ_Long_Bay',                       '下龙湾'),
    '印度尼西亚': ('Borobudur',                     '婆罗浮屠'),
    '马来西亚': ('Petronas_Towers',                 '吉隆坡双子塔'),
    '新加坡': ('Marina_Bay_Sands',                  '滨海湾金沙'),
    '菲律宾': ('Chocolate_Hills',                   '巧克力山'),
    '阿联酋': ('Burj_Khalifa',                      '哈利法塔'),
    '沙特阿拉伯': ('Al-Masjid_an-Nabawi',           '先知清真寺'),
    '以色列': ('Western_Wall',                      '哭墙'),
    '哈萨克斯坦': ('Bayterek_Tower',                '生命之树观景塔'),
    '格鲁吉亚': ('Gergeti_Trinity_Church',          '格尔盖蒂圣三一教堂'),
    '亚美尼亚': ('Khor_Virap',                      '霍尔维拉普修道院(亚拉腊山)'),
    '阿塞拜疆': ('Flame_Towers',                    '巴库火焰塔'),
    '尼泊尔': ('Mount_Everest',                     '珠穆朗玛峰'),
    '斯里兰卡': ('Sigiriya',                        '狮子岩'),
    '蒙古':   ('Erdene_Zuu_Monastery',              '额尔德尼召寺'),
    '缅甸':   ('Shwedagon_Pagoda',                  '仰光大金塔'),
    '柬埔寨': ('Angkor_Wat',                        '吴哥窟'),
    '老挝':   ('Pha_That_Luang',                    '塔銮大金塔'),
    
    # ========== 美洲 ==========
    '美国':   ('Statue_of_Liberty',                 '自由女神像'),
    '加拿大': ('Moraine_Lake',                      '梦莲湖'),
    '墨西哥': ('Chichen_Itza',                      '奇琴伊察金字塔'),
    '巴西':   ('Christ_the_Redeemer_(statue)',      '救世基督像'),
    '阿根廷': ('Perito_Moreno_Glacier',             '佩里托莫雷诺冰川'),
    '秘鲁':   ('Machu_Picchu',                      '马丘比丘'),
    '哥伦比亚': ('Cartagena,_Colombia',             '卡塔赫纳古城'),
    '智利':   ('Torres_del_Paine_National_Park',    '百内国家公园'),
    '古巴':   ('Old_Havana',                        '哈瓦那老城'),
    '委内瑞拉': ('Angel_Falls',                     '安赫尔瀑布'),
    '厄瓜多尔': ('Galápagos_Islands',               '加拉帕戈斯群岛'),
    '玻利维亚': ('Salar_de_Uyuni',                  '乌尤尼盐沼'),
    '巴拉圭': ('Iguazu_Falls',                      '伊瓜苏瀑布'),
    '乌拉圭': ('Punta_del_Este',                    '埃斯特角城'),
    
    # ========== 非洲 ==========
    '埃及':   ('Great_Pyramid_of_Giza',             '吉萨大金字塔'),
    '摩洛哥': ('Jemaa_el-Fnaa',                     '马拉喀什德吉玛广场'),
    '南非':   ('Table_Mountain',                    '开普敦桌山'),
    '肯尼亚': ('Maasai_Mara',                       '马赛马拉自然保护区'),
    '坦桑尼亚': ('Mount_Kilimanjaro',               '乞力马扎罗山'),
    '埃塞俄比亚': ('Rock-Hewn_Churches,_Lalibela',  '拉利贝拉岩石教堂'),
    '加纳':   ('Cape_Coast_Castle',                 '海岸角城堡'),
    '尼日利亚': ('Zuma_Rock',                       '祖玛岩'),
    '马达加斯加': ('Avenue_of_the_Baobabs',         '猴面包树大道'),
    '津巴布韦': ('Victoria_Falls',                  '维多利亚瀑布'),
    '卢旺达': ('Volcanoes_National_Park,_Rwanda',   '火山国家公园'),
    
    # ========== 大洋洲 ==========
    '澳大利亚': ('Sydney_Opera_House',              '悉尼歌剧院'),
    '新西兰':   ('Milford_Sound',                   '米尔福德峡湾'),
    '巴布亚新几内亚': ('Mount_Wilhelm',             '威廉山'),
    '斐济':     ('Mamanuca_Islands',                '玛玛努卡群岛'),
}

assert len(COUNTRY_WIKI_TARGETS) == 99, f'应有99国, 实际 {len(COUNTRY_WIKI_TARGETS)}'

if __name__ == '__main__':
    print(f'共 {len(COUNTRY_WIKI_TARGETS)} 国')
    titles = [v[0] for v in COUNTRY_WIKI_TARGETS.values()]
    if len(titles) != len(set(titles)):
        print('警告: 词条重复')
    else:
        print('校验通过, 无重复词条')
