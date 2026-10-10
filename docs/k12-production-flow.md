# 做一门课后短片

同事部署时，先读这一页，再读 `.cursor/skills/k12-explainer/SKILL.md`，然后读 `docs/decisions.md`。老师把知识点交给模型。模型做到成片。老师只看这一次成片。

受众是哈萨克斯坦的小学生，课后自己看。默认画风是暖色纸、蓝字、金色强调、没有人物。纸色、字色和强调色写在 `assets/library/catalog.json` 的 `style`。公开案例是 `works/cube-volume/cube-volume.mp4`。

## 老师交什么

新建 `works/<slug>/INPUT.md`。里面要有课名、受众、故事大纲、知识点。大纲只写每一段学生要看懂的问题和办法。不写逐句旁白。

缺授课语言，或缺必须使用的例题时，才问老师。其余按这一页做完。

## 云端要自带的东西

云端没有这台 Mac 的家目录，也没有 `~/miniconda3` 和 `~/ai-archive`。

- 配音用你们自己部署的 TTS。流程只要求每句一个 wav，见第 4 步。
- 画风就是目录里的 `style`，再看立方体这一课的成片。不要等另一支没有放进这个仓库的成片。
- 机器上要有 Google Chrome、带 H.264 的 ffmpeg、Node.js 22.12 或更新。`render.mjs` 在编码之前就会找 Chrome，没有 Chrome 连纯编码也起不来。在仓库根目录执行 `npm install`。
- Python 要能导入 `numpy`、`soundfile`、`faster_whisper`。词级对齐第一次运行会下载 faster-whisper small，约 464MB。机器不能联网时，把它放进 `assets/voice/whisper-small/`。
- 这台 Mac 的 ffmpeg 没有 `libx264`，会改用 `h264_videotoolbox`。Linux 上有 `libx264` 就用它。

先跑这一条。失败就先把上面的文件补齐，不要开始写新课。

```bash
python3 scripts/check_lesson.py
```

## 步骤

1. 写入知识点
2. 写大纲
3. 建立素材库
4. 写旁白和分镜
5. 样板接触图
6. 其余场只渲染改动
7. 全量帧只渲染一次
8. 儿童测试
9. 老师终验

第 3 步用带 `--library` 的检查。第 8 步才跑不带 `--library` 的检查。前面几步看这一步写出的文件或接触图。第 8 步之前不要跑完整检查，儿童测试记录还没有，命令会失败。命令失败就停在这一步修，不要问老师。

### 写入知识点

把老师给的原文放进 `works/<slug>/INPUT.md`。不删知识点。

### 写大纲

写 `works/<slug>/outline.md`。先定一条贯穿全片的画面主线。每一段只回答一个问题。上一种办法哪里不行，这一种怎么解决。同屏最多三个要看的东西。此步不写逐句旁白，不画新图。

同时建一个能渲染的空页面。它加载 `assets/lesson/look.js`，里面是暖色纸、蓝字、金色强调、`LOOK.word` 写字、`LOOK.L/E/K` 按录音取时间。场景写在 `scene.js` 的 `LOOK.lesson(课名, t => {...})` 里。用下面的命令起页。不要从人物短片起稿。不要复制某一课自己的 `kit.js` 和检查脚本，它们绑着那一课的路径和秒数。排版不要另发明，已经定下来的写在 `docs/decisions.md`。

```bash
python3 scripts/new_lesson.py <slug>
```

### 建立素材库

打开 `assets/library/catalog.json`。先用库里已有的条目。

库里没有的物件，按目录顶部的 `style` 补一件，追加到目录，再使用。补的是看得清的完整物件。一张钞票就是完整的一张，不裁掉一半。真钞、真币用照片，不把面额画上去。历史物件按本课受众来画。哈萨克斯坦的课，早期纸币用欧美纸币的样子。钞票本身的防伪水印留下。别人打上的网站水印或 SPECIMEN，库里有干净照片就用干净的那张。没有干净照片时，不要把 SPECIMEN 涂掉冒充真钞。`role` 为 `reference` 的条目只供对照，不能进画面。目录里的 `default_audience` 只在老师没写受众时使用。

库里有两种条目。图片条目在场景里用 `files={...}` 或 `PHOTOS = {...}` 加载。`kind` 为 `code` 的条目是一个画图函数，比如 `assets/library/draw/cubes.js` 里的 `cubeStack`。在 `studio.html` 里加载那个文件，在场景里调用 `fn` 写的函数名。新画的代码物件也放进 `assets/library/draw/`，登记到目录，下一课直接用。

`works/<slug>/library.json` 的 `uses` 只写这一课用到的 id。场景里一件库里的东西都没用时，检查会失败。

```bash
python3 scripts/check_lesson.py <slug> --library
```

### 写旁白和分镜

用库里的物件写 `works/<slug>/STORYBOARD.md` 和旁白。点名的东西必须已有 id。不要为了一句新旁白再画一套。不要把旁白交给老师确认。

教学含义以 `INPUT.md` 为准。可以删重复句。删了要在分镜里写原因。

