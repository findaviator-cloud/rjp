# -*- coding: utf-8 -*-
"""
videos.py  -  6 trial videos ki script (LKG + Class 1)

Har video ke scenes:
  text  : jo AWAAZ mein bolna hai (Balabolka mein yahi paste karna hai)
  subs  : screen par dikhne wale subtitle tukde (SRT mein jaate hain)
  vis   : Blender mein kya dikhega
  pause : bacche ke sochne ke liye chuppi (seconds), awaaz ke baad jodi jaati hai
  wave  : True ho to bhaalu haath hilata hai

Is file ko Notepad mein khol kar text badal sakte hain (UTF-8 mein save karein).
"""

# --- Bacchon ke naam (yahan badal sakte hain) ---
NAME_LKG = "तनिष्का"      # LKG
NAME_C1 = "त्रिशिका"       # Class 1

RED = (0.85, 0.10, 0.10)
YELLOW = (1.00, 0.78, 0.05)
GREEN = (0.15, 0.65, 0.20)
BLUE = (0.10, 0.35, 0.90)
ORANGE = (1.00, 0.45, 0.05)
PINK = (0.95, 0.35, 0.60)

SWAR = [("अ", "anar"), ("आ", "aam"), ("इ", "imli"), ("ई", "eekh"), ("उ", "ullu")]

VIDEOS = {}

# ---------------------------------------------------------------- LKG 1
VIDEOS["lkg1"] = {
    "title": "LKG-1  अ से अनार (स्वर अ आ इ ई उ)",
    "lang": "hi",
    "bg": (0.80, 0.92, 1.00),
    "floor": (0.55, 0.80, 0.45),
    "scenes": [
        {"text": "नमस्ते {T}! नमस्ते बच्चों! मैं हूँ भालू। आओ, आज हम अक्षर सीखें।",
         "subs": ["नमस्ते {T}!", "नमस्ते बच्चों!", "मैं हूँ भालू", "आओ, अक्षर सीखें"],
         "vis": {"row": ["अ", "आ", "इ", "ई", "उ"]}, "wave": True},
        {"text": "अ से अनार। देखो, यह अनार है। अनार लाल है। अ से अनार। अब {T}, तुम बोलो, अ से अनार।",
         "subs": ["अ से अनार", "यह अनार है", "अनार लाल है", "अ से अनार", "{T} बोलो:\nअ से अनार"],
         "vis": {"letter": "अ", "obj": "anar"}},
        {"text": "आ से आम। देखो, यह आम है। आम पीला है। आ से आम। अब {T}, तुम बोलो, आ से आम।",
         "subs": ["आ से आम", "यह आम है", "आम पीला है", "आ से आम", "{T} बोलो:\nआ से आम"],
         "vis": {"letter": "आ", "obj": "aam"}},
        {"text": "इ से इमली। देखो, यह इमली है। इमली खट्टी होती है। इ से इमली। अब {T}, तुम बोलो, इ से इमली।",
         "subs": ["इ से इमली", "यह इमली है", "इमली खट्टी है", "इ से इमली", "{T} बोलो:\nइ से इमली"],
         "vis": {"letter": "इ", "obj": "imli"}},
        {"text": "ई से ईख। ईख यानी गन्ना। गन्ना मीठा होता है। ई से ईख। अब {T}, तुम बोलो, ई से ईख।",
         "subs": ["ई से ईख", "ईख यानी गन्ना", "गन्ना मीठा है", "ई से ईख", "{T} बोलो:\nई से ईख"],
         "vis": {"letter": "ई", "obj": "eekh"}},
        {"text": "उ से उल्लू। देखो, यह उल्लू है। उल्लू रात में जागता है। उ से उल्लू। अब {T}, तुम बोलो, उ से उल्लू।",
         "subs": ["उ से उल्लू", "यह उल्लू है", "उल्लू रात में जागता है", "उ से उल्लू", "{T} बोलो:\nउ से उल्लू"],
         "vis": {"letter": "उ", "obj": "ullu"}},
        {"text": "अ से अनार, आ से आम, इ से इमली, ई से ईख, उ से उल्लू। शाबाश {T}! शाबाश बच्चों! फिर मिलेंगे। टाटा!",
         "subs": ["अ से अनार", "आ से आम", "इ से इमली", "ई से ईख", "उ से उल्लू", "शाबाश {T}!\nटाटा!"],
         "vis": {"recap": SWAR}, "wave": True},
    ],
}

