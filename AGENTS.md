# 教育项目 01

小学生课后自己看的手绘短片。p5 和 p5.brush 画，无头 Chrome 逐帧渲染，ffmpeg 合成 MP4。配音由部署方自己的 TTS 接入。

做下一支课之前，按这个顺序读：

1. `docs/decisions.md`
2. `docs/k12-production-flow.md`
3. `.cursor/skills/k12-explainer/SKILL.md`
4. `docs/usage.md`

## 布局

- `src/core.js`、`src/timeline.js`、`render.mjs` 是共享引擎。不为单独一课改它们。
- `assets/fonts/` 是共享字体，含西里尔字符。页面用相对路径引用。
- `assets/lesson/` 是新课的空页面。`assets/library/` 是素材目录。
- `works/<slug>/` 是一支课。入口是 `studio.html`。场景是 `scene.js`。
- `out/` 是帧序列，可以随时删。

新课用这一条起页，不要从别的课复制：

```bash
python3 scripts/new_lesson.py <slug>
```

## 命令

都在仓库根目录跑。

```bash
node render.mjs --page=works/<slug>/studio.html --sheet=0.5,2,4 --out=works/<slug>/check/sheet.jpg
node render.mjs --page=works/<slug>/studio.html --stills=2,8 --out=works/<slug>/check/stills
node render.mjs --page=works/<slug>/studio.html --frames --workers=4 --frames-dir=out/<slug>/frames
node render.mjs --encode --frames-dir=out/<slug>/frames --audio=works/<slug>/audio/mix.wav --out=works/<slug>/<slug>.mp4
```

本机 ffmpeg 若没有 `libx264`，`render.mjs` 会改用 `h264_videotoolbox`。作品页面里的 `PROJECT.audio` 相对仓库根目录写。

交付前跑 `python3 scripts/check_lesson.py <slug>`。