旁白写成 `works/<slug>/narration_ru.json`。每一项有 `id` 和 `text`。听到的词和画面上的句子不同时，加 `spoken`。一段的第一句加 `"chapter": true`。

录音的约定只有一条。每句一个 wav，放在 `works/<slug>/audio/voice/0000.wav`、`0001.wav`……，序号是 `id`。采样率、声道不限。用什么 TTS、什么声音、什么参数，由部署的人定。`scripts/tts_api.py` 把每句 POST 到 `TTS_URL`，请求体是 `{"text", "language"}` 加上 `TTS_BODY` 里的字段，把返回的 wav 存下来。服务的接口不一样，就改这个文件里的 `speak()`。

```bash
TTS_URL=http://<host>/tts python3 scripts/tts_api.py <slug>
python3 scripts/align_ru.py <slug>
python3 scripts/mix_ru.py <slug> --music works/<slug>/audio/music.mp3 --sfx works/<slug>/audio/confirmation_001.ogg@<答案秒数>
```

`align_ru.py` 用 faster-whisper 听每一句，打印 `match`，写出 `timeline.json`、`cues.js` 和 `audio/narration.wav`。`match` 低先看识别出的句子。数字被写成阿拉伯数字是正常的。词听错了（比如两个词连成另一个词）就换说法，删掉那一句的 wav，重新生成。场景里用 `LOOK.K(句号, ['восемь', '8'])` 取关键词时间，两种写法都给。

配乐先下载到 `works/<slug>/audio/music.mp3`，仍用技能里的 Easy Lemon 地址。混音把配乐放在人声下面大约 18 分贝。音效用 Kenney Interface Sounds 里的 `confirmation_001.ogg`，只打在答案出现的那一下。答案秒数取 `timeline.json` 里那个词的 `start`。

### 样板接触图

先做开头一场，渲染接触图。看不清的物件先改库里的那一件，再改场景。样板没看清之前，不跑全量帧。

```bash
node render.mjs --page=works/<slug>/studio.html --sheet=1,3,5 --out=works/<slug>/check/sheet.jpg
```

### 其余场只渲染改动

其余场按 `docs/decisions.md` 的节拍来做。讲完的东西离开，再让下一句的东西进来。只渲染改过的秒数。`--range` 的两个数是秒。

```bash
node render.mjs --page=works/<slug>/studio.html --range=12:20 --frames --workers=4 --frames-dir=out/<slug>/frames
```

### 全量帧只渲染一次

接触图能看清之后，才做全量帧。帧数等于成片秒数乘 24。《立方体的体积》50 秒、1207 帧，在这台 Mac 上 4 个 worker 渲染 33 秒，编码 11 秒。这一步只做一次。只改声音时用 `ffmpeg -c:v copy`，不重渲画面。画面或时长变了，删掉对应帧，再渲染改过的范围。

```bash
node render.mjs --page=works/<slug>/studio.html --frames --workers=4 --frames-dir=out/<slug>/frames
node render.mjs --encode --frames-dir=out/<slug>/frames --audio=works/<slug>/audio/mix.wav --out=works/<slug>/<slug>.mp4
```

渲染细节在 `AGENTS.md`。编码用本机 ffmpeg 实际有的 H.264。

### 儿童测试

没有孩子在场也可以做这一关。对照 `INPUT.md` 的每个知识点，在成片上找一个时间点。小孩要能指着画面说出那个东西。写进 `works/<slug>/.audit/child-comprehension.md`，每个知识点一行。知识点名单放在 `works/<slug>/targets.json`。指不出来就回去改画面，不交给老师。

没有孩子坐在屏幕前时，这一关是模型对着成片把每个知识点指出来，不是小孩已经看懂。抽帧要从编码后的 MP4 抽，不从渲染帧抽。这一步的检查还要求 `outline.md`、`STORYBOARD.md` 和 `<slug>.mp4` 都在。

```bash
python3 scripts/check_lesson.py <slug>
```

### 老师终验

把 `works/<slug>/<slug>.mp4` 交给老师。老师只在这一步看片。老师指出的问题修完后，重新跑儿童测试，再交一次。

## 不要做

- 不要把写完的脚本或文字分镜交回老师。
- 不要先整理工单再开始画画。
- 不要等全部素材变体齐了再做整片。库里够这一课用的就可以拍。
- 不要在已经否掉的初剪上继续补。否掉就按大纲里的主线重做。
- 不要把检查图当成成片已经改好。修完要在编码后的 MP4 上再看那个时间点。
- 不要把案例的句数当成新课的句数。新课的时间以录音为准。

## 最小的完整样例

`works/cube-volume/` 是按这一页从零做出来的一课，可以照着看每一步写出的文件。场景只有一个 `scene.js`。它里面的点乘是那一课老师原文的体积公式，下一支数钱的片子用 `×`，见 `docs/decisions.md`。

## 不在这个仓库里的课

其他已经做过的课留在做课的机器上，不放进这个仓库。下一门课不要中途把旁白交回去等确认，也不要等全部素材变体齐了再拍。节拍以 `docs/decisions.md` 为准。
