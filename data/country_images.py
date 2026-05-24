"""
99 国 -> Unsplash 地标照片映射。

每条 photo ID 都从 unsplash.com 详情页实际抓取, 三重验证元数据(位置/标签/标题).

URL 模板使用 Unsplash CDN 横屏裁切参数:
  &fit=crop&crop=entropy&w=1600&h=600
确保无论原图竖横, 输出都是 1600x600 横屏图.
"""

COUNTRY_IMAGES = {
    # —— 已实地验证 22 国 (从 unsplash.com 详情页三重验证元数据后写入) ——
    # 欧洲 8 国
    '法国':   ('photo-1743065272129-5e261bad0c46', '埃菲尔铁塔',           'Paris, France'),
    '意大利': ('photo-1555992828-ca4dbe41d294',    '罗马斗兽场 (航拍)',     'aerial drone, Rome, Italy'),
    '西班牙': ('photo-1745186487192-09eccb385169', '圣家堂',               'Barcelona, Spain'),
    '德国':   ('photo-1679254877059-09e01f2cd0f8', '新天鹅堡',             'Neuschwanstein Castle, Germany'),
    '英国':   ('photo-1503566303019-ba141f5f9b76', '伦敦大本钟',           'Westminster, London'),
    '葡萄牙': ('photo-1501415201023-2f45fbcefac0', '里斯本28路黄电车',     'Lisbon, Portugal'),
    '荷兰':   ('photo-1683226661979-59114c07ff29', '小孩堤防风车群',       'Kinderdijk, Netherlands'),
    '瑞士':   ('photo-1531743579253-fa8d52993ba5', '马特洪峰',             'Zermatt, Switzerland'),
    '希腊':   ('photo-1563789031959-4c02bcb41319', '圣托里尼蓝顶教堂',     'Oia, Santorini, Greece'),
    # 亚洲 7 国
    '俄罗斯': ('photo-1513326738677-b964603b136d', '红场圣瓦西里大教堂',   "Moscow, Russia, St Basil's"),
    '土耳其': ('photo-1560856311-69382e596cd4',    '伊斯坦布尔圣索菲亚',   'Istanbul, Turkey, Hagia Sophia'),
    '中国':   ('photo-1508804185872-d7badad00f7d', '万里长城 (秋色)',      'Great Wall of China'),
    '日本':   ('photo-1526481280693-3bfa7568e0f3', '富士山+忠灵塔',        'Fujiyoshida, Japan, Mount Fuji'),
    '印度':   ('photo-1523428461295-92770e70d7ae', '泰姬陵',               'Taj Mahal, Agra, India'),
    '泰国':   ('photo-1568321385520-b9252021b491', '曼谷郑王庙',           'Wat Arun, Bangkok, Thailand'),
    '柬埔寨': ('photo-1504639650150-bf773680d8c3', '吴哥窟 (日出)',        'Angkor Wat, Siem Reap, Cambodia'),
    '阿联酋': ('photo-1748373448914-1d7f882700e2', '迪拜哈利法塔',         'Burj Khalifa, Dubai'),
    # 美洲 4 国
    '美国':   ('photo-1512315342380-81f12a02bd7e', '自由女神像',           'Statue of Liberty, New York'),
    '巴西':   ('photo-1516834611397-8d633eaec5d0', '里约救世基督像',       'Christ The Redeemer, Rio de Janeiro'),
    '秘鲁':   ('photo-1568805746970-0bbae56ab18b', '马丘比丘',             'Machu Picchu, Peru'),
    # 非洲 1 国
    '埃及':   ('photo-1738580426685-f8f0d34291dc', '吉萨金字塔与狮身人面像', 'Sphinx and Pyramids of Giza, Egypt'),
    # 大洋洲 1 国
    '澳大利亚': ('photo-1624138784614-87fd1b6528f8', '悉尼歌剧院 (航拍)',  'Sydney Opera House, Australia'),

    # —— 第二批 14 国 (亚洲剩余 + 欧洲 1, 三重元数据验证) ——
    # 东南亚 7 国
    '越南':       ('photo-1669819894338-53ab7afc6958', '下龙湾',                'Ha Long Bay, Quang Ninh, Vietnam'),
    '印度尼西亚': ('photo-1591674585153-ca78d0339b09', '婆罗浮屠 (日出)',        'Borobudur, Magelang, Central Java, Indonesia'),
    '马来西亚':   ('photo-1666715945700-832656ecf2d0', '吉隆坡双子塔 (夜景)',     'Petronas Twin Towers, Kuala Lumpur, Malaysia'),
    '新加坡':     ('photo-1628221680019-f28a2716e727', '滨海湾金沙',             'Marina Bay Sands, Singapore'),
    '菲律宾':     ('photo-1555590858-be28a58c2688',    '马荣火山 + 古萨瓦遗址',   'Mayon Volcano, Cagsawa Ruins, Legazpi, Philippines'),
    '缅甸':       ('photo-1468336210566-1e743694dc18', '蒲甘古城 + 热气球',       'Old Bagan, Myanmar (Burma)'),
    '老挝':       ('photo-1610426714962-83caa2244105', '琅勃拉邦香通寺',          'Wat Xiengthong, Luang Prabang, Laos'),
    # 南亚 2 国
    '韩国':       ('photo-1566800890932-e89159daf3dc', '首尔景福宫',             'Gyeongbokgung Palace, Seoul, South Korea'),
    '尼泊尔':     ('photo-1623268963489-1e80a6334b9f', '加德满都博达哈大佛塔',     'Boudhanath Stupa, Kathmandu, Nepal'),
    '斯里兰卡':   ('photo-1627895457805-c7bf42cb9873', '锡吉里耶狮子岩',          'Sigiriya Lion Rock, Sri Lanka'),
    # 中亚/西亚 3 国
    '哈萨克斯坦': ('photo-1604269949318-10589797d025', '阿斯塔纳巴伊杰列克塔',     'Bayterek monument, Nur-Sultan (Astana), Kazakhstan'),
    '沙特阿拉伯': ('photo-1742084312070-0a952dff8b8c', '利雅得王国塔',            'Kingdom Tower, Riyadh, Saudi Arabia'),
    '以色列':     ('photo-1618777618311-92f986a6519d', '耶路撒冷圆顶清真寺',       'Dome of the Rock, Old City of Jerusalem, Israel'),
    # 欧洲 1 国
    '比利时':     ('photo-1568471060904-3f623b573607', '布鲁塞尔大广场市政厅',     'Hotel de Ville, Grand Place, Brussels, Belgium'),

    # —— 第三批 9 国 (亚洲扩展, 三重元数据验证) ——
    # 西亚 / 中东 5 国
    '约旦':       ('photo-1551171128-c5b124a4174c', '佩特拉古城卡兹尼宝库',      'Petra Treasury, Petra, Jordan'),
    '伊朗':       ('photo-1624746068623-d3f9c4ce5739', '伊斯法罕清真寺穹顶',       'Mosque dome, Isfahan, Iran'),
    '黎巴嫩':     ('photo-1496823407868-80f47c7453b5', '贝鲁特城市鸟瞰',           'Beirut aerial view, Lebanon'),
    '卡塔尔':     ('photo-1596986343464-332d54fa5702', '多哈滨海大道天际线',       'Al Corniche Street, Doha, Qatar'),
    '阿曼':       ('photo-1715890545305-b6927eeea369', '马斯喀特苏丹卡布斯大清真寺', 'Sultan Qaboos Grand Mosque, Muscat, Oman'),
    # 南亚 3 国
    '巴基斯坦':   ('photo-1514558427911-8e293bebf18c', '罕萨山谷',                'Hunza Valley, Hunza, Pakistan'),
    '孟加拉国':   ('photo-1588103554185-045da246b5ed', '达卡布里甘加河船码头',      'Sadarghat, Buriganga River, Dhaka, Bangladesh'),
    '马尔代夫':   ('photo-1572374800615-17f4eac1202a', '中央环礁岛屿俯瞰',         'Kinbidhoo, Thaa Atoll, Maldives'),
    '不丹':       ('photo-1608377229419-3b5168b6c3da', '帕罗虎穴寺',              "Tiger's Nest (Paro Taktsang), Bhutan"),
    # 中亚 1 国
    '乌兹别克斯坦': ('photo-1664602078796-68ee76b3fc59', '撒马尔罕雷吉斯坦广场',     'Registan Square, Samarkand, Uzbekistan'),

    # —— 第四批 (2026-05 第四轮): 切换到 Pexels 图源 (前缀 'pexels:') ——
    # 北非 2 国 (本轮仅完成切换 + 验证, 剩余 41 个非洲国家留给下轮)
    '阿尔及利亚': ('pexels:2092453',  '撒哈拉沙漠贝尼阿巴斯',     'Béni Abbès, Béchar Province, Algeria - Sahara dunes'),
    '突尼斯':     ('pexels:27599624', '西迪布赛义德蓝白小镇',     'Sidi Bou Said, Tunis Governorate, Tunisia'),
}