# ---------------------------------------------------------------- LKG 2
def _count_scene(n, word):
    seq = ", ".join(["एक", "दो", "तीन", "चार", "पाँच"][:n])
    if n == 1:
        text = "एक। देखो, एक गेंद। एक गेंद। एक।"
        subs = ["1", "एक गेंद", "1"]
    else:
        text = "%s। देखो, %s गेंद। %s। %s गेंद। %s।" % (word, word, seq, word, word)
        subs = [str(n), "%s गेंद" % word, seq, str(n)]
    return {"text": text, "subs": subs, "vis": {"seq": (1, n), "obj": "ball", "big": True}}

VIDEOS["lkg2"] = {
    "title": "LKG-2  गिनती 1 से 5",
    "lang": "hi",
    "bg": (1.00, 0.93, 0.80),
    "floor": (0.95, 0.70, 0.40),
    "scenes": [
        {"text": "नमस्ते {T}! नमस्ते बच्चों! आज हम गिनती सीखेंगे। एक, दो, तीन, चार, पाँच।",
         "subs": ["नमस्ते {T}!", "नमस्ते बच्चों!", "आज गिनती सीखेंगे", "एक, दो, तीन,\nचार, पाँच"],
         "vis": {"row": ["1", "2", "3", "4", "5"]}, "wave": True},
        _count_scene(1, "एक"),
        _count_scene(2, "दो"),
        _count_scene(3, "तीन"),
        _count_scene(4, "चार"),
        _count_scene(5, "पाँच"),
        {"text": "आओ, सब मिलकर गिनें। एक, दो, तीन, चार, पाँच। शाबाश {T}! शाबाश बच्चों! टाटा!",
         "subs": ["सब मिलकर गिनें", "एक, दो, तीन,\nचार, पाँच", "शाबाश {T}!\nटाटा!"],
         "vis": {"seq": (1, 5), "obj": "ball", "big": True}, "wave": True},
    ],
}

# ---------------------------------------------------------------- LKG 3
VIDEOS["lkg3"] = {
    "title": "LKG-3  रंग पहचानो",
    "lang": "hi",
    "bg": (0.90, 0.85, 1.00),
    "floor": (0.55, 0.75, 0.95),
    "scenes": [
        {"text": "नमस्ते {T}! नमस्ते बच्चों! आज हम रंग पहचानेंगे।",
         "subs": ["नमस्ते {T}!", "नमस्ते बच्चों!", "आज हम रंग पहचानेंगे"],
         "vis": {"balls": [RED, YELLOW, GREEN, BLUE]}, "wave": True},
        {"text": "यह है लाल रंग। अनार लाल होता है। लाल, लाल, लाल। {T}, तुम भी बोलो, लाल।",
         "subs": ["यह है लाल रंग", "अनार लाल होता है", "लाल, लाल, लाल", "{T} बोलो: लाल"],
         "vis": {"colorword": "लाल", "obj": "anar", "color": RED}},
        {"text": "यह है पीला रंग। आम पीला होता है। पीला, पीला, पीला। {T}, तुम भी बोलो, पीला।",
         "subs": ["यह है पीला रंग", "आम पीला होता है", "पीला, पीला, पीला", "{T} बोलो: पीला"],
         "vis": {"colorword": "पीला", "obj": "aam", "color": YELLOW}},
        {"text": "यह है हरा रंग। पत्ता हरा होता है। हरा, हरा, हरा। {T}, तुम भी बोलो, हरा।",
         "subs": ["यह है हरा रंग", "पत्ता हरा होता है", "हरा, हरा, हरा", "{T} बोलो: हरा"],
         "vis": {"colorword": "हरा", "obj": "patta", "color": GREEN}},
        {"text": "यह है नीला रंग। यह गेंद नीली है। नीला, नीला, नीला। {T}, तुम भी बोलो, नीला।",
         "subs": ["यह है नीला रंग", "यह गेंद नीली है", "नीला, नीला, नीला", "{T} बोलो: नीला"],
         "vis": {"colorword": "नीला", "obj": "ball_blue", "color": BLUE}},
        {"text": "बताओ तो {T}, आम किस रंग का होता है?",
         "subs": ["बताओ तो {T}!", "आम किस रंग का है?"],
         "vis": {"only": "aam"}, "pause": 4},
        {"text": "पीला! शाबाश {T}! फिर मिलेंगे। टाटा!",
         "subs": ["पीला!", "शाबाश {T}!\nटाटा!"],
         "vis": {"colorword": "पीला", "obj": "aam", "color": YELLOW}, "wave": True},
    ],
}

