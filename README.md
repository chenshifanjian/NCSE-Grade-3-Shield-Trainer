# NCSE-Grade-3-Shield-Trainer

**中文名：三级御盾锻打**

专为全国计算机（NCRE）三级_信息安全技术考试打造的选择题练习小程序，助你筑牢知识御盾，决胜考场！

## 🌟 特色亮点

  * **高效刷题** ：题目来源于网络，30 秒倒计时。
  * **智能错题记录** ：错题自动存入 `mistakes.txt`，精准定位知识盲区，助力高效复习。
  * **长长记性**：可以在错题的时候记录一些笔记之类的。
  * **暖心鼓励相伴** ：`Encouraging words.txt` 为你注入学习动力，让备考充满信心。

## 🛠️ 项目结构

  * **主程序** ：`quiz_app.py`，驱动整个练习流程。
  * **题库文件** ：`combined_questions_without_numbers.docx`，题目随机排列，选项也随机（选项字母未随机，降低开发难度）。
  * **错题文件** ：`mistakes.txt`，记录错题，方便随时查看。
  * **鼓励话语文件** ：`Encouraging words.txt`，为你提供学习动力。

## 💻 环境搭建

  * Python 环境（推荐 3.6 及以上）
  * 依赖库：`python-docx`（运行 `pip install python-docx` 安装）

## 🚀 快速上手

  1. 克隆项目：

     * `git clone <项目 GitHub 克隆链接>`

  2. 进入项目目录：

     * `cd NCSE-Grade-3-Shield-Trainer`

  3. 安装依赖：

     * `pip install python-docx`

  4. 启动程序：

     * `python quiz_app.py`

## 📚 题库扩充

  1. 打开 `combined_questions_without_numbers.docx`。
  2. 按现有格式（题目、选项、答案）在文末添加新题，保持清晰准确。

## 🤝 贡献指南

  1. 叉（Fork）本项目至你的 GitHub。
  2. 克隆叉仓库，进行修改或开发。
  3. 提交更改并推送到你的 fork 仓库。
  4. 向本项目发起拉取请求（Pull Request），说明贡献内容。

希望这个项目能助你在信息安全技术考试中一臂之力！若使用中有任何问题，欢迎在 Issues 反馈。