# 注：第六轮后未配图国家的 photo ID 需要通过 web_search + 三步元数据验证流程逐一添加,
# 不要靠记忆推测 photo ID（Unsplash ID 是无规律字符串）。
# 已配 48 国全部通过 wsrv.nl 代理走 Cloudflare CDN, 国内可访问。


def get_image_url(country_name: str) -> str:
    """
    根据 photo_id 前缀返回对应的 CDN 直链:
      - Unsplash: 'photo-XXXXXXXX'             → images.unsplash.com/...
      - Pexels:   'pexels:1234567'             → images.pexels.com/photos/...

    所有 URL 通过 wsrv.nl 代理 (Cloudflare CDN, 国内可访问):
      https://wsrv.nl/?url=<URL>&w=1600&h=600&fit=cover
    """
    entry = COUNTRY_IMAGES.get(country_name)
    if not entry:
        return ''
    photo_id = entry[0]

    if photo_id.startswith('pexels:'):
        pid = photo_id.split(':', 1)[1]
        origin = (
            f'images.pexels.com/photos/{pid}/pexels-photo-{pid}.jpeg'
            f'?auto=compress&cs=tinysrgb'
        )
    else:
        # 默认 Unsplash
        origin = (
            f'images.unsplash.com/{photo_id}'
            f'?auto=format&crop=entropy&q=80'
        )

    # 通过 wsrv.nl 代理（Cloudflare CDN，国内可访问）
    # output=jpg 强制返回 JPG，避免 webp 在某些浏览器问题
    # 注意：wsrv.nl 的 url 参数本身需要包含 querystring，
    # 但 wsrv.nl 文档说 url= 后面直接拼接源 URL（含 querystring）即可
    from urllib.parse import quote
    return f'https://wsrv.nl/?url={quote(origin, safe="")}&w=1600&h=600&fit=cover&a=attention&output=jpg'


if __name__ == '__main__':
    print(f'已验证 {len(COUNTRY_IMAGES)} 国')
    for name, (pid, desc, source) in COUNTRY_IMAGES.items():
        src = 'pexels  ' if pid.startswith('pexels:') else 'unsplash'
        print(f'  [{src}] {name:8s} | {desc}')
        print(f'           {url}')