# ---------------------------------------------------------------- Class 1  Ginti
VIDEOS["c1_ginti"] = {
    "title": "Class 1 - 1  गिनती 1 से 10",
    "lang": "hi",
    "bg": (0.85, 0.95, 0.85),
    "floor": (0.95, 0.80, 0.50),
    "scenes": [
        {"text": "नमस्ते {R}! नमस्ते बच्चों! आज हम एक से दस तक गिनती सीखेंगे।",
         "subs": ["नमस्ते {R}!", "नमस्ते बच्चों!", "आज हम 1 से 10 तक\nगिनती सीखेंगे"],
         "vis": {"row": [str(i) for i in range(1, 11)]}, "wave": True},
        {"text": "पहले गिनते हैं। एक, दो, तीन।",
         "subs": ["पहले गिनते हैं", "एक, दो, तीन"],
         "vis": {"seq": (1, 3), "obj": "ball", "labels": True}},
        {"text": "अब एक से छह तक गिनते हैं। एक, दो, तीन, चार, पाँच, छह।",
         "subs": ["अब 1 से 6 तक", "एक, दो, तीन,\nचार, पाँच, छह"],
         "vis": {"seq": (1, 6), "obj": "ball", "labels": True}},
        {"text": "और अब एक से दस तक। एक, दो, तीन, चार, पाँच, छह, सात, आठ, नौ, दस।",
         "subs": ["और अब 1 से 10 तक", "एक, दो, तीन, चार, पाँच,", "छह, सात, आठ, नौ, दस"],
         "vis": {"seq": (1, 10), "obj": "ball", "labels": True}},
        {"text": "बताओ तो {R}! एक, दो, खाली, चार, पाँच। कौन सी गिनती छूट गई?",
         "subs": ["बताओ तो {R}!", "1, 2, __, 4, 5", "कौन सी गिनती छूट गई?"],
         "vis": {"quiz": ["1", "2", "?", "4", "5"]}, "pause": 4},
        {"text": "तीन! बिल्कुल सही {R}!",
         "subs": ["तीन!", "बिल्कुल सही {R}!"],
         "vis": {"quiz": ["1", "2", "3", "4", "5"], "hi": 2}},
        {"text": "अब बताओ {R}! सात, आठ, खाली, दस। कौन सी गिनती छूट गई?",
         "subs": ["अब बताओ {R}!", "7, 8, __, 10", "कौन सी गिनती छूट गई?"],
         "vis": {"quiz": ["7", "8", "?", "10"]}, "pause": 4},
        {"text": "नौ! शाबाश {R}! कल फिर मिलेंगे। टाटा!",
         "subs": ["नौ!", "शाबाश {R}!\nटाटा!"],
         "vis": {"quiz": ["7", "8", "9", "10"], "hi": 2}, "wave": True},
    ],
}

# ---------------------------------------------------------------- Class 1  Jodna
VIDEOS["c1_jodna"] = {
    "title": "Class 1 - 2  जोड़ना",
    "lang": "hi",
    "bg": (1.00, 0.90, 0.88),
    "floor": (0.60, 0.80, 0.55),
    "scenes": [
        {"text": "नमस्ते {R}! नमस्ते बच्चों! आज हम जोड़ना सीखेंगे। जोड़ना यानी मिलाना।",
         "subs": ["नमस्ते {R}!", "नमस्ते बच्चों!", "आज हम जोड़ना सीखेंगे", "जोड़ना यानी मिलाना"],
         "vis": {"row": ["1", "+", "2", "=", "3"]}, "wave": True},
        {"text": "एक गेंद और एक गेंद। मिलाकर कितनी हुईं? एक, दो। कुल दो गेंद।",
         "subs": ["1 गेंद और 1 गेंद", "मिलाकर कितनी हुईं?", "एक, दो", "कुल 2 गेंद"],
         "vis": {"sum": (1, 1)}},
        {"text": "दो गेंद और तीन गेंद। मिलाकर कितनी हुईं? एक, दो, तीन, चार, पाँच। कुल पाँच गेंद।",
         "subs": ["2 गेंद और 3 गेंद", "मिलाकर कितनी हुईं?", "एक, दो, तीन, चार, पाँच", "कुल 5 गेंद"],
         "vis": {"sum": (2, 3)}},
        {"text": "चार गेंद और एक गेंद। मिलाकर कुल पाँच गेंद।",
         "subs": ["4 गेंद और 1 गेंद", "मिलाकर कुल 5 गेंद"],
         "vis": {"sum": (4, 1)}},
        {"text": "तीन गेंद और तीन गेंद। मिलाकर कुल छह गेंद।",
         "subs": ["3 गेंद और 3 गेंद", "मिलाकर कुल 6 गेंद"],
         "vis": {"sum": (3, 3)}},
        {"text": "अब तुम बताओ {R}! दो और दो, कितने हुए?",
         "subs": ["अब तुम बताओ {R}!", "2 + 2 = ?"],
         "vis": {"sum": (2, 2), "hide_result": True}, "pause": 4},
        {"text": "चार! शाबाश {R}! कल फिर मिलेंगे। टाटा!",
         "subs": ["चार!", "शाबाश {R}!\nटाटा!"],
         "vis": {"sum": (2, 2)}, "wave": True},
    ],
}

