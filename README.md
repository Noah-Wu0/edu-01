# 教育项目 01

教育动画项目 MVP。下一个做课的模型读完下面三页，就可以按同一套做法做出小学生课后自己看的短片。

1. [决定](docs/decisions.md)。做什么、做完是什么样、哪些排版已经否过。
2. [制作过程](docs/k12-production-flow.md)。从老师的知识点到成片的顺序。
3. [用法](docs/usage.md)。怎么加载技能、起一课、看接触图、混音、编码、跑检查。

画面规则在 `.cursor/skills/k12-explainer/SKILL.md`。案例只有 `works/cube-volume/`，是立方体的体积。纸币照片和其他课不在这个仓库里。

```bash
npm install
python3 scripts/check_lesson.py
python3 scripts/check_lesson.py cube-volume
```

引擎沿用一份已有的渲染代码，许可见 `LICENSE`。这个仓库不再带人物角色。
