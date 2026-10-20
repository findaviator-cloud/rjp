=====================================================================
 BACHCHON KE VIDEOS  -  1 HAFTE KA TRIAL  (LKG + Class 1)
 Bhaalu teacher ke saath 6 chhote 3D videos
=====================================================================

PEHLE YE FOLDER KAHAN RAKHEIN
  Poore folder ko C:\tmp\rjp mein copy karein (Windows Defender ka
  Controlled Folder Access wahan nahi rokta). Folder ke andar
  build_video.py, videos.py, render.bat, img\, lkg1\, lkg2\ ... hone chahiye.

6 VIDEOS (default topics - apni kitaab se match karke badal sakte hain)
  1. lkg1        LKG    अ से अनार (swar अ आ इ ई उ)
  2. lkg2        LKG    Ginti 1 se 5
  3. lkg3        LKG    Rang pehchano (laal, peela, hara, neela)
  4. c1_ginti    Class 1  Ginti 1 se 10 + "kaun si ginti chhoot gayi?"
  5. c1_jodna    Class 1  Jodna (2+3=5 ...) + sawal
  6. c1_english  Class 1  English 3-letter words (SUN, EGG, CUP, HAT)

HAR VIDEO KE 4 KADAM
---------------------------------------------------------------------
KADAM 1 - AWAAZ (Balabolka)  [har video ke 6-8 scene]
  * Balabolka kholein. Tools -> Use Microsoft Online Voices.
  * Hindi videos (lkg1, lkg2, lkg3, c1_ginti, c1_jodna):
        Voice: Microsoft Swara Online (Natural) - Hindi (India)
        Speed (Rate): LKG ke liye -2,  Class 1 ke liye -1
  * c1_english:
        Voice: English (India) wali Neerja ya Prabhat (Online Natural)
        Speed: -1
  * File -> Open -> lkg1\scene01.txt  (ye text pehle se bana hua hai)
  * "Save audio file" dabayein, format WAV, naam scene01.wav, usi folder
    (lkg1\) mein save karein.  Phir scene02.txt -> scene02.wav ... aise
    aakhri scene tak.
  * ZAROORI: ek video ke sabhi scene ek hi voice aur ek hi speed se banayein.
  * Banne ke baad har wav ek baar sun lein. Agar koi shabd galat bol raha
    ho, scene txt mein uski spelling ya viraam (. ,) badal kar dobara banayein.

KADAM 2 - TEST  (3 frame, time naapna)
  * CMD kholein:      cd C:\tmp\rjp
  * Chalayein:        render.bat lkg1 test
  * Aakhir mein likha aayega "Ek frame ka time: X sec -> poore ... ghante".
    3 sample tasveerein lkg1\test\ mein milengi - dekh lein.
  * Pehle ye kar lein, taaki pata chale laptop par kitna time lagega.

KADAM 3 - RENDER  (poora video)
  * Chalayein:        render.bat lkg1
  * Ye khud: awaaz ki lambai napta hai -> frames (12 fps) banata hai ->
    subtitles (.srt) aur full.wav banata hai -> frames render karta hai
    -> aakhir mein  lkg1\lkg1.mp4  (awaaz ke saath) bana deta hai.
  * Beech mein laptop band ho jaye ya CMD band ho jaye to koi baat nahi:
    wahi command dobara chalayein, jo frames ban chuke hain unhein chhod
    kar baaki banata hai.
  * Raat ko saare videos ek saath: render_all.bat


NAYA (v5): SCREEN PAR SUBTITLE AUR BACCHE KA NAAM
  * render.bat / render_all.bat ab har video ki DO mp4 banate hain:
      <video>.mp4        -> subtitle (neeche) aur bacche ke naam ki patti (shuru aur aakhir mein) screen par judi hui. Seedha bacchon ko dikha sakte hain.
      <video>_clean.mp4  -> bina subtitle ke (CapCut mein apne tareeke se subtitle lagane ke liye).
  * Subtitle ki tasveerein img\subs\ mein pehle se bani hain. videos.py ka text ya naam badalne par:
        pip install pillow
        python make_subs.py
  * Subtitle kisi video mein nahi chahiye to:  render.bat lkg1 nosubs
  * Frames dobara nahi banti; sirf mp4 jodne mein 2-4 minute lagte hain.

KADAM 4 - CAPCUT (sirf subtitles aur export)
  * CapCut mein lkg1\lkg1.mp4 import karke timeline par daalein.
    (Awaaz pehle se judi hui hai. 1.80x speed wali jugaad ab nahi chahiye.)
  * Text -> Local captions -> lkg1\lkg1.srt import karein.
  * Subtitle bade aur peele/safed rakhein, neeche. Export.

AGAR DIKKAT AAYE
  * Blender ka rasta alag hai  -> render.bat kholkar BLENDER wali line badlein.
  * Eevee crash / kaala screen -> render.bat lkg1 workbench   (sabse tez,
    thoda saadha look)
  * Jaldi dekhna hai (preview)  -> render.bat lkg1 draft      (aadha size)
  * "scene wav files nahi mili" -> abhi awaaz nahi bani; andaze se chalega.
    Test ke liye theek, asli video ke liye pehle Kadam 1 karein.
  * "ye audio files nahi mili: sceneXX.wav" -> woh wav banayein.
  * "format alag hai" -> sabhi wav ek hi voice/setting se dobara banayein.

BACHCHON KE NAAM
  * LKG videos mein 'तनिष्का' aur Class 1 videos mein 'त्रिशिका' ka naam bolta
    aur likha aata hai (shuru mein, sawal-jawab mein aur shabaashi mein).
  * Naam badalna ho to videos.py ke upar NAME_LKG / NAME_C1 badlein aur
    scene txt dobara banane ke liye make_text.py chalayein (Python chahiye),
    ya mujhe bata dein.

TEXT BADALNA HO
  * videos.py ko Notepad se kholein (UTF-8). "text" = jo bolna hai,
    "subs" = screen par subtitle ke tukde.
  * Bolne ka text lkg1\sceneXX.txt mein bhi badlein (wahi Balabolka mein jata hai).
  * Naya Hindi akshar / ank jodna ho to bata dein, main images bana dunga.

KAUN SI CHEEZ KAISE BANI HAI
  * Bhaalu, anar, aam, imli, ईख, उल्लू, gend, sooraj, ande, cup, topi -
    sab Blender mein simple shapes se bane hain (koi download nahi).
  * Akshar aur ank img\ folder ki tasveerein hain (font: Baloo 2, SIL Open
    Font License). Isliye Hindi ki matra sahi aati hain.
  * Camera sthir hai, 12 fps, 1280x720 - HD 4400 par kam se kam time ke liye.

TRIAL KA PLAN (1 hafta)
  Din 1: lkg1 + c1_ginti        Din 3: lkg2 + c1_jodna
  Din 5: lkg3 + c1_english      Din 6-7: bachchon ko dikhayein, dekhein:
    - kya poora video dekha?   - kya video ke baad bol paaye?
    - kahan bore hue?           - kya pasand aaya (bhaalu, awaaz, subtitle)?
  Mujhe ye batayein, phir main agle videos usi hisaab se banaunga.
=====================================================================