# ---------------------------------------------------------------- Class 1  English
VIDEOS["c1_english"] = {
    "title": "Class 1 - 3  English 3-letter words",
    "lang": "en",
    "bg": (1.00, 0.97, 0.80),
    "floor": (0.60, 0.80, 0.95),
    "scenes": [
        {"text": "Hello Trishika! Hello friends! I am Bear. Today we will learn three letter words.",
         "subs": ["Hello Trishika!\nनमस्ते {R}!", "Hello friends!\nनमस्ते दोस्तों!", "I am Bear.\nमैं भालू हूँ।", "Three letter words\nतीन अक्षर के शब्द"],
         "vis": {"row": ["?", "?", "?"]}, "wave": True},
        {"text": "S, U, N. Sun. S, U, N. Sun. The sun is hot.",
         "subs": ["S - U - N", "Sun\nसूरज", "S - U - N", "Sun\nसूरज", "The sun is hot.\nसूरज गरम है।"],
         "vis": {"word": "SUN", "obj": "sun"}},
        {"text": "E, G, G. Egg. E, G, G. Egg. I eat an egg.",
         "subs": ["E - G - G", "Egg\nअंडा", "E - G - G", "Egg\nअंडा", "I eat an egg.\nमैं अंडा खाता हूँ।"],
         "vis": {"word": "EGG", "obj": "egg"}},
        {"text": "C, U, P. Cup. C, U, P. Cup. I drink milk in a cup.",
         "subs": ["C - U - P", "Cup\nकप", "C - U - P", "Cup\nकप", "I drink milk in a cup.\nमैं कप में दूध पीता हूँ।"],
         "vis": {"word": "CUP", "obj": "cup"}},
        {"text": "H, A, T. Hat. H, A, T. Hat. I wear a hat.",
         "subs": ["H - A - T", "Hat\nटोपी", "H - A - T", "Hat\nटोपी", "I wear a hat.\nमैं टोपी पहनता हूँ।"],
         "vis": {"word": "HAT", "obj": "hat"}},
        {"text": "Quiz time, Trishika! What is this?",
         "subs": ["Quiz time, Trishika!\nसवाल का समय!", "What is this?\nयह क्या है?"],
         "vis": {"only": "cup"}, "pause": 4},
        {"text": "It is a cup! C, U, P. Well done, Trishika! See you tomorrow. Bye bye!",
         "subs": ["It is a cup!\nयह कप है!", "C - U - P", "Well done, Trishika!\nशाबाश {R}!", "Bye bye!\nटाटा!"],
         "vis": {"word": "CUP", "obj": "cup"}, "wave": True},
    ],
}

ORDER = ["lkg1", "lkg2", "lkg3", "c1_ginti", "c1_jodna", "c1_english"]


# {T} = LKG wale bacche ka naam, {R} = Class 1 wale bacche ka naam
for _v in VIDEOS.values():
    for _s in _v["scenes"]:
        _s["text"] = _s["text"].replace("{T}", NAME_LKG).replace("{R}", NAME_C1)
        _s["subs"] = [c.replace("{T}", NAME_LKG).replace("{R}", NAME_C1) for c in _s["subs"]]
