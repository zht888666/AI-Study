import sqlite3
import matplotlib.pyplot as plt


def ai_dictionary_app():
    # 1.连接数据库并确保数据表存在
    conn = sqlite3.connect('englishwords.db')
    cursor = conn.cursor()
    # 创建单词本
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vocab_book (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            word TEXT UNIQUE,
            add_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()

    # 主菜单
    while True:
        print("\n" + "=" * 35)
        print("           智能电子词典 ")
        print("1.  智能查词 (英汉互查与生词添加)")
        print("2.  查看我的生词本")
        print("3.  从生词本删除单词")
        print("4.  导出生词本 (TXT文件)")
        print("5.  学习数据大屏 (每日背词趋势图)")
        print("6.  退出系统")
        print("=" * 35)

        choice = input(" 请输入对应功能的数字 (1-6)：").strip()

        if choice == '1':
            print("\n---  已进入智能查词模式 (输入 0 返回主菜单) ---")
            while True:
                word_input = input('\n请输入要查询的单词或中文：').strip()
                if not word_input:
                    continue
                if word_input == '0':
                    print("返回主菜单...")
                    break

                first_char = word_input[0].lower()
                results = []

                if 'a' <= first_char <= 'z':
                    mode = input("请选择：[1]精确匹配  [2]前缀扩展  [3]同义词联想 -> ").strip()
                    if mode == '1':
                        cursor.execute("SELECT word, pronunciation, meaning FROM englishwords WHERE word=? LIMIT 10;",
                                       (word_input,))
                        results = cursor.fetchall()
                    elif mode == '2':
                        cursor.execute(
                            "SELECT word, pronunciation, meaning FROM englishwords WHERE word LIKE ? LIMIT 10;",
                            (word_input + "%",))
                        results = cursor.fetchall()
                    elif mode == '3':
                        cursor.execute("SELECT meaning FROM englishwords WHERE word=?", (word_input,))
                        res = cursor.fetchone()
                        if res:
                            original_meaning = res[0]
                            clean_meaning = original_meaning
                            for noise in ['n.', 'v.', 'adj.', 'adv.', 'prep.', 'pron.', 'conj.', ' ', '的']:
                                clean_meaning = clean_meaning.replace(noise, '')
                            clean_meaning = clean_meaning.replace('；', ',').replace(';', ',').replace('，', ',')
                            word_list = clean_meaning.split(',')
                            core_word = word_list[0][:2] if (len(word_list) > 0 and word_list[0]) else clean_meaning[:2]

                            cursor.execute(
                                "SELECT word, pronunciation, meaning FROM englishwords WHERE meaning LIKE ? AND word != ? LIMIT 10;",
                                (f"%{core_word}%", word_input))
                            results = cursor.fetchall()
                    else:
                        print(" 模式错误。")
                        continue
                else:
                    cursor.execute(
                        "SELECT word, pronunciation, meaning FROM englishwords WHERE meaning LIKE ? LIMIT 10;",
                        (f"%{word_input}%",))
                    results = cursor.fetchall()

                # 展示查询结果
                if not results:
                    print(" 抱歉，词库里没有找到相关内容。")
                else:
                    print("-" * 40)
                    for row in results:
                        print(f" 单词：{row[0]:<15} 发音：{row[1]}\n 意思：{row[2]}\n" + " - " * 15)
                    print("-" * 40)

                    add_target = input(" 需加入生词本请直接输入单词 (按回车跳过) -> ").strip()
                    if add_target:
                        try:
                            cursor.execute("INSERT INTO vocab_book (word) VALUES (?)", (add_target,))
                            conn.commit()
                            print(f" 成功将 '{add_target}' 收入生词本！")
                        except sqlite3.IntegrityError:
                            print(f"'{add_target}' 已经在生词本里啦")

        elif choice == '2':
            cursor.execute("SELECT word, add_time FROM vocab_book ORDER BY id DESC LIMIT 50;")
            saved_words = cursor.fetchall()
            if not saved_words:
                print("\n 你的生词本目前空空如也。")
            else:
                print("\n" + "=" * 15 + " 我的生词本 " + "=" * 15)
                for w in saved_words:
                    print(f"  {w[0]:<15} (添加于 {w[1][:10]})")
                print("=" * 42)

        elif choice == '3':
            print("\n---  已进入删除模式 ---")
            del_word = input("请输入你要移出生词本的单词 (输入 0 取消)：").strip()
            if del_word and del_word != '0':
                cursor.execute("DELETE FROM vocab_book WHERE word = ?;", (del_word,))
                conn.commit()
                if cursor.rowcount > 0:
                    print(f" 成功将 '{del_word}' 从生词本彻底删除！")
                else:
                    print(f" 生词本里没有找到 '{del_word}' 哦。")

        elif choice == '4':
            print("\n---  准备导出生词本 ---")
            cursor.execute("SELECT word, add_time FROM vocab_book ORDER BY add_time DESC;")
            export_words = cursor.fetchall()
            if not export_words:
                print(" 生词本是空的，无法导出！")
            else:
                try:
                    with open("my_vocab_book.txt", "w", encoding="utf-8") as f:
                        f.write("=== 我的专属 AI 生词本 ===\n")
                        f.write(f"共计收录: {len(export_words)} 个单词\n\n")
                        for w in export_words:
                            f.write(f"单词: {w[0]:<15} | 添加时间: {w[1][:10]}\n")
                    print(" 导出成功！请查看 'my_vocab_book.txt' 文件！")
                except Exception as e:
                    print(f"️ 导出出错：{e}")

        elif choice == '5':
            # 数据可视化大屏 - 每日背词趋势图
            print("\n---  正在生成数据可视化图表 ---")

            # 配置中文字体，防止图表上的中文变成方块乱码
            plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
            plt.rcParams['axes.unicode_minus'] = False

            # 核心 SQL：使用 GROUP BY 按照“日期”进行分组统计
            cursor.execute("""
                SELECT SUBSTR(add_time, 1, 10) as date, COUNT(*) 
                FROM vocab_book 
                GROUP BY date 
                ORDER BY date ASC;
            """)
            data = cursor.fetchall()

            if not data:
                print(" 生词本里还没有数据哦，快去查几个单词再来看趋势图吧！")
            else:
                # 将数据拆包成 x 轴（日期）和 y 轴（数量）两个列表
                dates = [row[0] for row in data]
                counts = [row[1] for row in data]

                # 开始绘制图表
                plt.figure(figsize=(10, 6))  # 设定画布的宽和高

                # 画柱状图，设置颜色和边框
                plt.bar(dates, counts, color='skyblue', edgecolor='royalblue')

                # 设置图表的标题和坐标轴名称
                plt.title('我的每日添词学习趋势', fontsize=16, fontweight='bold')
                plt.xlabel('学习日期', fontsize=12)
                plt.ylabel('新增单词数 (个)', fontsize=12)

                # 在每个柱子头顶打印具体的数字
                for i in range(len(dates)):
                    plt.text(i, counts[i] + 0.1, str(counts[i]), ha='center', va='bottom')

                plt.xticks(rotation=45)  # 日期文字太长，让它们倾斜45度防止重叠
                plt.tight_layout()  # 自动调整排版，防止边缘被裁剪

                print(" 图表生成成功！请在弹出的新窗口中查看。")
                print(" 提示：看完后关闭图表窗口，即可回到主菜单。")
                plt.show()  # 正式把画好的图展示在屏幕上



        elif choice == '6':
            print("\n感谢使用智能电子词典！")
            break

        else:
            print("\n 输入有误，请重新输入 1-6 的数字。")

    cursor.close()
    conn.close()


if __name__ == '__main__':
    ai_dictionary_app()
