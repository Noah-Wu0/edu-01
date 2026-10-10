# 用法

做课的模型按这个顺序用。决定和不能再犯的错在 `docs/decisions.md`。步骤的门禁在 `docs/k12-production-flow.md`。画面规则在 `.cursor/skills/k12-explainer/SKILL.md`。

## 加载技能

在 Cursor 里做课之前，读 `.cursor/skills/k12-explainer/SKILL.md`。技能描述里写了科普、课后、面额、算式、素材库。这些词出现时用这份技能，不要另写一套排版。

仓库根目录执行：

```bash
npm install
python3 scripts/check_lesson.py
```

第二条不过，就先补流程或技能里缺的句子，不要开始写新课。机器上要有 Google Chrome、带 H.264 的 ffmpeg、Node.js 22.12 或更新。对齐还要 Python 能导入 `numpy`、`soundfile`、`faster_whisper`。

## 从知识点到成片

1. 老师的原文放进 `works/<slug>/INPUT.md`。不删知识点。
2. 写 `outline.md`。每一段只回答一个问题。此步不写逐句旁白。

```bash
python3 scripts/new_lesson.py <slug>
```

3. 从 `assets/library/catalog.json` 选物件，写入 `works/<slug>/library.json` 的 `uses`。库里没有的，按目录里的 `style` 补完整的一件并登记。

```bash
python3 scripts/check_lesson.py <slug> --library
```

4. 写 `STORYBOARD.md` 和 `narration_ru.json`。每一项有 `id` 和 `text`。用部署方自己的 TTS 把每句存成 `audio/voice/0000.wav`。

```bash
TTS_URL=http://<host>/tts python3 scripts/tts_api.py <slug>
python3 scripts/align_ru.py <slug>
python3 scripts/mix_ru.py <slug> --music works/<slug>/audio/music.mp3 --sfx works/<slug>/audio/confirmation_001.ogg@<答案秒数>
```

哈萨克语对齐时加上 `ALIGN_LANG=kk`。接口和仓库里假设的不一样，就改 `scripts/tts_api.py` 里的 `speak()`。`TTS_BODY` 可以带上 `{"language":"kk"}` 或 `{"language":"ru"}`。

5. 先看接触图。看不清就改，不要跑全量帧。

```bash
node render.mjs --page=works/<slug>/studio.html --sheet=1,3,5 --out=works/<slug>/check/sheet.jpg
node render.mjs --page=works/<slug>/studio.html --stills=2,8 --out=works/<slug>/check/stills
```

6. 改过的秒数才重新渲染。`--frames` 会跳过已经存在的帧。画面或时长变了，先删掉那一段帧。

```bash
node render.mjs --page=works/<slug>/studio.html --range=12:20 --frames --workers=4 --frames-dir=out/<slug>/frames
```

7. 接触图能看清之后，才渲染全量帧并编码。只换音轨时用 `ffmpeg -c:v copy`，不重渲画面。

```bash
node render.mjs --page=works/<slug>/studio.html --frames --workers=4 --frames-dir=out/<slug>/frames
node render.mjs --encode --frames-dir=out/<slug>/frames --audio=works/<slug>/audio/mix.wav --out=works/<slug>/<slug>.mp4
```

8. 对着编码后的 MP4 抽帧，不是对着 `out/<slug>/frames`。每个知识点在 `targets.json` 里有一条，儿童测试 `works/<slug>/.audit/child-comprehension.md` 里要有同样的字，并写上小孩能指着说出的东西。没有孩子在场时，这一关是模型自己指。

```bash
ffmpeg -y -ss 12 -i works/<slug>/<slug>.mp4 -frames:v 1 works/<slug>/check/mp4/t12.jpg
python3 scripts/check_lesson.py <slug>
```

9. 把成片交给老师。老师指出的问题修完后，重新做儿童测试，再交一次。

## 看画面时看什么

接触图回答「这一帧清不清」。编码后的帧回答「成片里是不是这一帧」。只看渲染帧、不看 MP4，会把还没编码的改动当成已经交出去了。

数钱的帧要能同时看见三件事。左边是这一题的钱，纸币不贴着上沿。右边是一条竖着的算式。金色只有最后的得数，它上面有一条短线。

## 案例

照着看 `works/cube-volume/`。它是立方体的体积，文件和命令都走完了上面的顺序。可以抄的和不能抄的写在 `docs/decisions.md` 的最后一节。纸币照片不在这个公开案例里。
